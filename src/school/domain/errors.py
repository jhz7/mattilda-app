from src.shared.errors.business import BusinessError


def InvalidEnrollmentError(school_id: str, student_id: str) -> BusinessError:
    return BusinessError(
        code="InvalidEnrollmentError",
        message=f"EnrollmentDeletedError",
        attributes={"school_id": school_id, "student_id": student_id},
    )


def InvalidEnrollmentError(school_id: str, student_id: str) -> BusinessError:
    return BusinessError(
        code="InvalidEnrollmentError",
        message=f"EnrollmentDeletedError",
        attributes={"school_id": school_id, "student_id": student_id},
    )


def InvalidSchoolStatusError(school_id: str) -> BusinessError:
    return BusinessError(
        code="SchoolInvalidStatusError",
        message=f"Invalid status for school {school_id}",
        attributes={"school_id": school_id},
    )
