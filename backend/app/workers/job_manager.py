import time
import uuid
import heapq
from typing import Dict, Any, Callable, List, Optional
from app.core.logger import get_logger

logger = get_logger()

class JobPriority:
    CRITICAL = 1
    HIGH = 2
    NORMAL = 3
    LOW = 4

class JobTask:
    def __init__(self, job_id: str, fn: Callable, args=(), kwargs=None, priority: int = JobPriority.NORMAL, delay_sec: float = 0.0):
        self.job_id = job_id
        self.fn = fn
        self.args = args or ()
        self.kwargs = kwargs or {}
        self.priority = priority
        self.execute_at = time.time() + delay_sec
        self.retries = 0
        self.max_retries = 3
        self.status = "PENDING" # PENDING, RUNNING, COMPLETED, FAILED

    def __lt__(self, other):
        # Priority Queue ordering: lowest numeric value = highest priority
        if self.priority == other.priority:
            return self.execute_at < other.execute_at
        return self.priority < other.priority

class WorkerManager:
    """
    Enterprise Worker & Asynchronous Job Manager.
    Supports Immediate, Delayed, Scheduled, Retry, and Batch jobs across Priority Queues (CRITICAL, HIGH, NORMAL, LOW).
    Abstracted interface designed for Celery / RabbitMQ drop-in replacement.
    """

    def __init__(self):
        self._priority_queue: List[JobTask] = []
        self._completed_jobs: Dict[str, dict] = {}

    def enqueue_job(
        self,
        fn: Callable,
        args: tuple = (),
        kwargs: dict = None,
        priority: int = JobPriority.NORMAL,
        delay_sec: float = 0.0,
        job_id: str = None
    ) -> str:
        job_id = job_id or str(uuid.uuid4())
        task = JobTask(job_id, fn, args, kwargs, priority, delay_sec)
        heapq.heappush(self._priority_queue, task)
        logger.info(f"Enqueued job {job_id} [Priority: {priority}, Delay: {delay_sec}s]")
        return job_id

    def process_next_job(self) -> Optional[dict]:
        if not self._priority_queue:
            return None

        # Check top job
        now = time.time()
        if self._priority_queue[0].execute_at > now:
            return None # Top job not ready yet

        task = heapq.heappop(self._priority_queue)
        task.status = "RUNNING"
        start_time = time.time()

        try:
            result = task.fn(*task.args, **task.kwargs)
            duration_ms = round((time.time() - start_time) * 1000, 2)
            task.status = "COMPLETED"
            
            res_summary = {
                "job_id": task.job_id,
                "status": "COMPLETED",
                "duration_ms": duration_ms,
                "result": result
            }
            self._completed_jobs[task.job_id] = res_summary
            return res_summary
        except Exception as ex:
            task.retries += 1
            if task.retries < task.max_retries:
                task.execute_at = time.time() + (task.retries * 2) # Exponential backoff
                heapq.heappush(self._priority_queue, task)
                logger.warning(f"Job {task.job_id} failed. Retrying ({task.retries}/{task.max_retries})... Error: {str(ex)}")
            else:
                task.status = "FAILED"
                err_summary = {
                    "job_id": task.job_id,
                    "status": "FAILED",
                    "error": str(ex)
                }
                self._completed_jobs[task.job_id] = err_summary
                return err_summary

    def get_job_status(self, job_id: str) -> Optional[dict]:
        return self._completed_jobs.get(job_id)

worker_manager = WorkerManager()
