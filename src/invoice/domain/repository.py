from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass
from datetime import datetime
from decimal import Decimal

from src.invoice.domain.events import InvoiceEvent
from src.invoice.domain.model import Invoice
from src.shared.errors.application import NotFoundError


class InvoiceQuery(ABC):
    pass


@dataclass
class ById(InvoiceQuery):
    id: str


class InvoicesQuery(ABC):
    pass


@dataclass
class BySchoolId(InvoicesQuery):
    school_id: str


@dataclass
class ByStudentId(InvoicesQuery):
    student_id: str


@dataclass
class All(InvoicesQuery):
    token: str


@dataclass
class PendingInvoiceReadProjection:
    id: str
    student_id: str
    school_id: str
    base_amount: Decimal
    due_amount: Decimal
    created_at: datetime
    updated_at: datetime


@dataclass
class AccountStatement:
    due_amount: Decimal
    invoices: list[PendingInvoiceReadProjection]

    @staticmethod
    def of(invoices: list[PendingInvoiceReadProjection]) -> "AccountStatement":
        due_amount = sum(invoice.due_amount for invoice in invoices)

        return AccountStatement(due_amount=due_amount, invoices=invoices)


class InvoiceRepository(ABC):
    async def get(self, query: InvoiceQuery) -> Invoice:
        found_invoice = await self.find(query)

        if found_invoice is None:
            raise NotFoundError(resource="Invoice", attributes=asdict(query))

        return found_invoice

    @abstractmethod
    async def exists(self, query: InvoiceQuery) -> bool:
        pass

    @abstractmethod
    async def find(self, query: InvoiceQuery) -> Invoice | None:
        pass

    @abstractmethod
    async def account_statement(self, query: InvoicesQuery) -> AccountStatement:
        pass

    @abstractmethod
    async def update(self, event: InvoiceEvent) -> None:
        pass
