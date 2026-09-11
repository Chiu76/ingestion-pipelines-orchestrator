import itertools
import logging
from typing import Callable
from datetime import datetime, timezone
import json

from db import SessionMaker
from models import TaskRun

from orchestrator import Job
from orchestrator.schemas import TaskStatus


class Task():
    id_iter = itertools.count()

    def __init__(self, name: str, fn: Callable, log_messages: dict[str, str] = {}, *args, **kwargs):
        self.name = name
        self.fn = fn
        self.log_messages = log_messages
        self.args = args
        self.kwargs = kwargs

        self.execution_id: str = str(next(Task.id_iter))
        self.status: TaskStatus = TaskStatus.INITIALIZED
        self.vars: dict = {}
        self.start_timestamp: datetime | None = None 
        self.end_timestamp: datetime | None = None

        # tasks can be created independently of a job
        # before a job executes a task, the job connects the task to itself by running Task.connect_to_job() 
        self.job_id: str | None = None
        self.logger: logging.Logger = logging.getLogger(f'{self.name}')

    def connect_to_job(self, job: Job):
        self.job_id = job.id
        self.logger = logging.getLogger(f'{self.job_id}:{self.name}')

    def insert_task_run(self):
        with SessionMaker() as session:
            task_run = TaskRun(
                job_id=self.job_id,
                execution_id=self.execution_id,
                task_name=self.name,
                status=self.status,
                vars=json.dumps(self.vars),
                start_timestamp=self.start_timestamp,
                end_timestamp=self.end_timestamp,
            )
            session.add(task_run)
            session.commit()

    def execute(self) -> None: 
        self.status = TaskStatus.RUNNING
        self.start_timestamp = datetime.now(timezone.utc)

        try:
            self.fn(self, *self.args, **self.kwargs)
            if self.status == TaskStatus.RUNNING:
                raise Exception('Task function ended without updating `Task.status` from `RUNNING` value during its execution')
        except Exception as e:
            print(f'{self.name}: failed with exception: {e}')
            self.logger.error(e)
            self.status = TaskStatus.EXCEPTION
            self.vars = {'exception': str(e)}

        self.end_timestamp = datetime.now(timezone.utc)

        self.insert_task_run()

        return self.status, self.vars

    def _get_log_message(self, key: str, *format_vars) -> str:
        return self.log_messages[key].format(*format_vars)

    def log_info(self, key: str, *format_vars) -> None:
        return self.logger.info(self._get_log_message(key, *format_vars))
