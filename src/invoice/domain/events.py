from abc import ABC
from datetime import date, datetime
from decimal import Decimal


class InvoiceEvent(ABC):
    id: str
    at: datetime


class InvoiceCreated(InvoiceEvent):
    id: str
    school_id: str
    student_id: str
    amount: Decimal
    due_date: date
    at: datetime


class InvoicePaid(InvoiceEvent):
    id: str
    at: datetime


class InvoiceCancelled(InvoiceEvent):
    id: str
    at: datetime
