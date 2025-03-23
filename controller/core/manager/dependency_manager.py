import json
import os
import re
from utils.global_store import GlobalStore,LocalStore
import logging
from validators.orchestratror import Orchestrator
from utils import error_handling
import urllib.parse
class DependencyManager:
    def __init__(self):
        self.local_store=LocalStore()
        self.global_store = GlobalStore()
        self.scenario_path = self.local_store.get_value('scenario_path')
        self.dependencies = self.load_dependencies()
        self.orchestrator = Orchestrator()
        
    def resolve_path_with_arrays(self, json_response, path_string, return_list=False):
        """
        Resolves a path with array indices marked with [*] and correctly handles both:
        - List values (if [*] is present)
        - Non-list values (if [*] is absent)
        """
        if not path_string:
            return None

        current_value = json_response
        parts = path_string.split('.')

        for i, part in enumerate(parts):
            if '[*]' in part:
                array_key = part.split('[*]')[0]

                if not isinstance(current_value, dict) or array_key not in current_value:
                    return [] if return_list else None
                
                array_value = current_value[array_key]
                if not isinstance(array_value, list):  # Handle non-list case
                    return array_value  # Directly return the value if it's not a list
                
                remaining_path = '.'.join(parts[i + 1:])
                results = []

                for item in array_value:
                    if not remaining_path:  # If this is the last part, return the item itself
                        results.append(item)
                    else:
                        # For nested [*], we want to collect all values
                        if '[*]' in remaining_path:
                            nested_results = self.resolve_path_with_arrays(item, remaining_path, return_list=True)
                            if nested_results is not None:
                                if isinstance(nested_results, list):
                                    results.extend(nested_results)
                                else:
                                    results.append(nested_results)
                        else:
                            result = self.resolve_path_with_arrays(item, remaining_path, return_list=False)
                            if result is not None:
                                results.append(result)

                return results if return_list else (results[0] if results else None)

            elif isinstance(current_value, dict) and part in current_value:
                current_value = current_value[part]  # Fixed: Actually update current_value
            else:
                return None

        return current_value  # Return value even if it's a single field like `metaData.totalCount`


    def extract_values(self, response, request_name, is_replace=False):
        """Extract values from API response based on multiple conditions and store them individually in GlobalStore."""
        try:
            if not response:
                return response  # If response is empty, return it immediately

            request_name = request_name.strip()
            logging.info(f"Processing Request: {request_name}")

            key_type = "replace" if is_replace else "store"

            # Get the "store" or "replace" section from dependencies.json
            extraction_map = self.dependencies.get(request_name, {}).get(key_type, {})

            if not extraction_map:
                logging.warning(f"No '{key_type}' section found for '{request_name}'")
                return response

            for key, config in extraction_map.items():
                if key == "location":
                    continue  # Skip processing for "location"

                try:
                    # Ensure config is always treated as a list (to handle multiple conditions)
                    config_list = config if isinstance(config, list) else [config]

                    for sub_config in config_list:
                        if not isinstance(sub_config, dict):
                            logging.error(f"Invalid sub_config format for key: {key}, expected dict but got {type(sub_config)}")
                            continue

                        json_paths = sub_config.get("json_paths", {})
                        conditions = sub_config.get("condition", []) if isinstance(sub_config, dict) else []

                        # Extract additional flags (except json_paths & condition)
                        flags = {k: v for k, v in sub_config.items() if k not in {"json_paths", "condition"}}

                        if key_type == "store":
                            self.process_and_store_value(response, key, json_paths, conditions, **flags)
                        elif key_type == "replace":
                            self.process_and_update_obj(response, key, json_paths, conditions, **flags)

                except Exception as e:
                    error_handling.set_status_failed(response)
                    logging.error(f"Error processing key '{key}': {str(e)}", exc_info=True)

        except Exception as e:
            error_handling.set_status_failed(response)
            logging.critical(f"Critical failure in extract_values: {str(e)}", exc_info=True)

        return response

    def extract_query_param(self,obj, path):
        """
        Extracts a query parameter from a URL string in JSON using the `[?query:...]` notation.
        
        Args:
            obj (dict): JSON object containing the URL field.
            path (str): JSON path with `[?query:...]` notation.

        Returns:
            str: Extracted query parameter value or an empty string if not found.
        """
        if "[?query:" not in path:
            return None  # Not a query param path

        try:
            # Extract base path and query parameter key
            base_path, query_param = path.split("[?query:")
            query_param = query_param.rstrip("]")

            # Resolve the base path to get the URL string
            url = obj.get(base_path.strip())
            if not url:
                return ""

            # Parse the URL and extract query parameters
            parsed_url = urllib.parse.urlparse(url)
            query_params = urllib.parse.parse_qs(parsed_url.query)

            return query_params.get(query_param, [""])[0]  # Return first value or empty string
        except Exception as e:
            print(f"Error extracting query param '{query_param}' from path '{path}': {e}")
            return ""

    def check_sort(self,response,**flags):
        if "sort_order" in flags:
            self.orchestrator.execute_method("sort_manager",self.global_store.get_value(flags.get("sort_order"),{}),response)


    def process_and_store_value(self, response, group_key, json_paths, conditions, **flags):
        """Processes grouped values (keys that must belong to the same object)."""
        try:
            first_key, first_path = next(iter(json_paths.items()))
            first_path_cleaned = first_path.replace("$.", "", 1)

            if "[?query:" in first_path_cleaned:
                for key,path in json_paths.items():
                    self.local_store.set_value(key,self.extract_query_param(response,first_path_cleaned))
                return
            else:
                is_multi_select = flags.get("multi_select", False)
                self.check_sort(response,**flags) 
                parent_path = self.extract_parent_path(first_path_cleaned)
                if not parent_path:
                    self.store_direct_values(self.global_store, response, json_paths)
                    return

                objects = self.resolve_path_with_arrays(response, parent_path, return_list=True)
                if not objects:
                    return

                if not isinstance(objects, list):
                    objects = [objects]

                used_values = set() if is_multi_select else None
                used_keys = set()

                for obj in objects:
                    if self.check_conditions(obj, conditions):
                        self.store_extracted_values(self.global_store, obj, json_paths, used_values, used_keys, is_multi_select)
            
        except Exception as e:
            error_handling.set_status_failed(response)
            print(f"Error processing and storing values for group_key '{group_key}' Please check api response manually once: {str(e)}")


    def extract_parent_path(self,first_path_cleaned):
        """Extracts the parent path from the given cleaned JSON path."""
        return '.'.join(first_path_cleaned.split('.')[:-1]) if '.' in first_path_cleaned else ""


    def store_direct_values(self,global_store, response, json_paths):
        """Stores direct values in global storage when no parent path exists."""
        try:
            for sub_key, sub_path in json_paths.items():
                sub_path_cleaned = sub_path.replace("$.", "", 1)
                self.local_store.set_value(sub_key, response[sub_path_cleaned])
        except KeyError as e:
            error_handling.set_status_failed(response)
            print(f"KeyError: {str(e)} - Some keys not found in response")
        except Exception as e:
            error_handling.set_status_failed(response)
            print(f"Unexpected error while storing direct values: {str(e)}")


    def store_extracted_values(self,global_store, obj, json_paths, used_values, used_keys, is_multi_select):
        """Extracts and stores values while handling multi-select scenarios."""
        try:
            values_to_store = {}
            for sub_key, sub_path in json_paths.items():
                if sub_key in used_keys:
                    continue

                sub_path_cleaned = sub_path.replace("$.", "", 1)
                field_name = sub_path_cleaned.split('.')[-1]

                if isinstance(obj, dict) and field_name in obj:
                    value = obj[field_name]
                    if is_multi_select and value in used_values:
                        continue

                    if is_multi_select:
                        used_values.add(value)
                    
                    values_to_store[sub_key] = value
                    used_keys.add(sub_key)
            
            for sub_key, value in values_to_store.items():
                self.local_store.set_value(sub_key, value)
        except Exception as e:
            print(f"Error while extracting and storing values: {str(e)}")

    def process_and_update_obj(self, response, group_key, json_paths, conditions, **flags):
        """Processes and updates grouped values (keys that must belong to the same object)."""
        try:
            # Determine parent path
            parent_path = self._get_parent_path(json_paths)
            
            # If there is no parent path, update response directly
            if not parent_path:
                self._update_direct_keys(response, json_paths,**flags)
                return
            
            # Get all objects that could contain grouped values
            objects = self.resolve_path_with_arrays(response, parent_path, return_list=True)
            if not objects:
                return
            
            # Ensure objects is a list
            if not isinstance(objects, list):
                objects = [objects]

            # Update nested objects
            self._update_nested_objects(objects, json_paths, conditions,**flags)
        
        except Exception as e:
            error_handling.set_status_failed(response)
            print(f"Error in process_and_update_obj: {str(e)}")

    def _get_parent_path(self, json_paths):
        """Extracts and returns the parent path before the last dot."""
        key, first_path = next(iter(json_paths.items()))
        first_path_cleaned = first_path.replace("$.", "", 1)
        return '.'.join(first_path_cleaned.split('.')[:-1]) if '.' in first_path_cleaned else ""

    def _update_direct_keys(self, response, json_paths,**flags):
        """Directly updates response with stored values when there's no parent path."""
        try:
            for sub_key, sub_path in json_paths.items():
                key = sub_path.replace("$.", "", 1)
                response[key] = self.local_store.get_value(sub_key)
        except KeyError as e:
            error_handling.set_status_failed(response)
            print(f"KeyError in _update_direct_keys: {e}")

    def _update_nested_objects(self, objects, json_paths, conditions, **flags):
        """Updates nested objects that meet the specified conditions."""
        try:
            is_multi_select = flags.get("multi_select", False)

            for obj in objects:
                if self.check_conditions(obj, conditions):
                    temp_array = []  # Temporary array to store all values

                    for sub_key, sub_path in json_paths.items():
                        field_name = sub_path.replace("$.", "", 1).split('.')[-1]

                        if isinstance(obj, dict) and field_name in obj:
                            value = self.local_store.get_value(sub_key)

                            # If multi_select is enabled, collect values in temp_array
                            if is_multi_select and isinstance(obj[field_name],list):
                                temp_array.append(value)
                            elif isinstance(obj[field_name],list):
                                obj[field_name] = [value]
                            else:
                                obj[field_name] = value  # Directly update for non-multi-select

                    # If multi_select, update obj[field_name] with all collected values
                    if is_multi_select and temp_array:
                        obj[field_name] = temp_array

        except KeyError as e:
            print(f"KeyError in _update_nested_objects: {e}")
        except Exception as e:
            print(f"Unexpected error in _update_nested_objects: {e}")

            
    def load_dependencies(self):
        """Load dependencies from JSON file."""
        dependencies_file= self.local_store.get_value("merged_config_path")
        if os.path.exists(dependencies_file):
            with open(dependencies_file, "r") as file:
                return json.load(file)
        return {}
    
    def check_conditions(self, obj, conditions):
        """Checks if all conditions are satisfied in the given object."""
        if not conditions:
            return True  # No conditions to check, assume valid
        for condition in conditions:
            flag_path_cleaned = condition["flag_path"].replace("$.", "", 1)
            expected_values = condition.get("expected_values", [])
            
            # Get the field name (after the last dot)
            field_name = flag_path_cleaned.split('.')[-1]
            
            # Check if the object has the field
            if isinstance(obj, dict) and field_name in obj:
                flag_value = obj[field_name]
                if flag_value not in expected_values:
                    return False  # Condition failed
            else:
                return False  # Missing required field
                
        return True  # All conditions passed

    def get_first_valid_value(self, json_data, json_paths):
        """Return the first valid value from multiple JSON paths."""
        for path in json_paths:
            value = self.get_json_value(json_data, path)
            if value is not None:
                return value
        return None

    def get_json_value(self, json_data, json_path):
        """Fetch a value from JSON using dot notation."""
        keys = json_path.lstrip("$.").split(".")
        value = json_data
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return None