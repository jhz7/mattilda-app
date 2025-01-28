from dotenv import load_dotenv
from fastapi import FastAPI
from src.student.infrastructure.api.http.route import router as student_router
from src.school.infrastructure.api.http.route import router as school_router

load_dotenv()

app = FastAPI()

app.include_router(student_router, prefix="/mattilda")
app.include_router(school_router, prefix="/mattilda")
