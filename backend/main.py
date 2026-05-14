from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from fastapi.middleware.cors import CORSMiddleware
from routes import upload, chat, interactions
import os, json

app = FastAPI(title="Medical Interaction Assistant")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router)
app.include_router(chat.router)
app.include_router(interactions.router)

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Medical Interaction Assistant",
        version="1.0.0",
        routes=app.routes,
    )
    # Fix Swagger UI bug for List[UploadFile] rendering as array of strings
    schemas = openapi_schema.get("components", {}).get("schemas", {})
    for schema_name, schema in schemas.items():
        if "properties" in schema:
            for prop_name, prop_val in schema["properties"].items():
                if prop_val.get("type") == "array":
                    items = prop_val.get("items", {})
                    if items.get("type") == "string" and items.get("contentMediaType") == "application/octet-stream":
                        items["format"] = "binary"

    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

STORAGE_DIR = "storage"
os.makedirs(STORAGE_DIR, exist_ok=True)

if not os.path.exists(f"{STORAGE_DIR}/medical_memory.json"):
    with open(f"{STORAGE_DIR}/medical_memory.json", "w") as f:
        json.dump({"medications": [], "conditions": [], "allergies": []}, f)

if not os.path.exists(f"{STORAGE_DIR}/chat_memory.json"):
    with open(f"{STORAGE_DIR}/chat_memory.json", "w") as f:
        json.dump([], f)
