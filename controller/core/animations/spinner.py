import time
from rich.console import Console
from rich.progress import SpinnerColumn, Progress

class Spinner:
    """Displays a circular spinner while executing tasks."""

    def __init__(self):
        self.console = Console()

    def run_with_spinner(self, task_name, function, *args, **kwargs):
        """Executes a function with a spinner and returns its result.
        
        Args:
            task_name (str): The name of the task being executed.
            function (callable): The function to execute.
            *args, **kwargs: Arguments for the function.
        
        Returns:
            The result of the function execution.
        """
        with Progress(SpinnerColumn(), transient=True) as progress:
            task = progress.add_task(f"[yellow]Processing {task_name}...", total=None)

            # Execute the function (e.g., API request)
            time.sleep(1)  # Optional delay to show the loader
            result = function(*args, **kwargs)

            # Determine status and color
            status = "failed" if not result else result.get("status", "failed")
            color = "green" if status == "success" else "red"
            icon = "🟢" if status == "success" else "🔴"

            progress.remove_task(task)
            self.console.print(f" {icon} [bold {color}]{task_name} -> {status.upper()}[/bold {color}]")

            return result  # Return the result for further processing
