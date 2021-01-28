import requests

from chalicelib.settings import SENSORS_AFRICA_API, SENSORS_AFRICA_AUTH_TOKEN

def post_sensor_data(data, node_uid, pin):
    response = requests.post(f"{SENSORS_AFRICA_API}/v1/push-sensor-data/",
    json=data,
    headers={
        "Authorization": f"Token {SENSORS_AFRICA_AUTH_TOKEN}",
        "SENSOR": str(node_uid),
        "PIN": pin
        }
    )
    if response.ok:
        return response.json()
    raise Exception(response.text)
    
def get_sensors_africa_nodes():
    response = requests.get(f"{SENSORS_AFRICA_API}/v1/node/",
    headers={"Authorization": f"Token {SENSORS_AFRICA_AUTH_TOKEN}"})
    if response.ok:
        return response.json()["results"]
    return []
