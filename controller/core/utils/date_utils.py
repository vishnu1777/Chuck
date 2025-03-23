import datetime
import re
from datetime import timedelta



def detect_date_format(date_str):
    """Detects the format of a date string and returns its datetime format."""
    date_formats = [
        ("%d %B %Y", r"\b\d{2} [A-Za-z]+ \d{4}\b"),  # 20 March 2024
        ("%d-%m-%Y", r"\b\d{2}-\d{2}-\d{4}\b"),      # 20-03-2024
        ("%d/%m/%Y", r"\b\d{2}/\d{2}/\d{4}\b"),      # 20/03/2024
        ("%B %d, %Y", r"\b[A-Za-z]+ \d{2}, \d{4}\b") # March 20, 2024
    ]
    
    for fmt, pattern in date_formats:
        if re.fullmatch(pattern, date_str):
            return fmt
    return None  

def replace_dates(payload, target_date):
    """
    Recursively replaces dates in a JSON payload while keeping the original format.
    
    :param payload: JSON dictionary or list
    :param target_date: The
     new date (YYYY-MM-DD) to replace old dates.
    """
    if not target_date:
        return payload
    if isinstance(payload, dict):
        return {k: replace_dates(v, target_date) for k, v in payload.items()}
    elif isinstance(payload, list):
        return [replace_dates(item, target_date) for item in payload]
    elif isinstance(payload, str):  
        detected_format = detect_date_format(payload)  # Detect the date format
        if detected_format:
            formatted_date = datetime.strptime(target_date, "%Y-%m-%d").strftime(detected_format)
            return formatted_date  # Replace with target date in the detected format
    return payload  # Return unchanged if not a date


