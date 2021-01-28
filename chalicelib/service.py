import boto3
import csv
import pickle
import requests

from chalicelib.sensorafrica import (
    get_sensors_africa_nodes,
    post_sensor_data, )

from chalicelib.settings import S3_BUCKET_NAME, S3_OBJECT_KEY

from datetime import datetime as dt

def get_nodes_sensor_data(node_uid):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36",
        }
    response = requests.get(
        url="http://sensors.opendata.durban/CS/download/{}".format(node_uid), headers=headers)
    if not response.ok:
        raise Exception(response.reason)
    return response.content.decode('utf-8')


def run(app):
    nodes = get_sensors_africa_nodes()
    nodes = [ node.get("uid") for node in nodes ]

    s3client = boto3.client("s3", region_name="eu-west-1")
    try:
        response = s3client.get_object(Bucket=S3_BUCKET_NAME, Key=S3_OBJECT_KEY)
        body = response['Body'].read()
        node_last_entry_dict = pickle.loads(body)
    except:
        node_last_entry_dict = dict()

    for node in nodes:
        if not node in node_last_entry_dict:
                node_last_entry_dict[node] = "2000-01-01"

        sensor_data = get_nodes_sensor_data(node)

        data_cr = csv.reader(sensor_data.splitlines(), delimiter=',')
        data_list = list(data_cr)
        for row in data_list[1:]:
            if dt.strptime(row[0], "%Y-%m-%d") > dt.strptime(node_last_entry_dict[node], "%Y-%m-%d"):
                timestamp = "{}T{}".format(row[0], row[4])
                sensor_data_values = [
                    {
                        "value": row[2],
                        "value_type": "P2"
                    },
                    {
                        "value": row[3],
                        "value_type": "P1"
                    }
                ]

                post_sensor_data({ 
                            "sensordatavalues": sensor_data_values, 
                            "timestamp": timestamp
                            }, node, "-")

                #update pickle variable               
                node_last_entry_dict[node] = row[0]
                s3client.put_object(Body=pickle.dumps(node_last_entry_dict), Bucket=S3_BUCKET_NAME, Key=S3_OBJECT_KEY)
        
            


