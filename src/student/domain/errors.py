from src.shared.errors.business import BusinessError


def InvalidStatusError(student_id: str) -> BusinessError:
    return BusinessError(
        code="StudentInvalidStatusError",
        message=f"Invalid status for student {student_id}",
        attributes={"student_id": student_id},
    )
