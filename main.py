import os
from datetime import datetime
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from database import db, create_document, get_documents

app = FastAPI(title="Linqkeun Mini ERP API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"name": "Linqkeun Mini ERP API", "status": "ok"}


@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:20]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:80]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:80]}"

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
    return response


# -----------------------------
# Schemas exposure for tooling
# -----------------------------
from fastapi.responses import JSONResponse

def pydantic_models_to_schema():
    # Dynamically read models from schemas.py for low-code CRUD tooling
    import importlib
    module = importlib.import_module("schemas")
    models = {}
    for name, obj in module.__dict__.items():
        try:
            if isinstance(obj, type) and issubclass(obj, BaseModel) and name not in ("BaseModel",):
                models[name] = obj.model_json_schema()
        except Exception:
            continue
    return models

@app.get("/schema")
def get_schema():
    return JSONResponse(pydantic_models_to_schema())


# -----------------------------
# Minimal API routes to demo modules
# -----------------------------
class CreateCustomer(BaseModel):
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None

@app.post("/customers")
def create_customer(payload: CreateCustomer):
    customer = payload.model_dump()
    customer["created_at"] = datetime.utcnow()
    cid = create_document("customer", customer)
    return {"id": cid, **customer}

@app.get("/customers")
def list_customers(limit: int = 50):
    docs = get_documents("customer", {}, limit=limit)
    # Convert ObjectId to string
    for d in docs:
        d["_id"] = str(d.get("_id"))
    return docs

class CreateProduct(BaseModel):
    sku: str
    name: str
    price: float

@app.post("/products")
def create_product(payload: CreateProduct):
    data = payload.model_dump()
    data["created_at"] = datetime.utcnow()
    pid = create_document("product", data)
    return {"id": pid, **data}

@app.get("/products")
def list_products(limit: int = 100):
    docs = get_documents("product", {}, limit=limit)
    for d in docs:
        d["_id"] = str(d.get("_id"))
    return docs


# Simple invoices
class InvoiceItem(BaseModel):
    product_id: str
    name: str
    quantity: float
    price: float
    tax_rate: float = 0.11

class CreateInvoice(BaseModel):
    customer_id: str
    items: List[InvoiceItem]
    currency: str = "IDR"

@app.post("/invoices")
def create_invoice(payload: CreateInvoice):
    inv = payload.model_dump()
    inv["status"] = "draft"
    inv["created_at"] = datetime.utcnow()
    total = sum(i["quantity"]*i["price"]*(1+i.get("tax_rate",0)) for i in inv["items"])
    inv["total"] = round(total, 2)
    inv_id = create_document("invoice", inv)
    return {"id": inv_id, **inv}

@app.get("/invoices")
def list_invoices(limit: int = 50):
    docs = get_documents("invoice", {}, limit=limit)
    for d in docs:
        d["_id"] = str(d.get("_id"))
    return docs


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
