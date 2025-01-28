from abc import ABC
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal


class InvoiceEvent(ABC):
    id: str
    at: datetime


@dataclass(frozen=True)
class InvoiceCreated(InvoiceEvent):
    id: str
    school_id: str
    student_id: str
    amount: Decimal
    due_date: date
    at: datetime


@dataclass(frozen=True)
class InvoicePaid(InvoiceEvent):
    id: str
    at: datetime


@dataclass(frozen=True)
class InvoiceCancelled(InvoiceEvent):
    id: str
    at: datetime
