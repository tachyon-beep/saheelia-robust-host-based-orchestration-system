"""Core orchestration logic connecting the CLI and Servo containers."""

from pathlib import Path
from .config import Config
from .task_manager import TaskManager, TaskStatus
from .servo_manager import ServoManager


class SaheeliOrchestrator:
    """Manage task queue and Servo container execution."""

    def __init__(self, config: Config) -> None:
        """Initialize managers using the given configuration."""
        self.config = config
        self.task_manager = TaskManager()
        self.servo_manager = ServoManager(config)
        self.results_dir = Path("results")

    def build_servo_image(self) -> None:
        """Build the Docker image for Servo agents."""
        self.servo_manager.build_image()

    def submit_task(self, prompt_path: Path) -> str:
        """Add a new task and return its ID."""
        task_id = self.task_manager.add_task(prompt_path)
        return task_id

    def get_status(self):
        """Return status information for all tasks."""
        return self.task_manager.list_tasks()

    def launch_next_task(self) -> None:
        """Launch the next pending task if one is available."""
        task = self.task_manager.next_task()
        if not task:
            return
        self.task_manager.update_status(task.task_id, TaskStatus.RUNNING)
        workspace = self.results_dir / task.task_id
        workspace.mkdir(parents=True, exist_ok=True)
        container = self.servo_manager.run_servo(task.task_id, task.prompt, workspace)
        status_code = self.servo_manager.wait_for_exit(container)
        complete = self.servo_manager.check_complete(workspace)
        self.servo_manager.copy_workspace(container, workspace)
        self.servo_manager.remove_container(container)
        if status_code == 0 and complete:
            self.task_manager.update_status(task.task_id, TaskStatus.COMPLETE)
        else:
            self.task_manager.update_status(task.task_id, TaskStatus.INCOMPLETE)
