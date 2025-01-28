from dataclasses import asdict
from fastapi import Depends
from sqlalchemy import select, exists, update
from sqlalchemy.ext.asyncio import AsyncSession
from src.invoice.domain.events import (
    InvoiceEvent,
    InvoiceCancelled,
    InvoiceCreated,
    InvoicePaid,
)
from src.shared.db.pg_sqlalchemy.connection import get_db
from src.shared.logging.log import Logger
from src.shared.errors.technical import TechnicalError
from src.invoice.domain.repository import (
    ById,
    BySchoolId,
    ByStudentId,
    Invoice,
    InvoiceRepository,
    InvoicesQuery,
    InvoiceQuery,
)
from src.invoice.infrastructure.persistence.sqlalchemy.dbo import (
    InvoiceDbo,
    PaymentDbo,
)
from src.invoice.domain.model import (
    InvoiceStatus,
    PaymentAdded,
    PaymentFailed,
    PaymentStatus,
    PaymentSucceed,
)

logger = Logger(__name__)


class SqlAlchemyInvoiceRepository(InvoiceRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def exists(self, query: InvoiceQuery) -> bool:
        try:
            statement = select(exists().where(self.__parse_single_query(query)))
            result = await self.session.execute(statement)

            return result.scalar() or False
        except Exception as e:
            error = TechnicalError(
                code="InvoiceRepositoryError",
                message=f"Fail checking invoice existing query={(str(query))}",
                attributes=asdict(query),
                cause=e,
            )

            logger.error(error)

            raise error from e

    async def find(self, query: InvoiceQuery) -> Invoice | None:
        try:
            db_query = select(InvoiceDbo).where(self.__parse_single_query(query))
            result = await self.session.execute(db_query)
            result = result.scalar()

            if result is None:
                return None

            return result.as_domain()
        except Exception as e:
            error = TechnicalError(
                code="InvoiceRepositoryError",
                message=f"Fail finding invoice query={(str(query))}",
                attributes=asdict(query),
                cause=e,
            )

            logger.error(error)

            raise error from e

    async def list(self, query: InvoicesQuery) -> list[Invoice]:
        try:
            result = await self.session.execute(
                select(InvoiceDbo).where(self.__parse_multiple_query(query))
            )
            result = result.scalars().all()

            return list(map(lambda dbo: dbo.as_domain(), result))
        except Exception as e:
            error = TechnicalError(
                code="InvoiceRepositoryError",
                message=f"Fail listing invoices query={(str(query))}",
                attributes=asdict(query),
                cause=e,
            )

            logger.error(error)

            raise error from e

    async def update(self, event: InvoiceEvent) -> None:
        try:
            match event:
                case InvoiceCreated():
                    dbo = InvoiceDbo.of(event)
                    self.session.add(dbo)

                case InvoicePaid():
                    statement = (
                        update(InvoiceDbo)
                        .where(InvoiceDbo.id == event.id)
                        .values(
                            status=InvoiceStatus.PAID.name,
                            paid_at=event.at,
                            updated_at=event.at,
                        )
                    )
                    await self.session.execute(statement)

                case InvoiceCancelled():
                    statement = (
                        update(InvoiceDbo)
                        .where(InvoiceDbo.id == event.id)
                        .values(
                            status=InvoiceStatus.CANCELED.name,
                            cancelled_at=event.at,
                            updated_at=event.at,
                        )
                    )
                    await self.session.execute(statement)

                case PaymentAdded():
                    payment_dbo = PaymentDbo.of(event)
                    self.session.add(payment_dbo)

                case PaymentSucceed():
                    invoice_statement = (
                        update(InvoiceDbo)
                        .where(InvoiceDbo.id == event.id)
                        .values(due_amount=event.due_amount, updated_at=event.at)
                    )
                    payment_statement = (
                        update(PaymentDbo)
                        .where(PaymentDbo.id == event.payment.id)
                        .values(
                            status=PaymentStatus.SUCCEED.name,
                            succeed_at=event.at,
                            updated_at=event.at,
                        )
                    )
                    await self.session.execute(invoice_statement)
                    await self.session.execute(payment_statement)

                case PaymentFailed():
                    statement = (
                        update(PaymentDbo)
                        .where(PaymentDbo.id == event.payment_id)
                        .values(
                            status=PaymentStatus.FAILED.name,
                            failed_at=event.at,
                            updated_at=event.at,
                        )
                    )
                    await self.session.execute(statement)

                case _:
                    raise ValueError(f"Unknown InvoiceEvent type: {event}")

            await self.session.commit()
        except Exception as e:
            error = TechnicalError(
                code="InvoiceRepositoryError",
                message=f"Fail updating invoice ",
                attributes=asdict(event),
                cause=e,
            )

            logger.error(error)

            raise error from e

    def __parse_single_query(self, query: InvoiceQuery):
        match query:
            case ById(id):
                return InvoiceDbo.id == id
            case _:
                raise NotImplementedError("Query not implemented")

    def __parse_multiple_query(self, query: InvoicesQuery):
        match query:
            case BySchoolId(student_id):
                return InvoiceDbo.school_id == student_id
            case ByStudentId(student_id):
                return InvoiceDbo.student_id == student_id
            case _:
                raise NotImplementedError("Query not implemented")


def get_invoice_repository(
    session: AsyncSession = Depends(get_db),
) -> InvoiceRepository:
    return SqlAlchemyInvoiceRepository(session=session)
