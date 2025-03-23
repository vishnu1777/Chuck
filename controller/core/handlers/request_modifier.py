import json
from utils.global_store import GlobalStore,LocalStore
from manager.dependency_manager import DependencyManager
from utils.file_utils import *
import re
from datetime import datetime, timedelta
from logmanager.logger_manager import LoggerManager

class RequestModifier:
    def __init__(self, scenario_path):
        self.scenario_path = scenario_path
        self.global_store = GlobalStore()
        self.local_store=LocalStore()
        try:
            self.scenario_path = self.local_store.get_value('scenario_path')
            self.dependency_manager = DependencyManager()
            self.logger = LoggerManager(self.__class__.__name__)
            self.base_url, self.path_config = self.load_config()
        except Exception as e:
            print(f"Error initializing RequestModifier: {e}")
            self.base_url, self.path_config = None, {}

    def load_config(self):
        """Load base URL and API paths."""
        try:
            with open(self.global_store.get_value('path_config_path'), "r") as file:
                path_config = json.load(file)
            return self.global_store.get_value("base_url"), path_config
        except Exception as e:
            print(f"Error loading config: {e}")
            return None, {}

    def replace_doj_in_url(self, url):
        """Replaces DOJ (date) in the URL dynamically."""
        try:
            global_store = GlobalStore()
            env_data = global_store.get_value("env_data")
            date_config = env_data.get("date", {})

            if not env_data or not date_config:
                return url  

            days_offset = date_config.get("custom", date_config.get("default"))
            date_format = date_config.get("format", "%Y-%m-%d")
            new_doj = (datetime.today() + timedelta(days=days_offset)).strftime(date_format)
            date_pattern = re.compile(r"\d{4}-\d{2}-\d{2}")

            if date_pattern.search(url):
                return date_pattern.sub(new_doj, url)
            return url
        except Exception as e:
            print(f"Error replacing DOJ in URL: {e}")
            return url

    def get_new_date(self):
        """Gets the new date based on configuration."""
        try:
            global_store = GlobalStore()
            env_data = global_store.get_value("env_data")
            date_config = env_data.get("date", {})

            days_offset = date_config.get("custom", date_config.get("default"))
            date_format = date_config.get("format", "%Y-%m-%d")
            return (datetime.today() + timedelta(days=days_offset)).strftime(date_format)
        except Exception as e:
            print(f"Error getting new date: {e}")
            return datetime.today().strftime("%Y-%m-%d")  # Return today's date as fallback

    def detect_date_format(self, date_str):
        """Detects the format of a date string and returns its datetime format."""
        try:
            date_formats = [
                ("%d %B %Y", r"\b\d{2} [A-Za-z]+ \d{4}\b"),
                ("%d-%m-%Y", r"\b\d{2}-\d{2}-\d{4}\b"),
                ("%d/%m/%Y", r"\b\d{2}/\d{2}/\d{4}\b"),
                ("%B %d, %Y", r"\b[A-Za-z]+ \d{2}, \d{4}\b")
            ]
            for fmt, pattern in date_formats:
                if re.fullmatch(pattern, date_str):
                    return fmt
            return None
        except Exception as e:
            print(f"Error detecting date format: {e}")
            return None

    def replace_dates(self, payload, target_date):
        """Recursively replaces dates in a JSON payload while keeping the original format."""
        try:
            if isinstance(payload, dict):
                return {k: self.replace_dates(v, target_date) for k, v in payload.items()}
            elif isinstance(payload, list):
                return [self.replace_dates(item, target_date) for item in payload]
            elif isinstance(payload, str):
                detected_format = self.detect_date_format(payload)
                if detected_format:
                    formatted_date = datetime.strptime(target_date, "%Y-%m-%d").strftime(detected_format)
                    return formatted_date
            return payload
        except Exception as e:
            print(f"Error replacing dates: {e}")
            return payload  # Return unchanged payload in case of error

    def replace_base_url(self, url):
        """Replaces base URL dynamically."""
        try:
            return re.sub(r"^https:[\\/]+[^\\/]+", self.base_url, url)
        except Exception as e:
            print(f"Error replacing base URL: {e}")
            return url
        

    def replace_headers_based_on_selection(self):
        try:
            current_channel_name=self.local_store.get_value("current_channel")
            channel_config_path=os.path.join(self.global_store.get_value("region_config_path"),"channel_headers")
            if not os.path.exists(channel_config_path):
                raise FileNotFoundError(f"Ooops looks like the channel config  is missing!! {channel_config_path}")
            channel_header_path=os.path.join(channel_config_path,current_channel_name+".json")
            if not os.path.exists(channel_header_path):
                raise FileNotFoundError(f"Ooops looks like the channel file  is missing!! {channel_header_path}")
            new_headers=read_json_file(channel_header_path)
            if self.global_store.get_value("active_language") and new_headers.get("Language"):
                new_headers["Language"]=self.global_store.get_value("active_language")
            return new_headers
        except Exception as e:
            print("Ooops looks like the channel file is missing!! ")
            self.logger.log_error(f"Channel file is missing error->{str(e)}")


            
    def update_request_components(self, request_name, url, headers, payload, query_params):
        """Replace placeholders in extracted request components with stored values."""
        try:
            dependencies = self.load_dependencies()
            url = self.replace_doj_in_url(url) 
            headers=self.replace_headers_based_on_selection()  #get the selective header
            if request_name not in dependencies:
                return url, headers, payload, query_params

            dependency = dependencies[request_name]

            if dependency.get("replace_path_params"):
                url = self.process_path_params(request_name)

            url = self.replace_doj_in_url(url)
            url = self.replace_base_url(url)

            if "replace" in dependency:
                locations = dependency["replace"]["location"]
                if "query_params" in locations:
                    new_query_params = self.dependency_manager.extract_values(query_params, request_name, True)
                    query_params = query_params if not new_query_params else new_query_params
                if "headers" in locations:
                    new_header = self.dependency_manager.extract_values(headers, request_name, True)
                    headers = headers if not new_header else new_header
                if "payload" in locations:
                    new_payload = self.dependency_manager.extract_values(payload, request_name, True)
                    payload = payload if not new_payload else new_payload

            payload = self.replace_dates(payload, self.get_new_date())
            return url, headers, payload, query_params
        except Exception as e:
            print(f"Error updating request components: {e}")
            return url, headers, payload, query_params  # Return original values in case of failure

    def process_path_params(self, request_name):
        """Replace path parameters dynamically using values from GlobalStore."""
        try:
            if request_name not in self.path_config:
                raise ValueError(f"API '{request_name}' not found in path_config.json")

            api_path = self.path_config[request_name]

            for param in api_path.split("/{")[1:]:
                param_name = param.split("}")[0]
                value = self.local_store.get_value(param_name)
                if value is not None:
                    api_path = api_path.replace(f"{{{param_name}}}", str(value))

            return f"{self.base_url}{api_path}"
        except Exception as e:
            print(f"Error processing path parameters for {request_name}: {e}")
            return f"{self.base_url}/{request_name}"  # Return fallback path

    def replace_json_value(self, json_data, key, new_value):
        """Replace a value inside JSON data."""
        try:
            if isinstance(json_data, dict) and key in json_data:
                json_data[key] = new_value
            return json_data
        except Exception as e:
            print(f"Error replacing JSON value: {e}")
            return json_data

    def load_dependencies(self):
        """Load dependencies.json file."""
        try:
            dependencies_file = self.local_store.get_value("merged_config_path")
            with open(dependencies_file, "r") as file:
                return json.load(file)
        except FileNotFoundError:
            print("Dependencies file not found.")
            return {}
        except Exception as e:
            print(f"Error loading dependencies: {e}")
            return {}
