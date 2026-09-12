import itertools
import logging
from typing import Callable
from datetime import datetime, timezone
import json

from enum import StrEnum

from .core.db import SessionMaker
from .core.models import TaskRun


class TaskStatus(StrEnum):
    INITIALIZED = 'initialized'
    RUNNING = 'running'
    EXCEPTION = 'exception'
    FAILED = 'failed'
    SUCCESS = 'success'
    SKIPPED = 'skipped'
    DEPENDENCY_FAILED = 'dependency_failed'



class Job():
    id_iter = itertools.count()
    def _get_job_id(self) -> str: return f'{self.name}_{str(next(Job.id_iter))}'

    def __init__(self, name: str):
        self.name = name

        self.id: str = self._get_job_id()
        # list of Task instances
        self.to_execute: list = []

    def set_to_execute(self, to_execute: list):
        self.to_execute = to_execute

    def run(self):
        continue_running_flag = True
        for task in self.to_execute:
            if continue_running_flag:
                task.connect_to_job(self)
                status, vars = task.execute()
                print(task.name, status, vars)
                if status in [TaskStatus.FAILED, TaskStatus.EXCEPTION]:
                    continue_running_flag = False
            else:
                task.status = TaskStatus.DEPENDENCY_FAILED
                task.vars = {}
                print(task.name, task.status, task.vars)


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
