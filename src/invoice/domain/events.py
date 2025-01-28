from abc import ABC
from datetime import date, datetime
from decimal import Decimal

from src.invoice.domain.model import Payment


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


class PaymentAdded(InvoiceEvent):
    id: str
    payment: Payment
    at: datetime


class PaymentSucceed(InvoiceEvent):
    id: str
    due_amount: Decimal
    payment: Payment
    at: datetime


class PaymentFailed(InvoiceEvent):
    id: str
    payment_id: str
    at: datetime
