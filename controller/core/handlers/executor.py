import os
from manager.execution_manager import ExecutionManager
from logmanager.logger_manager import LoggerManager
from animations.spinner import Spinner 
from reporting.report_generator import HTMLReportGenerator
from utils.global_store import GlobalStore,LocalStore
class Executor:
    """Executes API test scenarios in sequence with a circular loader."""

    def __init__(self, scenario_path):
        self.scenario_path = scenario_path
        self.logger = LoggerManager(self.__class__.__name__)
        self.global_store = GlobalStore()
        self.local_store = LocalStore()
        self.report_generator = HTMLReportGenerator(self.global_store.get_value("selected_region"),self.local_store.get_value("scenario_name"),self.logger.LOG_FILE_PATH)
        self.execution_manager = ExecutionManager(scenario_path)
        self.spinner = Spinner()  # Create an instance of the spinner


    def generate_report(self):
        """Generate HTML report after execution."""
        self.report_generator.generate_html_report(self.global_store.get_value("final_test_results"))

    def run(self):
        """Executes the test scenario in the defined order."""
        try:
            execution_sequence = self.execution_manager.load_execution_sequence()

            if not execution_sequence:
                self.logger.log_info("Execution sequence is empty. Skipping execution.")
                return

            scenario_name = os.path.basename(self.scenario_path)
            self.spinner.console.print(f"\n[bold cyan]Executing Scenario:[/bold cyan] {scenario_name}")
            scenario_status = "success"  # Assume success unless an API fails

            for api in execution_sequence:
                request_api, method = api.split(":")
                result = self.spinner.run_with_spinner(
                    request_api, self.execution_manager.execute_request, request_api, method
                )

                if not result or result.get("status") != "success":
                    scenario_status = "failed"  # Mark scenario as failed if any API fails

            # Print final scenario status
            final_color = "green" if scenario_status == "success" else "red"
            final_icon = "🟢" if scenario_status == "success" else "🔴"
            self.spinner.console.print(f"\n{final_icon} [bold {final_color}]{scenario_name} -> {scenario_status.upper()}[/bold {final_color}]")
        except Exception as e:
            self.logger.log_error(f"Error executing scenario: {str(e)}")
        finally:
            self.generate_report()