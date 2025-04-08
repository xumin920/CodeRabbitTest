import json
import avxtflib
import time


def _query_elasticsearch(tf: avxtflib.AvxTfLib, index_name, json_data):
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
