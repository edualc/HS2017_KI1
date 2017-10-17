import csv
import requests
import json
import time

USERNAME = 'zhaw-ki-2048'
PASSWORD = '3T33TrXtnzwuvaLVxofB'

def log(file_writer, line):
    file_writer.writerow(line)

def elastic_post(content):
    url = 'http://elasticsearch.cle.squibble.me/zhaw/ki-2048'
    response = requests.post(url,
                            auth=requests.auth.HTTPBasicAuth(USERNAME, PASSWORD),
                            json=content)
    # print(response)
    # time.sleep(5)
