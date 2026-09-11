from ..task import Task
from ..schemas import TaskStatus


def init_task__(force_refresh: bool = False):
    return Task(
        'task__',
        fn,
        log_messages,
        force_refresh=force_refresh,
    )


def fn(self: Task, force_refresh: bool = False):
    self.log_info('start_task')

    self.vars = {
        'task_var': 'value',
    }

    self.status = TaskStatus.SUCCESS

    self.log_info('end_task')


log_messages = {
    'start_task': 'TASK_START: start_task',
    'end_task': 'TASK_END: end_task',
}
