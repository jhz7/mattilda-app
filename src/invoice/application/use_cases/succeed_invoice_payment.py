from dataclasses import dataclass

from src.shared.logging.log import Logger
from src.invoice.domain.repository import ById, InvoiceRepository
from src.invoice.domain.model import Invoice

logger = Logger(__name__)


@dataclass
class Request:
    id: str
    payment_id: str


class SucceedInvoicePayment:
    def __init__(
        self,
        invoices: InvoiceRepository,
    ):
        self.invoices = invoices

    async def execute(self, request: Request) -> Invoice:
        logger.info(
            f"About to mark as succeed an invoice payment: invoice={request.id}"
        )

        invoice = await self.invoices.get(query=ById(id=request.id))
        events, invoice = invoice.succeed_payment(payment_id=request.payment_id)

        for event in events:
            await self.invoices.update(event)

        return invoice
