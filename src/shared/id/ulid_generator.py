from ulid import monotonic as ulid_monotonic

from src.shared.id.generator import IdGenerator


class UlidIdGenerator(IdGenerator):
    async def generate(self) -> str:
        ulid = ulid_monotonic.new()
        return str(ulid)


def get_id_generator() -> IdGenerator:
    return UlidIdGenerator()
