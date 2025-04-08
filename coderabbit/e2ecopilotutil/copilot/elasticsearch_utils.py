import json
import avxtflib
import time


def _query_elasticsearch(tf: avxtflib.AvxTfLib, index_name, json_data):
    """
    Queries the specified Elasticsearch index with a JSON payload.
    
    Retrieves a Copilot virtual machine instance from the provided interface and builds a GET request that embeds the target index and JSON query data. If the VM is available, the command is executed and its JSON output is parsed and returned.
    
    Args:
        index_name: The name of the Elasticsearch index to query.
        json_data: A dictionary containing the query parameters.
    
    Returns:
        The parsed JSON result from Elasticsearch, or None if the Copilot VM is unavailable.
    """
    copilot_vm = tf.copilot()
    if copilot_vm is not None:
        cmd = (
            "sudo /opt/copilot/bin/curles GET /"
            + index_name
            + "/_search?pretty -d '"
            + json.dumps(json_data)
            + "'"
        )
        _, stdout = copilot_vm.run(cmd)
        result_output_json = json.loads(stdout)
        return result_output_json


def check_index_elasticsearch(tf: avxtflib.AvxTfLib, index_name):
    """
    Checks if the specified Elasticsearch index exists.
    
    This function retrieves a Copilot virtual machine from the provided avxtflib instance to run a command that lists
    all Elasticsearch indices. It then checks the command output for the given index name, retrying up to 60 times with a
    1-second interval between attempts. If the index is detected, it returns True; otherwise, it returns False.
        
    Parameters:
        index_name (str): The name of the Elasticsearch index to check.
        
    Returns:
        bool: True if the index is found; otherwise, False.
    """
    copilot_vm = tf.copilot()
    if copilot_vm is not None:
        cmd = "sudo /opt/copilot/bin/curles GET /_cat/indices | grep " + index_name
        for _ in range(60):
            _, stdout = copilot_vm.run(cmd)
            if index_name in stdout:
                return True
            time.sleep(1)
    return False


def _query_elasticsearch_perfmon(tf: avxtflib.AvxTfLib, index_name, gw_name, timestamp):
    """
    Queries Elasticsearch for performance monitoring data.
    
    Constructs a JSON query to filter performance monitoring records by gateway name 
    and timestamp, then executes the query on the specified Elasticsearch index via 
    the Copilot virtual machine. If the Copilot VM is unavailable, the function 
    returns None.
    
    Args:
        index_name: Name of the Elasticsearch index to query.
        gw_name: Gateway name used to filter the results.
        timestamp: Timestamp for filtering records; it is converted to a string.
    
    Returns:
        The JSON-parsed result from the Elasticsearch query, or None if no Copilot VM is available.
    """
    copilot_vm = tf.copilot()
    if copilot_vm is not None:
        json_data = {
            "query": {
                "bool": {
                    "filter": [
                        {"term": {"gatewayName.keyword": gw_name}},
                        {"term": {"@timestamp": str(timestamp)}},
                    ]
                }
            }
        }
        return _query_elasticsearch(tf, index_name, json_data)
