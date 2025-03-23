import re
from logmanager.logger_manager import LoggerManager
from handlers.curl import *
from utils.global_store import GlobalStore,LocalStore
from utils.process_request import *
from handlers.request_modifier import RequestModifier
from utils.file_utils import *
from validators.orchestratror import Orchestrator
from manager.dependency_manager import DependencyManager
from utils import error_handling
from validators.test_manager import TestAPIValidation
class CurlHandler:
    """Handles execution of curl requests with environment URL updates."""

    def __init__(self):
        self.global_store = GlobalStore()
        self.local_store=LocalStore()
        self.orchestrator = Orchestrator()
        self.base_url = self.global_store.get_value("base_url") #same here
        self.logger = LoggerManager(self.__class__.__name__)
        self.schema_path=os.path.join(self.global_store.get_value("region_path"),"schema")
        self.test_obj=TestAPIValidation(self.orchestrator,self.schema_path)
        self.scenario_path=self.local_store.get_value("scenario_path")
        self.request_modifier = RequestModifier(self.scenario_path)
        self.curlObj = CURL()
        self.dependency_manager = DependencyManager()
    
    def clean_curl_command(self,curl_command):
        # Remove all single and double backslashes
        curl_command = curl_command.replace("\\\\", "").replace("\\", "")
        # Replace multiple spaces and newlines with a single space
        curl_command = re.sub(r'\s+', ' ', curl_command).strip()
        return curl_command


    def get_curl_command(self,curl_path):
        try:
            with open(curl_path, "r") as file:
                curl_command = file.read()
            return self.clean_curl_command(curl_command).replace("\\", "")
        except FileNotFoundError:
            print(f"File {curl_path} not found.")
            return None
        
    def execute_curl(self, curl_path,method,request_name):
        """Reads, modifies, and executes a .curl request."""
        try:
            
            curl_command = self.get_curl_command(curl_path)
            url, headers, payload, query_params = self.curlObj.extract_curl_components(curl_command)
            new_headers = {key.rstrip(';'): value for key, value in headers.items()}
            # update the replace value in the respective files
            url, new_headers, payload, query_params=self.request_modifier.update_request_components(request_name,url,new_headers,payload,query_params)
            self.curlObj.saveAllFiles(new_headers,payload,query_params,url)
            self.logger.log_info(f"curl for {request_name}->",self.curlObj.generateCurl(method,url,new_headers,payload))
            response,time_taken = get_url_response(method,url,new_headers,query_params,payload)
            # store values
            self.dependency_manager.extract_values(response,request_name)
            # print("response->",response)
            self.logger.log_info(f"response for {request_name}->{response}")
            # testing starts here
            self.test_obj.test(response,request_name)
            return response
        except Exception as e:
            error_handling.set_status_failed(response)
            self.logger.log_error(f"Unexpected error while executing in execute_curl method -> {curl_path} : {str(e)}")
            print(f"Unexpected error while executing in execute_curl method -> {curl_path} : {str(e)}")



    def extract_url_and_path(self,curl_command):
        """Extracts the base URL (until .com) and the path parameters after .com."""
        url_match = re.search(r"'(http[s]?://[^/]+\.com)(/.*?)?'", curl_command)
        if url_match:
            base_url = url_match.group(1)  
            path_params = url_match.group(2) if url_match.group(2) else ""
            return base_url, path_params
        return None, None


    def extract_path(self, full_url):
        """Extracts only the path from the full URL."""
        return "/" + "/".join(full_url.split("/")[3:])  # Remove domain part
