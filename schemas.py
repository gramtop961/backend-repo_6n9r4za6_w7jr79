"""
Database Schemas for Linqkeun Mini ERP

Each Pydantic model below represents a MongoDB collection (collection name = class name lowercased).
These models power validation for core ERP modules: Sales/CRM, Inventory, Procurement, Finance, HRM,
Projects, and basic Analytics.
"""

from typing import Optional, List, Literal
from datetime import date, datetime
from pydantic import BaseModel, Field, EmailStr

# -------------------------------------------------
# Core - Identity and RBAC
# -------------------------------------------------
class Organization(BaseModel):
    name: str
    country: Optional[str] = "ID"
    currency: str = "IDR"

class Role(BaseModel):
    name: Literal[
        "owner","admin","manager","sales","warehouse","procurement","finance","hr","employee"
    ]
    permissions: List[str] = Field(default_factory=list)

class User(BaseModel):
    full_name: str
    email: EmailStr
    phone: Optional[str] = None
    role: str = "employee"
    is_active: bool = True

# -------------------------------------------------
# Sales & CRM
# -------------------------------------------------
class Customer(BaseModel):
    name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    address: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    source: Optional[str] = Field(default=None, description="lead source")
    assigned_to: Optional[str] = None

class Lead(BaseModel):
    customer_name: str
    contact_email: Optional[EmailStr] = None
    stage: Literal["new","qualified","proposal","won","lost"] = "new"
    value: float = 0
    expected_close: Optional[date] = None

class Opportunity(BaseModel):
    customer_id: Optional[str] = None
    title: str
    stage: Literal["prospecting","qualification","proposal","negotiation","won","lost"] = "prospecting"
    amount: float
    expected_close: Optional[date] = None

class QuotationItem(BaseModel):
    product_id: str
    name: str
    quantity: float = Field(gt=0)
    price: float = Field(ge=0)
    discount: float = 0

class Quotation(BaseModel):
    number: Optional[str] = None
    customer_id: str
    date_issued: date = Field(default_factory=date.today)
    status: Literal["draft","sent","accepted","rejected"] = "draft"
    items: List[QuotationItem]
    notes: Optional[str] = None

class InvoiceItem(BaseModel):
    product_id: str
    name: str
    quantity: float = Field(gt=0)
    price: float = Field(ge=0)
    tax_rate: float = 0.11  # default 11% VAT (PPN)

class Invoice(BaseModel):
    number: Optional[str] = None
    customer_id: str
    date_issued: date = Field(default_factory=date.today)
    due_date: Optional[date] = None
    status: Literal["draft","sent","paid","overdue","cancelled"] = "draft"
    currency: str = "IDR"
    items: List[InvoiceItem]
    notes: Optional[str] = None

class Payment(BaseModel):
    invoice_id: str
    amount: float
    date_paid: date = Field(default_factory=date.today)
    method: Optional[str] = None
    reference: Optional[str] = None

# -------------------------------------------------
# Inventory & Warehouse
# -------------------------------------------------
class Product(BaseModel):
    sku: str
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    uom: str = "pcs"
    price: float = 0.0
    barcode: Optional[str] = None
    track_stock: bool = True

class Warehouse(BaseModel):
    name: str
    code: Optional[str] = None
    address: Optional[str] = None

class StockMovement(BaseModel):
    product_id: str
    warehouse_id: str
    quantity: float
    type: Literal["in","out","transfer"] = "in"
    ref_type: Optional[str] = None  # e.g., SO, PO, ADJ
    ref_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class Supplier(BaseModel):
    name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    rating: Optional[float] = Field(default=None, ge=0, le=5)

# -------------------------------------------------
# Procurement
# -------------------------------------------------
class PurchaseItem(BaseModel):
    product_id: str
    name: str
    quantity: float
    price: float

class PurchaseOrder(BaseModel):
    number: Optional[str] = None
    supplier_id: str
    status: Literal["draft","approved","ordered","received","cancelled"] = "draft"
    items: List[PurchaseItem]
    notes: Optional[str] = None

# -------------------------------------------------
# Finance & Accounting (simplified)
# -------------------------------------------------
class GLAccount(BaseModel):
    code: str
    name: str
    type: Literal["asset","liability","equity","income","expense"]

class JournalLine(BaseModel):
    account_code: str
    debit: float = 0.0
    credit: float = 0.0
    memo: Optional[str] = None

class JournalEntry(BaseModel):
    number: Optional[str] = None
    date: date = Field(default_factory=date.today)
    lines: List[JournalLine]
    memo: Optional[str] = None

# -------------------------------------------------
# HRM
# -------------------------------------------------
class Employee(BaseModel):
    employee_id: str
    name: str
    email: Optional[EmailStr] = None
    position: Optional[str] = None
    salary: float = 0.0

class Attendance(BaseModel):
    employee_id: str
    date: date
    status: Literal["present","absent","leave"] = "present"

class Payroll(BaseModel):
    employee_id: str
    period: str  # e.g., 2025-01
    gross: float
    deductions: float = 0.0
    net: float

# -------------------------------------------------
# Project Management
# -------------------------------------------------
class Project(BaseModel):
    name: str
    description: Optional[str] = None
    owner_id: Optional[str] = None
    status: Literal["active","on_hold","completed","cancelled"] = "active"

class Task(BaseModel):
    project_id: str
    title: str
    description: Optional[str] = None
    assignee_id: Optional[str] = None
    status: Literal["todo","in_progress","done"] = "todo"
    estimated_hours: float = 0
    logged_hours: float = 0

# -------------------------------------------------
# Minimal Analytics (placeholders for AI modules)
# -------------------------------------------------
class ForecastConfig(BaseModel):
    target: Literal["sales","inventory"]
    horizon_days: int = 30
    group_by: Optional[str] = None  # e.g., product_id, customer_id

# Note: The platform will read these schemas from GET /schema endpoint for validation/CRUD tooling.
