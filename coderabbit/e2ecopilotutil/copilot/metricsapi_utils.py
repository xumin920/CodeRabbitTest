import json
import avxtflib
import time
import logging

logger = logging.getLogger(__name__)


def unlock_metricsAPI(tf) -> bool:
    """
    Enable Network Insights API, internally metricsAPI, a Copilot Add-on Feature
    :return: True or False, response.ok
    """
    path = "/api/features/metricsApi/lock"
    payload = {"lock": "false"}
    response = tf.copilot_api.put(path, payload)
    return response.ok


def lock_metricsAPI(tf) -> bool:
    """
    Disable Network Insights API, internally metricsAPI, a Copilot Add-on Feature
    :return: True or False, response.ok
    """
    path = "/api/features/metricsApi/lock"
    payload = {"lock": "true"}
    response = tf.copilot_api.put(path, payload)
    return response.ok


def _set_metricsAPI_key(tf, key) -> bool:
    """
    Set the Network Insights (metrics) API to key.
    :param key: the metricsAPI key to set
    :return: True or False, response.ok
    """
    path = "/api/settings/configuration/metricsApi"
    payload = {"key": key}
    response = tf.copilot_api.post(path, payload)
    return response.ok


def reset_metricsAPI_key(tf) -> str:
    """
    Generate and set a Network Insights API (metricsAPI) key AND return it.
    :return: a string representation the new key
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
    From the controller, because it is already in the copilot security group, curl the metricsAPI
    :param key: string, metricsAPI key
    :param timeout: int, seconds
    :return: stdout of the metricsAPI curl
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
