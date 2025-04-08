import json
import avxtflib
import time
import logging

logger = logging.getLogger(__name__)


def unlock_metricsAPI(tf) -> bool:
    """
    Enables the Network Insights API by unlocking the metrics feature.
    
    Sends a PUT request to the '/api/features/metricsApi/lock' endpoint with a payload that sets the lock to false.
    Returns True if the API call is successful, otherwise False.
    """
    path = "/api/features/metricsApi/lock"
    payload = {"lock": "false"}
    response = tf.copilot_api.put(path, payload)
    return response.ok


def lock_metricsAPI(tf) -> bool:
    """
    Disables the Network Insights metrics API.
    
    Sends a PUT request to the copilot API's metrics API lock endpoint with a payload that
    enables the lock, effectively disabling the API. Returns True if the operation succeeds,
    or False otherwise.
    
    Returns:
        bool: True if the API call was successful, False otherwise.
    """
    path = "/api/features/metricsApi/lock"
    payload = {"lock": "true"}
    response = tf.copilot_api.put(path, payload)
    return response.ok


def _set_metricsAPI_key(tf, key) -> bool:
    """
    Set the metrics API key in the configuration.
    
    This function updates the metrics API key by posting a payload to the
    '/api/settings/configuration/metricsApi' endpoint. It returns True if the
    operation is successful.
    
    Args:
        key: The new metrics API key to be set.
    
    Returns:
        bool: True if the key was successfully updated, otherwise False.
    """
    path = "/api/settings/configuration/metricsApi"
    payload = {"key": key}
    response = tf.copilot_api.post(path, payload)
    return response.ok


def reset_metricsAPI_key(tf) -> str:
    """
    Generates and sets a new metrics API key.
    
    Creates a base64-encoded key from 30 random bytes with URL-safe modifications,
    applies it via an API call, and returns the new key as a string. An
    AssertionError is raised if setting the key fails.
    """
    import os
    import base64

    # this formula is based on resetMetricsApiKey in copilot/apps.ui/src/util/api/settingsConfiguration.api.ts
    key = (
        base64.b64encode(os.urandom(30))
        .decode("utf-8")
        .replace("/", "_")
        .replace("+", "-")
    )
    assert _set_metricsAPI_key(tf, key)
    return str(key)


def curl_metrics_api(tf, key, gwname, timeout=300):
    """
    Execute a curl command to poll the metrics API for a specified gateway.
    
    This function builds a curl command to query the metrics API endpoint using the provided
    authorization key. It polls every 10 seconds until the response contains the specified gateway
    name or the timeout is reached. A warning is logged if the timeout is 60 seconds or less, and an
    AssertionError is raised if the gateway name is not detected within the given timeout.
    
    Args:
        key (str): The metrics API authorization key.
        gwname (str): The name of the gateway to search for in the API response.
        timeout (int, optional): The maximum number of seconds to wait for the gateway data (default 300).
    
    Returns:
        str: The output from the metrics API containing the gateway data.
    
    Raises:
        AssertionError: If the metrics API does not report stats for the specified gateway within the timeout.
    """
    if timeout <= 60:
        logger.warning(
            "Gateway statistics will take at least 60s to be reported, suggest increasing the timeout."
        )
    ctrl = tf.controller()
    cp = tf.copilot()
    cmd = f"curl -k -X 'GET' 'https://{cp.public_ip}/metrics-api/v1/gateways?format=json' -H 'Authorization: Bearer {key}' | jq"
    stopTime = time.time() + timeout
    logger.info(
        f"Waiting up to {timeout} seconds for {gwname} to appear in MetricsAPI output..."
    )
    out = None
    while time.time() < stopTime:
        _, out = ctrl.run(cmd)
        if gwname in out:
            break
        else:
            logger.debug(out)
            time.sleep(10)
    else:
        assert False, f"MetricsAPI failed to report stats for {gwname}!"
    logger.debug(out)
    return out
