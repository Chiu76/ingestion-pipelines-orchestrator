from enum import StrEnum


class TaskStatus(StrEnum):
    INITIALIZED = 'initialized'
    RUNNING = 'running'
    EXCEPTION = 'exception'
    FAILED = 'failed'
    SUCCESS = 'success'
    SKIPPED = 'skipped'
    DEPENDENCY_FAILED = 'dependency_failed'
