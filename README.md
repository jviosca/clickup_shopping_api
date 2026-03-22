# ClickUp Shopping List API

API HTTP en **Python** con [FastAPI](https://fastapi.tiangolo.com/) que recibe una lista de la compra y la vuelca como ítems en un **checklist** de una tarea de [ClickUp](https://clickup.com/), usando la API v2 de ClickUp.

## Qué hace

- **`GET /health`** — Comprueba que el servicio está en marcha.
- **`POST /clickup/shopping-list`** — Recibe un JSON con `items` (textos), deduplica por nombre (sin distinguir mayúsculas), busca o crea un checklist con el nombre configurado en la tarea indicada y añade cada ítem al checklist. Protege el endpoint con el header `x-api-key`.

Documentación interactiva al arrancar el servidor: `http://127.0.0.1:8000/docs`.

## Requisitos

- Python 3.10+ recomendado  
- Token de API de ClickUp y el ID de la tarea donde quieres la lista

## Instalación

```bash
python -m venv .venv
# Windows (cmd): .venv\Scripts\activate.bat
# Windows (PowerShell): .venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Variables de entorno

Obligatorias al arrancar la aplicación:

| Variable | Descripción |
|----------|-------------|
| `CLICKUP_TOKEN` | Token de autorización de ClickUp (cabecera `Authorization` hacia su API). |
| `CLICKUP_SHOPPING_TASK_ID` | ID de la tarea ClickUp donde vive el checklist. |
| `CLICKUP_SHOPPING_API_KEY` | Secreto compartido; el cliente debe enviarlo en el header `x-api-key`. |

Opcional:

| Variable | Descripción |
|----------|-------------|
| `CLICKUP_SHOPPING_CHECKLIST` | Nombre del checklist (por defecto `Lista`). Si no existe, se crea. |

## Ejecución

```bash
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

## Ejemplo de petición

Sustituye la clave por el mismo valor que `CLICKUP_SHOPPING_API_KEY`:

```bash
curl -X POST "http://127.0.0.1:8000/clickup/shopping-list" \
  -H "Content-Type: application/json" \
  -H "x-api-key: TU_CLAVE" \
  -d '{"items": ["leche", "pan", "tomates"]}'
```

En PowerShell puedes usar `Invoke-RestMethod` o `curl.exe` (no el alias `curl`).

## Estructura del repo

- `main.py` — Aplicación FastAPI y llamadas a ClickUp con `httpx`.
- `requirements.txt` — Dependencias del proyecto.
