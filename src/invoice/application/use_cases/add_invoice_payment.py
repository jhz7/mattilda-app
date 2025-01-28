from dataclasses import asdict, dataclass
from decimal import Decimal

from src.shared.id.generator import IdGenerator
from src.shared.logging.log import Logger
from src.invoice.domain.repository import ById, InvoiceRepository
from src.invoice.domain.model import Invoice

logger = Logger(__name__)


@dataclass
class Request:
    id: str
    amount: Decimal


class AddInvoicePayment:
    def __init__(
        self,
        invoices: InvoiceRepository,
        id_generator: IdGenerator,
    ):
        self.invoices = invoices
        self.id_generator = id_generator

    async def execute(self, request: Request) -> Invoice:
        logger.info(f"About to add an invoice payment: request={asdict(request)}")

        invoice = await self.invoices.get(query=ById(id=request.id))

        payment_id = await self.id_generator.generate()
        event, invoice = invoice.add_payment(
            payment_id=payment_id, amount_to_pay=request.amount
        )

        await self.invoices.update(event)

        return invoice
