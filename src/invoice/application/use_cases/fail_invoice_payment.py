from dataclasses import dataclass

from src.shared.logging.log import Logger
from src.invoice.domain.repository import ById, InvoiceRepository
from src.invoice.domain.model import Invoice

logger = Logger(__name__)


@dataclass
class Request:
    id: str
    payment_id: str


class FailInvoicePayment:
    def __init__(
        self,
        invoices: InvoiceRepository,
    ):
        self.invoices = invoices

    async def execute(self, request: Request) -> Invoice:
        logger.info(f"About to mark as failed an invoice payment: invoice={request.id}")

        invoice = await self.invoices.get(query=ById(id=request.id))
        event, invoice = invoice.fail_payment(payment_id=request.payment_id)

        await self.invoices.update(event)

        return invoice
