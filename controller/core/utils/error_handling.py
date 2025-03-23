def handle_response_status(response, error_occurred):
    """Ensure the response includes a status flag based on error occurrence."""
    if error_occurred or not response:
        return {"status": "failed"}  # If error occurs, return failed status
    else:
        if isinstance(response, dict):  # Ensure it's a dict before modifying
            response["status"] = "success"
        return response
def set_status_failed(response):
    """Ensure the response includes a status flag based on error occurrence."""
    response["status"] = "failed"