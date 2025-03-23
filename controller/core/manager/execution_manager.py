import os
import json
from handlers.curl_handler import CurlHandler
from logmanager.logger_manager import LoggerManager
from utils.global_store import GlobalStore,LocalStore
class ExecutionManager:
    """Manages the execution sequence of API requests in a scenario."""

    def __init__(self, scenario_path):
        self.scenario_path = scenario_path
        self.local_store=LocalStore()
        self.curl_handler = CurlHandler()
        self.global_store = GlobalStore() #since i need region path i'm not using local store as we region_path is globally accessed and consant 
        self.logger = LoggerManager(self.__class__.__name__)
        self.execution_sequence_file = os.path.join(scenario_path, "execution_sequence.json")

    def load_execution_sequence(self):
        """Loads execution sequence from JSON file."""
        if not os.path.exists(self.execution_sequence_file):
            self.logger.log_error(f"Execution sequence file not found: {self.execution_sequence_file}")
            return []

        with open(self.execution_sequence_file, "r") as file:
            return json.load(file)
        
    def test(self,response,api_name):
        self.orchestrator.register_class("schema_validator")
        self.orchestrator.execute_method("schema_validator","validate_schema",response,os.path.join(self.schema_path,api_name+".py"),api_name.upper())

    def execute_request(self, request_file,method):
        """Executes a single request from the sequence."""
        request_path = os.path.join(self.scenario_path, "requests/", request_file+".curl")
        if not os.path.exists(request_path):
            self.logger.log_debug(f"Request file not found: {request_path}")
            return {"status":"failed"}
        response= self.curl_handler.execute_curl(request_path,method,request_file)
        return response
