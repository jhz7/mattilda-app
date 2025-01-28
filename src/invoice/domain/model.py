from dataclasses import dataclass
from datetime import datetime, date
from decimal import Decimal
from enum import Enum
from src.invoice.domain.errors import (
    PaymentNotFoundError,
    InvoiceInvalidStatusError,
    InvalidPaymentAmountError,
    PaymentInvalidStatusError,
)
from src.invoice.domain.events import (
    InvoiceEvent,
    InvoiceCreated,
    InvoiceCancelled,
    InvoicePaid,
    PaymentAdded,
    PaymentFailed,
    PaymentSucceed,
)


class PaymentStatus(Enum):
    PENDING = "PENDING"
    SUCCEED = "SUCCEED"
    FAILED = "FAILED"


class InvoiceStatus(Enum):
    PAID = "PAID"
    PENDING = "PENDING"
    CANCELED = "CANCELED"


@dataclass(frozen=True)
class Payment:
    id: str
    invoice_id: str
    amount: Decimal
    status: PaymentStatus
    created_at: datetime
    updated_at: datetime
    failed_at: datetime | None = None
    succeed_at: datetime | None = None

    @staticmethod
    def of(
        id: str, invoice_id: str, amount: Decimal, at: datetime = datetime.now()
    ) -> "Payment":
        return Payment(
            id=id,
            invoice_id=invoice_id,
            amount=amount,
            status=PaymentStatus.PENDING,
            created_at=at,
            updated_at=at,
        )

    def succeed(self, at: datetime = datetime.now()) -> "Payment":
        if not self.is_pending():
            raise PaymentInvalidStatusError(
                payment_id=self.id, invoice_id=self.invoice_id
            )

        return Payment(
            id=self.id,
            invoice_id=self.invoice_id,
            amount=self.amount,
            status=PaymentStatus.SUCCEED,
            created_at=self.created_at,
            updated_at=at,
            succeed_at=at,
        )

    def fail(self, at: datetime = datetime.now()) -> "Payment":
        if not self.is_pending():
            raise PaymentInvalidStatusError(
                payment_id=self.id, invoice_id=self.invoice_id
            )

        return Payment(
            id=self.id,
            invoice_id=self.invoice_id,
            amount=self.amount,
            status=PaymentStatus.FAILED,
            created_at=self.created_at,
            updated_at=at,
            failed_at=at,
        )

    def is_pending(self) -> bool:
        return PaymentStatus.PENDING == self.status


@dataclass(frozen=True)
class Invoice:
    id: str
    student_id: str
    school_id: str
    initial_amount: Decimal
    due_amount: Decimal
    due_date: date
    status: InvoiceStatus
    payments: list[Payment]
    created_at: datetime
    updated_at: datetime
    paid_at: datetime | None = None
    cancelled_at: datetime | None = None

    @staticmethod
    def of(
        student_id: str,
        school_id: str,
        amount: Decimal,
        due_date: date,
        at: datetime = datetime.now(),
    ) -> tuple[InvoiceEvent, "Invoice"]:
        invoice = Invoice(
            id=f"school:{school_id}/student:{school_id}/period:{due_date.year}-{due_date.month}",
            school_id=school_id,
            student_id=student_id,
            initial_amount=amount,
            due_amount=amount,
            due_date=due_date,
            status=InvoiceStatus.PENDING,
            payments=[],
            created_at=at,
            updated_at=at,
        )
        event = InvoiceCreated(
            id=invoice.id,
            school_id=school_id,
            student_id=student_id,
            amount=amount,
            due_date=due_date,
            at=at,
        )

        return event, invoice

    def add_payment(
        self, payment_id: str, amount_to_pay: Decimal, at: datetime = datetime.now()
    ) -> tuple[InvoiceEvent, "Invoice"]:
        if not self.is_pending():
            raise InvoiceInvalidStatusError(invoice_id=self.id)

        pending_payments = self.pending_payments()
        pending_payments_amount = sum(list(map(lambda p: p.amount, pending_payments)))

        if amount_to_pay > (self.due_amount - pending_payments_amount):
            raise InvalidPaymentAmountError(invoice_id=self.id, payment_id=payment_id)

        payment = Payment.of(
            id=payment_id, invoice_id=self.id, amount=amount_to_pay, at=at
        )

        invoice = Invoice(
            id=self.id,
            school_id=self.school_id,
            student_id=self.student_id,
            initial_amount=self.initial_amount,
            due_amount=self.due_amount,
            due_date=self.due_date,
            status=self.status,
            payments=self.payments + [payment],
            created_at=self.created_at,
            updated_at=at,
        )
        event = PaymentAdded(
            id=self.id,
            payment=payment,
            at=at,
        )

        return event, invoice

    def succeed_payment(
        self, payment_id: str, at: datetime = datetime.now()
    ) -> tuple[list[InvoiceEvent], "Invoice"]:
        if not self.is_pending():
            raise InvoiceInvalidStatusError(invoice_id=self.id)

        payment = next(filter(lambda p: p.id == payment_id, self.payments), None)

        if not payment:
            raise PaymentNotFoundError(invoice_id=self.id, payment_id=payment_id)

        succeeded_payment = payment.succeed(at=at)
        updated_payments = self.__replace_payment(succeeded_payment)

        due_amount = self.due_amount - payment.amount

        if due_amount <= 0:
            invoice = Invoice(
                id=self.id,
                school_id=self.school_id,
                student_id=self.student_id,
                initial_amount=self.initial_amount,
                due_amount=Decimal(0),
                due_date=self.due_date,
                status=InvoiceStatus.PAID,
                payments=updated_payments,
                created_at=self.created_at,
                updated_at=at,
                paid_at=at,
            )
            events = [
                PaymentSucceed(
                    id=self.id,
                    due_amount=Decimal(0),
                    payment=succeeded_payment,
                    at=at,
                ),
                InvoicePaid(
                    id=self.id,
                    at=at,
                ),
            ]

            return events, invoice

        invoice = Invoice(
            id=self.id,
            school_id=self.school_id,
            student_id=self.student_id,
            initial_amount=self.initial_amount,
            due_amount=due_amount,
            due_date=self.due_date,
            status=self.status,
            payments=updated_payments,
            created_at=self.created_at,
            updated_at=at,
        )
        event = PaymentSucceed(
            id=self.id,
            due_amount=due_amount,
            payment=succeeded_payment,
            at=at,
        )

        return [event], invoice

    def fail_payment(
        self, payment_id: str, at: datetime = datetime.now()
    ) -> tuple[InvoiceEvent, "Invoice"]:
        payment = next(filter(lambda p: p.id == payment_id, self.payments), None)

        if not payment:
            raise PaymentNotFoundError(invoice_id=self.id, payment_id=payment_id)

        failed_payment = payment.fail(at=at)
        updated_payments = self.__replace_payment(failed_payment)

        invoice = Invoice(
            id=self.id,
            school_id=self.school_id,
            student_id=self.student_id,
            initial_amount=self.initial_amount,
            due_amount=self.due_amount,
            due_date=self.due_date,
            status=self.status,
            payments=updated_payments,
            created_at=self.created_at,
            updated_at=at,
        )
        event = PaymentFailed(
            id=self.id,
            payment_id=payment_id,
            at=at,
        )

        return event, invoice

    def cancel(self, at: datetime = datetime.now()) -> tuple[InvoiceEvent, "Invoice"]:
        if not self.is_pending():
            raise InvoiceInvalidStatusError(invoice_id=self.id)

        invoice = Invoice(
            id=self.id,
            school_id=self.school_id,
            student_id=self.student_id,
            initial_amount=self.initial_amount,
            due_amount=self.due_amount,
            due_date=self.due_date,
            status=InvoiceStatus.CANCELED,
            created_at=self.created_at,
            updated_at=at,
            cancelled_at=at,
        )
        event = InvoiceCancelled(
            id=self.id,
            at=at,
        )

        return event, invoice

    def is_pending(self) -> bool:
        return InvoiceStatus.PENDING == self.status

    def pending_payments(self) -> list[Payment]:
        return list(filter(lambda p: p.is_pending(), self.payments))

    def __replace_payment(self, payment: Payment) -> list[Payment]:
        return [
            current_payment if current_payment.id != payment.id else payment
            for current_payment in self.payments
        ]
