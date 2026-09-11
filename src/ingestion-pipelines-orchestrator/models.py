from datetime import datetime

from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column

from db import Model


class TaskRun(Model):
    __tablename__ = 'task_runs'

    id: Mapped[int] = mapped_column(primary_key=True)

    job_id: Mapped[str] = mapped_column(String(64), nullable=True, index=True)
    execution_id: Mapped[int] = mapped_column(Integer, nullable=False)
    task_name: Mapped[str] = mapped_column(String(64), nullable=False, index=True)

    status: Mapped[str] = mapped_column(String(64), nullable=False)
    vars: Mapped[str] = mapped_column(String, nullable=False)

    start_timestamp: Mapped[datetime] = mapped_column(nullable=False)
    end_timestamp: Mapped[datetime] = mapped_column(nullable=False)
