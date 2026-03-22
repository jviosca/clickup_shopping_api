import os
from typing import List

import httpx
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel

CLICKUP_TOKEN = os.getenv("CLICKUP_TOKEN")
CLICKUP_SHOPPING_TASK_ID = os.getenv("CLICKUP_SHOPPING_TASK_ID")
CLICKUP_SHOPPING_CHECKLIST = os.getenv("CLICKUP_SHOPPING_CHECKLIST", "Lista")
CLICKUP_SHOPPING_API_KEY = os.getenv("CLICKUP_SHOPPING_API_KEY")

if not CLICKUP_TOKEN:
    raise RuntimeError("Falta CLICKUP_TOKEN")
if not CLICKUP_SHOPPING_TASK_ID:
    raise RuntimeError("Falta CLICKUP_SHOPPING_TASK_ID")
if not CLICKUP_SHOPPING_API_KEY:
    raise RuntimeError("Falta CLICKUP_SHOPPING_API_KEY")

CLICKUP_BASE = "https://api.clickup.com/api/v2"
CLICKUP_HEADERS = {
    "Authorization": CLICKUP_TOKEN,
    "Content-Type": "application/json",
}

app = FastAPI(title="ClickUp Shopping List API")


class ShoppingListRequest(BaseModel):
    items: List[str]


@app.get("/health")
def health():
    return {"ok": True}


async def get_task(task_id: str) -> dict:
    url = f"{CLICKUP_BASE}/task/{task_id}"
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(url, headers=CLICKUP_HEADERS)
    if resp.status_code >= 400:
        raise HTTPException(status_code=500, detail=f"Error leyendo tarea ClickUp: {resp.text}")
    return resp.json()


async def get_or_create_checklist(task_id: str, checklist_name: str) -> str:
    task = await get_task(task_id)
    for checklist in task.get("checklists", []):
        if checklist.get("name", "").strip().lower() == checklist_name.strip().lower():
            return checklist["id"]

    url = f"{CLICKUP_BASE}/task/{task_id}/checklist"
    payload = {"name": checklist_name}
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(url, headers=CLICKUP_HEADERS, json=payload)

    if resp.status_code >= 400:
        raise HTTPException(status_code=500, detail=f"Error creando checklist: {resp.text}")

    data = resp.json()
    return data["checklist"]["id"] if "checklist" in data else data["id"]


@app.post("/clickup/shopping-list")
async def add_shopping_list(
    req: ShoppingListRequest,
    x_api_key: str = Header(default="")
):
    if x_api_key != CLICKUP_SHOPPING_API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

    cleaned = []
    seen = set()
    for raw in req.items:
        item = raw.strip()
        if not item:
            continue
        key = item.lower()
        if key not in seen:
            seen.add(key)
            cleaned.append(item)

    if not cleaned:
        raise HTTPException(status_code=400, detail="No hay items válidos")

    checklist_id = await get_or_create_checklist(CLICKUP_SHOPPING_TASK_ID, CLICKUP_SHOPPING_CHECKLIST)

    created = []
    errors = []

    async with httpx.AsyncClient(timeout=30) as client:
        for item in cleaned:
            url = f"{CLICKUP_BASE}/checklist/{checklist_id}/checklist_item"
            payload = {"name": item}
            resp = await client.post(url, headers=CLICKUP_HEADERS, json=payload)

            if resp.status_code >= 400:
                errors.append({"item": item, "status": resp.status_code, "body": resp.text})
            else:
                created.append(item)

    return {
        "ok": True,
        "checklist_name": CLICKUP_SHOPPING_CHECKLIST,
        "created_count": len(created),
        "created": created,
        "errors": errors,
    }