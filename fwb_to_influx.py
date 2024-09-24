import requests
import os
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

# Define the URLs and headers
url_policy_status = "https://fwb.orked-tech.demo/api/v2.0/policy/policystatus"  #<-- CHANGE_HERE
url_system_status = "https://fwb.orked-tech.demo/api/v2.0/system/status.monitor"  #<-- CHANGE_HERE
headers = {
    "Authorization": "eyJ1c2VybmFtZSI6ImFkbWluIiwicGFzc3dvcmQiOiJhZG1pbiIsInZkb20iOiJyb290In0K", #<-- CHANGE_HERE
    "Accept": "application/json"
}

# Define the path to the CA certificate file #place CA cert into the same directory
ca_cert_path = os.path.join(os.path.dirname(__file__), "myCA.pem") #<-- CHANGE_HERE

# InfluxDB details #install influxdbv2 
influxdb_url = "http://influxdb.orked-tech.demo:8086" #<-- CHANGE_HERE
token = "4KyZMUTc6VASAISdFhqtmhb8FXfDhhApBnh2wl81SEnULGvmUcmwvXKmxB8ZhGzu1PHHck3VDPH7g7Piv0mR8g==" #<-- CHANGE_HERE
org = "my_api" #<-- CHANGE_HERE
bucket = "fwb_prod" #<-- CHANGE_HERE

# Initialize InfluxDB client
client = InfluxDBClient(url=influxdb_url, token=token)
write_api = client.write_api(write_options=SYNCHRONOUS)


# Function to send GET request and return JSON response
def get_json_response(url, headers, ca_cert_path):
    response = requests.get(url, headers=headers, verify=ca_cert_path)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to retrieve data from {url}. Status code: {response.status_code}")
        return None


# Get policy status
policy_status_data = get_json_response(url_policy_status, headers, ca_cert_path)
policy_status_map = {}

if policy_status_data:
    policy_results = policy_status_data.get("results", [])
    for policy in policy_results:
        policy_name = policy.get("_id", "N/A")
        sessionCount = policy.get("sessionCount", "N/A")
        connCntPerSec = policy.get("connCntPerSec", "N/A")
        policy_status_map[policy_name] = {
            "sessionCount": sessionCount,
            "connCntPerSec": connCntPerSec
        }

# Get system status
system_status_data = get_json_response(url_system_status, headers, ca_cert_path)
if system_status_data:
    system_results = system_status_data.get("results", {})
    # Extract global values
    global_values = {
        "global_cpu": system_results.get("cpu", "N/A"),
        "global_memory": system_results.get("memory", "N/A"),
        "global_log_disk": system_results.get("log_disk", "N/A"),
        "global_tcp_concurrent_connection": system_results.get("tcp_concurrent_connection", "N/A"),
        "global_tcp_connection_per_second": system_results.get("tcp_connection_per_second", "N/A"),
        "global_throughput_in": system_results.get("throughput_in", "N/A"),
        "global_throughput_out": system_results.get("throughput_out", "N/A"),
        "global_threat": system_results.get("threat", "N/A"),
    }
    print("global:")
    for key, value in global_values.items():
        print(f"{key}: {value}")

    # Write global values to InfluxDB
    point = Point("system_status").tag("type", "global")
    for key, value in global_values.items():
        point = point.field(key, value)
    write_api.write(bucket=bucket, org=org, record=point)

    # Extract per policy values and write to InfluxDB
    for policy_key in system_results:
        if policy_key.startswith("policy"):
            policies = system_results[policy_key]
            for policy in policies:
                name = policy.get("name", "N/A")
                info = policy.get("info", {})
                policy_values = {
                    f"{name}_tcp_concurrent_connection": info.get("tcp_concurrent_connection", "N/A"),
                    f"{name}_tcp_connection_per_second": info.get("tcp_connection_per_second", "N/A"),
                    f"{name}_throughput_in": info.get("throughput_in", "N/A"),
                    f"{name}_throughput_out": info.get("throughput_out", "N/A"),
                }
                print(f"name: {name}")
                for key, value in policy_values.items():
                    print(f"{key}: {value}")

                # Include sessionCount and connCntPerSec from the policy status
                if name in policy_status_map:
                    sessionCount = policy_status_map[name]["sessionCount"]
                    connCntPerSec = policy_status_map[name]["connCntPerSec"]
                    print(f"{name}_sessionCount: {sessionCount}")
                    print(f"{name}_connCntPerSec: {connCntPerSec}")
                    policy_values[f"{name}_sessionCount"] = sessionCount
                    policy_values[f"{name}_connCntPerSec"] = connCntPerSec
                else:
                    print("sessionCount: N/A")
                    print("connCntPerSec: N/A")

                # Write policy values to InfluxDB
                point = Point("policy_status").tag("policy_name", name)
                for key, value in policy_values.items():
                    point = point.field(key, value)
                write_api.write(bucket=bucket, org=org, record=point)
else:
    print("Failed to retrieve system status data.")
