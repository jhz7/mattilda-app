from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from src.shared.db.pg_sqlalchemy.connection import get_db
from src.student.infrastructure.persistence.sqlalchemy.dbo import StudentDbo


router = APIRouter()


class StudentDto(BaseModel):
    first_name: str
    last_name: str
    age: int
    identity_kind: str
    identity_code: str


@router.post("/students")
async def create_student(request: StudentDto, db: AsyncSession = Depends(get_db)):
    student_dbo = StudentDbo(
        first_name=request.first_name,
        last_name=request.last_name,
        age=request.age,
        identity_kind=request.identity_kind,
        identity_code=request.identity_code,
        status="active",
    )

    db.add(student_dbo)
    await db.commit()
    await db.refresh(student_dbo)

    return student_dbo
