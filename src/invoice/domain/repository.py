from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass

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
    async def list(self, query: InvoicesQuery) -> list[Invoice]:
        pass

    @abstractmethod
    async def update(self, event: InvoiceEvent) -> None:
        pass
