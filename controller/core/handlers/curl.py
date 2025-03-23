import re
import json
import os
from urllib.parse import urlparse,parse_qs
from utils.file_utils import *

class CURL:
    """
    A class for extracting and processing components from cURL commands.
    This class provides functionality to parse cURL commands, extract headers,
    URLs, payloads, and query parameters, and save them to appropriate files.
    """
    def extract_query_params(self,curl_command):
        url_match = re.search(r"curl --location '([^']+)'", curl_command)
        
        if url_match:
            url = url_match.group(1)
            parsed_url = urlparse(url)
            
            # If no query params, return an empty dictionary
            if not parsed_url.query:
                return {}
            
            return {k: v[0] if len(v) == 1 else v for k, v in parse_qs(parsed_url.query).items()}
        return {}
    
    def generateCurl(self,responseType,requestUrl,headers,payload,max_tries=3):
        headers_str = ' '.join(['-H "{}: {}"'.format(k, v) for k, v in headers.items()])
        data_str = json.dumps(payload)
        data_str = data_str.replace('\\', '')
        if responseType in ("post","put"):
            curl_command = f"curl --location '{requestUrl}' {headers_str} --data '{data_str}'"
        else:
            curl_command = f"curl --location '{requestUrl}' {headers_str}" 
        return curl_command

    def extract_headers(self, curl_command):
        """
        Extract headers from a cURL command.
        
        Args:
            curl_command (str): The cURL command to parse
            
        Returns:
            dict: A dictionary of header key-value pairs
        """
        headers = {}

        # Remove backslashes before processing
        curl_command = curl_command.replace("\\", "")

        # Extract headers using regex, handling both `--header` and `-H`
        header_matches = re.findall(r'-(?:H|header)\s+[\'"]?([^\'"]+)[\'"]?', curl_command)

        for header in header_matches:
            if ":" in header:
                key, value = header.split(":", 1)  # Split only at the first `:`
                headers[key.strip()] = value.strip()
            else:
                headers[header.strip()] = ""  # Handle cases where value might be missing

        return headers

    def extract_payload(self, curl_command):
        """
        Extracts the payload from a cURL command, handling both --data and --data-raw.

        Args:
            curl_command (str): The cURL command to parse.

        Returns:
            dict or str or None: Parsed JSON if valid, otherwise raw string, or None if not found.
        """
        # Match both --data and --data-raw with either single or double quotes
        match = re.search(r"--data(?:-raw)?\s+'([^']+)'|--data(?:-raw)?\s+\"([^\"]+)\"", curl_command)
        
        if match:
            payload_str = match.group(1) or match.group(2)  # Extract payload string
            payload_str = payload_str.strip("\"")  # Remove extra enclosing quotes
            
            try:
                return json.loads(payload_str)  # Convert to dict if it's valid JSON
            except json.JSONDecodeError:
                return payload_str  # Return raw string if it's not valid JSON
        
        return None  # No payload found

    def extract_url(self,curl_command):
        url_match = re.search(r"'(http[s]?://.*?)'", curl_command)
        url = url_match.group(1) if url_match else ''
        parsed_url = urlparse(url)
        # Get the base URL without query parameters
        base_url = parsed_url.scheme + "://" + parsed_url.netloc + parsed_url.path
        return base_url
    
    def extract_curl_components(self, curl_command):
        """
        Extract all components from a cURL command.
        
        Parses a cURL command to extract the URL, headers, payload data,
        and query parameters.
        
        Args:
            curl_command (str): The cURL command to parse
            
        Returns:
            tuple: (base_url, headers, payload, query_params)
        """
        # Extract URL,payload,headers,query_params
        base_url = self.extract_url(curl_command)
        headers = self.extract_headers(curl_command)
        payloads = self.extract_payload(curl_command)
        query_params = self.extract_query_params(curl_command)
       
        return base_url, headers, payloads, query_params
    
    def save_to_file(self, data, filename):
        """
        Save data to a file.
        
        Args:
            data (str): Data to save
            filename (str): Path to the output file
        """
        # Ensure the directory exists
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        with open(filename, 'w', encoding="utf-8") as file:
            file.write(data)
    
    def save_headers_to_json(self, headers, folder_path):
        """
        Save headers to a JSON file.
        
        Args:
            headers (dict): Headers to save
            folder_path (str): Path to the folder where headers.json will be saved
        """
        # Ensure the directory exists
        os.makedirs(folder_path, exist_ok=True)
        
        header_file = os.path.join(folder_path, "headers.json")
        with open(header_file, "w", encoding="utf-8") as f:
            json.dump(headers, f, indent=4)
    
    def save_payload_to_json(self, payload, folder_path):
        """
        Save payload to a JSON file.
        
        Args:
            payload (dict): Payload data to save
            folder_path (str): Path to the folder where payload.json will be saved
        """
        # Ensure the directory exists
        os.makedirs(folder_path, exist_ok=True)
        
        payload_file = os.path.join(folder_path, "payload.json")
        with open(payload_file, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=4)
    
    def save_query_to_json(self, query, folder_path):
        """
        Save query parameters to a JSON file.
        
        Args:
            query (dict): Query parameters to save
            folder_path (str): Path to the folder where query.json will be saved
        """
        # Ensure the directory exists
        os.makedirs(folder_path, exist_ok=True)
        
        query_file = os.path.join(folder_path, "query.json")
        with open(query_file, "w", encoding="utf-8") as f:
            json.dump(query, f, indent=4)
    
    def save_url_to_txt(self, url, folder_path):
        """
        Save URL to a text file.
        
        Args:
            url (str): URL to save
            folder_path (str): Path to the folder where url.txt will be saved
        """
        # Ensure the directory exists
        os.makedirs(folder_path, exist_ok=True)
        
        url_file = os.path.join(folder_path, "url.txt")
        with open(url_file, "w", encoding="utf-8") as f:
            f.write(url)

            
    def saveAllFiles(self,headers,payload,query_params,url):
        """Save URL, headers, payload, and query parameters to specific folders."""
        controller_path = get_file_root_path()
        self.save_headers_to_json(headers, os.path.join(controller_path,"tempStorage","headers"))
        self.save_payload_to_json(payload, os.path.join(controller_path,"tempStorage", "payloads"))
        self.save_query_to_json(query_params, os.path.join(controller_path,"tempStorage", "query"))
        self.save_url_to_txt(url, os.path.join(controller_path,"tempStorage", "url"))