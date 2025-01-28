from datetime import date
from decimal import Decimal
from pydantic import BaseModel

from src.invoice.application.use_cases.create_invoice import (
    Request as CreateInvoiceRequest,
)
from src.invoice.application.use_cases.add_invoice_payment import (
    Request as AddInvoicePaymentRequest,
)


class CreateInvoiceDto(BaseModel):
    school_id: str
    student_id: str
    amount: Decimal
    due_date: date

    def as_create_invoice_request(self) -> CreateInvoiceRequest:
        return CreateInvoiceRequest(
            school_id=self.school_id,
            student_id=self.student_id,
            amount=self.amount,
            due_date=self.due_date,
        )


class AddInvoicePaymentDto(BaseModel):
    amount: Decimal

    def as_add_invoice_payment_request(self, invoice_id: str) -> AddInvoicePaymentRequest:
        return AddInvoicePaymentRequest(
            id=invoice_id,
            amount=self.amount,
        )
