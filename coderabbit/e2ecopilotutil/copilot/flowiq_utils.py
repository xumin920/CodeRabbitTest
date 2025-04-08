import json
import avxtflib
import time
import logging
from datetime import date, datetime, timedelta

API_FLOWIQ_RECORDS_PATH = "/api/flowiq/records"


def get_flowiq_for_last_xmins(tf, xmins):
    """
    Fetch flowiq records from the Copilot API within the last x minutes.
    
    This function asserts that the provided context contains an initialized Copilot API,
    then constructs a payload with a date range spanning from the current time minus the
    specified minutes until now. It sends a POST request to the API endpoint and returns
    the parsed JSON response as a list of dictionaries representing flowiq records.
    
    Args:
        xmins (int): The number of minutes in the past for which to retrieve records.
    
    Returns:
        list: A list of dictionaries containing flowiq record data.
    
    Raises:
        AssertionError: If the provided context lacks an initialized Copilot API.
    """
    assert tf.copilot_api is not None, "Missing tf.copilot_api in terraform!"
    payload = {
        "query_string": "",
        "date_range": {"time_zone": "00:00", "gte": f"now-{xmins}m/m", "lte": "now"},
    }
    response = tf.copilot_api.post(API_FLOWIQ_RECORDS_PATH, payload)
    result = json.loads(response.text)
    return result


def get_flowiq_between_utc_datetimes(
    tf, earliest_datetime, latest_datetime, query_string=""
):
    """
    Retrieves flowiq records from the Copilot API between two UTC datetime values.
    
    This function posts a payload with a query string and a date range—formatted from the provided
    earliest and latest datetime values—to retrieve flowiq records. It returns the matching records as a
    list of dictionaries.
    
    Args:
        earliest_datetime (datetime): The start of the date range.
        latest_datetime (datetime): The end of the date range.
        query_string (str, optional): Additional filter expression for flow records.
            Defaults to an empty string.
    
    Returns:
        list[dict]: A list of flowiq records matching the specified criteria.
    """
    assert tf.copilot_api is not None, "Missing tf.copilot_api in terraform!"
    gte = earliest_datetime.strftime("%Y-%m-%dT%H:%M:%S.000Z")
    lte = latest_datetime.strftime("%Y-%m-%dT%H:%M:%S.000Z")
    payload = {
        "query_string": query_string,
        "date_range": {"gte": gte, "lte": lte},
    }
    response = tf.copilot_api.post(API_FLOWIQ_RECORDS_PATH, payload)
    result = json.loads(response.text)
    return result
