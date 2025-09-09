import threading

class TaskManager:
    def __init__(self):
        self._tasks = {}
        self._lock = threading.Lock()

    def get_workflow_id(self, task_id):
        with self._lock:
            return self._tasks.get(task_id)

    def add_task(self, task_id, workflow_id):
        with self._lock:
            if task_id in self._tasks:
                raise ValueError(f"Task {task_id} already exists")
            self._tasks[task_id] = workflow_id

    def delete_task(self, task_id):
        with self._lock:
            if task_id not in self._tasks:
                raise KeyError(f"Task {task_id} not found")
            del self._tasks[task_id]

    def list_tasks(self):
        with self._lock:
            return dict(self._tasks)


global_task_manager = TaskManager()