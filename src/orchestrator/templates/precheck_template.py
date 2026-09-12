from ..orchestrator import Task, TaskStatus


def init_precheck__():
    def fn(self: Task):
        self.vars = { 'precheck_var': 'value' }
        self.status = TaskStatus.SUCCESS
    return Task('precheck__', fn)
