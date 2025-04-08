import json
import avxtflib
import time
import logging
from datetime import date, datetime, timedelta

API_FLOWIQ_RECORDS_PATH = "/api/flowiq/records"


def get_flowiq_for_last_xmins(tf, xmins):
    """
    Returns a list of flowiq records as dicts from Copilot within the last x minutes,
    netflow.gw_name (host gw) matching the gwname (if provided),
    Uses the 'post' copilot API.
    :param tf:
    :param xmins: int, how many minutes in the past to filter on
    :return: list of flow iq records as dicts from last xmins
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
    Returns a list of flowiq records as dicts from Copilot
    Uses the 'post' copilot API.
    :param tf:
    :param gwname: target gateway host name to filter on
    :param earliest_datetime: datetime object
    :param latest_datetime: datetime object
    :param query_string: string used to further filter flow records
                            '(geoip.as_org:"YAHOO-GQ1")'
    :return: list of flow iq records as dicts matching the provided filter values
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
