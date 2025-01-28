from src.invoice.domain.repository import InvoiceRepository, InvoiceQuery, InvoicesQuery
from src.invoice.domain.model import Invoice


class InvoiceQueryHandler:
    def __init__(self, invoices: InvoiceRepository):
        self.invoices = invoices

    async def get(self, query: InvoiceQuery) -> Invoice:
        return await self.invoices.get(query=query)

    async def find(self, query: InvoiceQuery) -> Invoice | None:
        return await self.invoices.find(query=query)

    async def list(self, query: InvoicesQuery) -> list[Invoice]:
        return await self.invoices.list(query)
