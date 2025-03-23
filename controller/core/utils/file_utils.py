import json
import os
from pathlib import Path
from copy import deepcopy

import os

def delete_file(file_path):
    """
    Delete a file given its path.
    
    Args:
        file_path (str): The path to the file that needs to be deleted
        
    Returns:
        bool: True if the file was successfully deleted, False otherwise
    """
    try:
        # Check if the file exists
        if os.path.exists(file_path):
            # Delete the file
            os.remove(file_path)
            return True
        else:
            print(f"The file {file_path} does not exist.")
            return False
    except Exception as e:
        print(f"An error occurred while deleting the file: {e}")
        return False

def read_json_file(file_path):
    """Reads and returns the content of a JSON file."""
    if not os.path.exists(file_path):
        print(f"Warning: {file_path} not found.")
        return {}
    
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)
    except json.JSONDecodeError as e:
        print(f"Error reading {file_path}: {e}")
        return {}

def get_config_path():
    """Dynamically finds the 'configs/config.json' path from any script location."""
    current_path = Path(__file__).resolve()
    
    # Search for the 'configs' directory two levels up
    chainapi_root = current_path.parents[2]  # Go 2 levels up
    config_path = chainapi_root / "configs" / "config.json"

    if not config_path.exists():
        raise FileNotFoundError(f"⚠️ Config file not found: {config_path}")
    return config_path



   
def load_json(file_path):
    """Loads a JSON file"""
    try:
        with open(file_path, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading JSON file {file_path}: {e}")
        return {}
    

def get_folder_root_path():
    """function returns files parent/parent (grand parent) folder"""
    current_file_path = os.path.abspath(__file__)
    # Move two levels up
    root_path = os.path.abspath(os.path.join(current_file_path, '..', '..','..','..'))
    return root_path

def write_file(file_path,content):
    with open(file_path, 'w') as f:
        json.dump(content, f, indent=4)

def get_file_root_path():
    """function returns files parent folder"""
    current_file_path = os.path.abspath(__file__)
    # Move two levels up
    root_path = os.path.abspath(os.path.join(current_file_path, '..', '..'))
    return root_path

def merge_configs(parent_config, child_config):
    """
    Merge two configuration dictionaries, with child values overriding parent values
    where keys overlap, and preserving unique keys from both configurations.
    """
    # Create a deep copy of the parent config to avoid modifying the original
    merged_config = deepcopy(parent_config)
    
    # Recursively merge the child config into the merged config
    for key, value in child_config.items():
        if key in merged_config and isinstance(merged_config[key], dict) and isinstance(value, dict):
            # If both values are dictionaries, merge them recursively
            merged_config[key] = merge_configs(merged_config[key], value)
        else:
            # Otherwise, child value overrides parent value
            merged_config[key] = deepcopy(value)
    
    return merged_config

def cleanup_merged_config(file_path):
    """Helper function to clean up the merged config file."""
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
        except Exception as e:
            print(f"⚠️ Warning: Failed to delete merged config file: {str(e)}")
def create_and_merge_configs(parent_path,child_path,merge_file_path):
    parent_config = load_json(parent_path)
    child_config = load_json(child_path)
    merged_data =merge_configs(parent_config, child_config)
    write_file(merge_file_path,merged_data)

