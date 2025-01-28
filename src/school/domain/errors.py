from src.shared.errors.business import BusinessError


def InvalidStatusError(school_id: str) -> BusinessError:
    return BusinessError(
        code="SchoolInvalidStatusError",
        message=f"Invalid status for school {school_id}",
        attributes={"school_id": school_id},
    )
