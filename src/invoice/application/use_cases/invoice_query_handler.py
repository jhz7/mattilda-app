from src.invoice.domain.repository import (
    AccountStatement,
    InvoiceRepository,
    InvoiceQuery,
    InvoicesQuery,
)
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

    async def account_statement(self, query: InvoicesQuery) -> AccountStatement:
        return await self.invoices.account_statement(query)
