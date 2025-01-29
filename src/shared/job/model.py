from abc import ABC
from dataclasses import dataclass
from datetime import datetime
from typing import Literal, final


class JobItemResult(ABC):
    id: str
    started_at: str
    finished_at: str


@dataclass
class SuccessJobItem(JobItemResult):
    id: str
    started_at: str
    finished_at: str

    @property
    @final
    def kind(self) -> Literal["SUCCESS"]:
        return "SUCCESS"


@dataclass
class FailureJobItem(JobItemResult):
    id: str
    started_at: str
    finished_at: str
    error: str

    @property
    @final
    def kind(self) -> Literal["FAILURE"]:
        return "FAILURE"


@dataclass
class StartedJobItem:
    id: str
    started_at: datetime

    def succeeded(self, finished_at: datetime) -> SuccessJobItem:
        return SuccessJobItem(
            id=self.id,
            started_at=f"{self.started_at}",
            finished_at=f"{finished_at}",
        )

    def failed(self, finished_at: datetime, error: str) -> FailureJobItem:
        return FailureJobItem(
            id=self.id,
            started_at=f"{self.started_at}",
            finished_at=f"{finished_at}",
            error=error,
        )


class JobExecutionResult(ABC):
    id: str
    job_name: str
    started_at: datetime
    finished_at: datetime


@dataclass
class SuccessJobExecution(JobExecutionResult):
    id: str
    job_name: str
    started_at: datetime
    finished_at: datetime
    items: list[JobItemResult]
    succeed_items: int
    failed_items: int

    @property
    @final
    def kind(self) -> Literal["SUCCESS"]:
        return "SUCCESS"


@dataclass
class FailureJobExecution(JobExecutionResult):
    id: str
    job_name: str
    started_at: datetime
    finished_at: datetime
    error: str

    @property
    @final
    def kind(self) -> Literal["FAILURE"]:
        return "FAILURE"


@dataclass
class StartedJob:
    id: str
    job_name: str
    started_at: datetime

    def succeeded(
        self, finished_at: datetime, items: list[JobItemResult]
    ) -> SuccessJobExecution:
        succed_items = len([item for item in items if isinstance(item, SuccessJobItem)])
        failed_items = len([item for item in items if isinstance(item, FailureJobItem)])
        return SuccessJobExecution(
            id=self.id,
            job_name=self.job_name,
            started_at=self.started_at,
            finished_at=finished_at,
            items=items,
            succeed_items=succed_items,
            failed_items=failed_items,
        )

    def failed(self, finished_at: datetime, error: str) -> FailureJobExecution:
        return FailureJobExecution(
            id=self.id,
            job_name=self.job_name,
            started_at=self.started_at,
            finished_at=finished_at,
            error=error,
        )
