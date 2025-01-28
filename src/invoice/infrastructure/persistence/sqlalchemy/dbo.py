from datetime import date, datetime
from decimal import Decimal
from sqlalchemy import (
    DECIMAL,
    Date,
    DateTime,
    ForeignKey,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from invoice.domain.events import InvoiceCreated
from src.invoice.domain.model import InvoiceStatus, PaymentAdded, PaymentStatus
from src.shared.db.pg_sqlalchemy.connection import BaseSqlModel


class PaymentDbo(BaseSqlModel):
    __tablename__ = "payments"

    id: Mapped[str] = mapped_column(String, primary_key=True)

    invoice_id: Mapped[str] = mapped_column(ForeignKey("invoices.id"))
    amount: Mapped[Decimal] = mapped_column(DECIMAL(10, 2), nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False)
    failed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    succeed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    def __repr__(self):
        return f"<PaymentDbo(id={self.id}, amount={self.amount}, status={self.status})>"

    @staticmethod
    def of(event: PaymentAdded) -> "InvoiceDbo":
        return PaymentDbo(
            id=event.payment.id,
            invoice_id=event.id,
            amount=event.payment.amount,
            status=PaymentStatus.PENDING.name,
            created_at=event.payment.created_at,
            updated_at=event.payment.updated_at,
        )


class InvoiceDbo(BaseSqlModel):
    __tablename__ = "invoices"

    id: Mapped[str] = mapped_column(String, primary_key=True)

    student_id: Mapped[str] = mapped_column(ForeignKey("students.id"))
    school_id: Mapped[str] = mapped_column(ForeignKey("schools.id"))
    initial_amount: Mapped[Decimal] = mapped_column(DECIMAL(10, 2), nullable=False)
    due_amount: Mapped[Decimal] = mapped_column(DECIMAL(10, 2), nullable=False)
    due_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False)
    paid_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    payments: Mapped[list[PaymentDbo]] = relationship(
        "PaymentDbo", backref="invoice", lazy="joined"
    )

    def __repr__(self):
        return f"<InvoiceDbo(id={self.id}, status={self.status}, due_amount={self.due_amount})>"

    @staticmethod
    def of(event: InvoiceCreated) -> "InvoiceDbo":
        return InvoiceDbo(
            id=event.id,
            school_id=event.school_id,
            student_id=event.student_id,
            initial_amount=event.amount,
            due_amount=event.amount,
            due_date=event.due_date,
            status=InvoiceStatus.PENDING.name,
            created_at=event.at,
            updated_at=event.at,
        )
