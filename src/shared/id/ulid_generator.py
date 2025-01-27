from ulid import monotonic as ulid_monotonic

from src.shared.id.generator import IdGenerator


class UlidIdGenerator(IdGenerator):
    async def generate(self) -> str:
        str(ulid_monotonic.new())
