import csv
import requests
import json
import time

USERNAME = 'zhaw-ki-2048'
PASSWORD = '3T33TrXtnzwuvaLVxofB'

elastic_error_counter = 0
elastic_without_errors = True

def log(file_writer, line):
    file_writer.writerow(line)

def elastic_post(content):
    global elastic_without_errors, elastic_error_counter
    
    if elastic_without_errors:
        url = 'http://elasticsearch.cle.squibble.me/zhaw/ki-2048'
        response = requests.post(url,
                                auth=requests.auth.HTTPBasicAuth(USERNAME, PASSWORD),
                                json=content)

        if response.status_code != 201:
            print(response) # show in console, if elastic does not work
            elastic_error_counter += 1

        if elastic_error_counter > 10:
            elastic_without_errors = False    
