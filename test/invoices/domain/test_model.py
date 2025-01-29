from datetime import date, datetime
from decimal import Decimal

import pytest
from src.shared.errors.business import BusinessError
from src.invoice.domain.events import InvoiceCreated
from src.invoice.domain.model import (
    Invoice,
    InvoiceStatus,
    Payment,
    PaymentAdded,
    PaymentStatus,
)


class TestCreateInvoice:
    def test_create_invoice(self):
        student_id = "1"
        school_id = "2"
        amount = Decimal("100.00")
        due_date = date.today()
        now = datetime.now()

        expected_invoice_id = f"school:{school_id}|student:{student_id}|period:{due_date.year}-{due_date.month}"
        expected_invoice = Invoice(
            id=expected_invoice_id,
            student_id=student_id,
            school_id=school_id,
            initial_amount=amount,
            due_amount=amount,
            due_date=due_date,
            status=InvoiceStatus.PENDING,
            payments=[],
            created_at=now,
            updated_at=now,
        )
        expected_event = InvoiceCreated(
            id=expected_invoice_id,
            school_id=school_id,
            student_id=student_id,
            amount=amount,
            due_date=due_date,
            at=now,
        )

        event, invoice = Invoice.of(
            student_id=student_id,
            school_id=school_id,
            amount=amount,
            due_date=due_date,
            at=now,
        )

        assert invoice == expected_invoice
        assert event == expected_event


class TestAddPaymentToInvoice:
    def test_fail_when_is_not_pending(self):
        student_id = "1"
        school_id = "2"
        amount = Decimal("100.00")
        due_date = date.today()
        now = datetime.now()

        cancelled_invoice = Invoice(
            id=f"school:{school_id}|student:{student_id}|period:{due_date.year}-{due_date.month}",
            student_id=student_id,
            school_id=school_id,
            initial_amount=amount,
            due_amount=amount,
            due_date=due_date,
            status=InvoiceStatus.CANCELED,
            payments=[],
            created_at=now,
            updated_at=now,
            cancelled_at=now,
        )

        with pytest.raises(BusinessError) as exc:
            cancelled_invoice.add_payment(
                payment_id="1", amount_to_pay=Decimal("50.00")
            )

        assert str(exc.value.code) == "InvoiceInvalidStatusError"

    def test_fail_when_the_amount_to_pay_surpass_invoice_due_amount(self):
        student_id = "1"
        school_id = "2"
        amount = Decimal("100.00")
        due_date = date.today()
        now = datetime.now()

        _, pending_invoice = Invoice.of(
            student_id=student_id,
            school_id=school_id,
            amount=amount,
            due_date=due_date,
            at=now,
        )

        with pytest.raises(BusinessError) as exc:
            pending_invoice.add_payment(payment_id="1", amount_to_pay=Decimal("150.00"))

        assert str(exc.value.code) == "InvalidPaymentAmountError"

    def test_succeed(self):
        student_id = "1"
        school_id = "2"
        amount = Decimal("100.00")
        due_date = date.today()
        now = datetime.now()

        _, pending_invoice = Invoice.of(
            student_id=student_id,
            school_id=school_id,
            amount=amount,
            due_date=due_date,
            at=now,
        )

        amount_to_pay = Decimal("50.00")
        executed_at = datetime.now()
        expected_added_payment = Payment(
            id="1",
            invoice_id=pending_invoice.id,
            amount=amount_to_pay,
            status=PaymentStatus.PENDING,
            created_at=executed_at,
            updated_at=executed_at,
            failed_at=None,
            succeed_at=None,
        )
        expected_event = PaymentAdded(
            id=pending_invoice.id,
            payment=expected_added_payment,
            at=executed_at,
        )

        event, updated_invoice = pending_invoice.add_payment(
            payment_id="1", amount_to_pay=amount_to_pay, at=executed_at
        )

        assert updated_invoice.payments == [expected_added_payment]
        assert updated_invoice.updated_at == executed_at
        assert event == expected_event
