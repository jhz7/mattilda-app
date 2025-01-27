from dotenv import load_dotenv
from fastapi import FastAPI
from contextlib import asynccontextmanager
from src.student.infrastructure.api.http.route import router as student_routes

load_dotenv()

app = FastAPI()


# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     pass


app = FastAPI()

app.include_router(student_routes, prefix="/mattilda")
