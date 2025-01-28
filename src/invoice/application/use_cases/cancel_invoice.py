from dataclasses import dataclass

from src.shared.logging.log import Logger
from src.invoice.domain.repository import ById, InvoiceRepository
from src.invoice.domain.model import Invoice

logger = Logger(__name__)


@dataclass
class Request:
    id: str


class CancelInvoice:
    def __init__(
        self,
        invoices: InvoiceRepository,
    ):
        self.invoices = invoices

    async def execute(self, request: Request) -> Invoice:
        logger.info(f"About to cancel the invoice: invoice={request.id}")

        invoice = await self.invoices.get(query=ById(id=request.id))
        event, invoice = invoice.cancel()

        await self.invoices.update(event)

        return invoice
