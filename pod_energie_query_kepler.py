import requests

PROMETHEUS_URL = "http://localhost:9090"
TARGET_POD_NAME = "python-example-59d88d5ddc-vb24s"


def query_energy(pod_name: str): # last 5 minutes
    query = f'increase(kepler_container_joules_total{{pod_name="{pod_name}"}}[5m])'
    url = f"{PROMETHEUS_URL}/api/v1/query"
    response = requests.get(url, params={"query": query})
    result = response.json()
    data = result["data"]["result"]
    print(data)
    joules = float(data[0]["value"][1])
    return round(joules, 2)

#print(query_energy(TARGET_POD_NAME))
