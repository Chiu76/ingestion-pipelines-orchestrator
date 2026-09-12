import itertools

from .schemas import TaskStatus


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
