import requests
from utils.error_handling import handle_response_status

def get_url_response(method, url, headers=None, query_params=None, payload=None):
    """Send HTTP requests dynamically based on the provided method and handle errors gracefully."""
    try:
        method = method.lower()
        response = None
        if method == "post":
            response = requests.post(url, headers=headers, json=payload, params=query_params)
        elif method == "get":
            response = requests.get(url, headers=headers, params=query_params)
        elif method == "delete":
            response = requests.delete(url, headers=headers, params=query_params)
        elif method == "patch":
            response = requests.patch(url, headers=headers, json=payload, params=query_params)
        elif method == "put":
            response = requests.put(url, headers=headers, json=payload, params=query_params)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
        if response.status_code != 200:  # Check if status code is not 200
            print(f"❌ Error: Received status code {response.status_code}")
            return handle_response_status({}, error_occurred=True), response.elapsed
        response_json = response.json()  # Extract JSON response
        return handle_response_status(response_json, error_occurred=False), response.elapsed

    except requests.exceptions.Timeout:
        print("Request timed out.")
        return handle_response_status({}, error_occurred=True), None

    except requests.exceptions.RequestException as e:
        print("Error fetching URL:", e)
        return handle_response_status({}, error_occurred=True), None
