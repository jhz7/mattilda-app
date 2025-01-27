from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from src.shared.contact.model import Contact


class IdentityKind(Enum):
    CURP = "CURP"
    PASSPORT = "PASSPORT"


@dataclass
class Identity:
    kind: IdentityKind
    code: str


@dataclass
class Student:
    id: str
    first_name: str
    last_name: str
    age: int
    contact: list[Contact]
    identity: Identity
    created_at: datetime
    updated_at: datetime


@dataclass
class NewStudent(Student):
    id: str = field(init=False)
    created_at: datetime = field(init=False)
    updated_at: datetime = field(init=False)
