from orchestrator.job import Job

from templates.precheck_template import init_precheck__
from templates.task_template import init_task__


def run_job__():
    job = Job('job__')
    job.to_execute = [
        init_precheck__(),
        init_task__(force_refresh=False),
    ]
    job.run()
