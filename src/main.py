import asyncio
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from src.school.infrastructure.api.events.drop_student_enrollments_subscriber import (
    dropStudentEnrollmentsSubscriber,
)
from src.shared.errors.business import BusinessError
from src.shared.errors.application import ApplicationError
from src.shared.errors.technical import TechnicalError
from src.student.infrastructure.api.http.route import router as student_router
from src.school.infrastructure.api.http.route import router as school_router
from src.invoice.infrastructure.api.http.route import router as invoice_router

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    subscriber = await dropStudentEnrollmentsSubscriber()

    dropStudentEnrollmentsTask = asyncio.create_task(subscriber.run())
    yield
    dropStudentEnrollmentsTask.cancel()


app = FastAPI(lifespan=lifespan)


@app.exception_handler(Exception)
async def exception_handler(request: Request, error: Exception):
    return JSONResponse(
        status_code=500,
        content={"message": "Internal server error"},
    )


@app.exception_handler(Exception)
async def exception_handler(request: Request, error: TechnicalError):
    return JSONResponse(
        status_code=500,
        content={
            "code": error.code,
            "message": error.message,
            "attributes": error.attributes,
        },
    )


@app.exception_handler(Exception)
async def exception_handler(request: Request, error: ApplicationError):
    return JSONResponse(
        status_code=400,
        content={
            "code": error.code,
            "message": error.message,
            "attributes": error.attributes,
        },
    )


@app.exception_handler(Exception)
async def exception_handler(request: Request, error: BusinessError):
    return JSONResponse(
        status_code=400,
        content={
            "code": error.code,
            "message": error.message,
            "attributes": error.attributes,
        },
    )


app.include_router(student_router, tags=["Students"], prefix="/mattilda")
app.include_router(school_router, tags=["Schools"], prefix="/mattilda")
app.include_router(invoice_router, tags=["Invoices"], prefix="/mattilda")
