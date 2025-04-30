from entry_parser import *
from urllib.parse import unquote, urlparse, urlunparse
import json

# VARIABLES
__NETWORK__ = 'localhost:8001'
bruno_env = []
bruno_root = {
        "request": {
            "vars": {
                "res": [
                {
                    "name": "_Header_Content",
                    "value": "\"<?xml version=\\\"1.0\\\" encoding=\\\"iso-8859-1\\\"?>\"",
                    "enabled": True,
                    "local": False,
                    "uid": "a26Qsn30kwePzOaOSr6Ba"
                }
                ]
            }
        }
    }
bruno_config = {
        "version": "1",
        "name": "TOM - ",
        "type": "collection",
        "ignore": [
        "node_modules",
        ".git"
        ],
        "size": 0.019819259643554688,
        "filesCount": 38
    }
bruno_json = {
        "name": "--",
        "version": "1", 
        # "items" : [entry.to_dict for entry in log.entries]
        "environments": bruno_env,
        "root": bruno_root,
        "brunoConfig": bruno_config
    }

def UpdateSetName(test_set_data):
    bruno_json['name'] = test_set_data['folder name']
    bruno_config['name'] = test_set_data['folder name']

# FUNCTIONS
def build(log : Log, selected_set):
    try :
        print(f"Selected set: {selected_set}")
        UpdateSetName(selected_set['data'])
    except Exception as e:
        print(f"Error updating set name: {e}")
        return None
    bruno_json['items'] = [entry.get_bruno_data() for entry in log.entries if entry.get_bruno_data() is not None]
    update_seq(bruno_json["items"])
    return bruno_json
    
def update_seq(item_list): # update name and seq
    no_postData_ctr = nobody_ctr = body_ctr = 0 

    for idx,item in enumerate(item_list):
        if item["metadata"]["postBody"] : 
            body_ctr += 1
            item["name"] = "TFIXRTOM-" +str(body_ctr)+ item["name"] 
            item["filename"] = "TFIXRTOM-" + str(body_ctr)+item["filename"] 
        
        else :
            nobody_ctr += 1
            item["name"] = "[Technical_test]-"  + str(nobody_ctr) + item["name"] 
            item["filename"] = "[Technical_test]-" + str(nobody_ctr) + item["filename"] 

        item["seq"] += idx + 1
        item["name"] = item["name"] 
        item["filename"] = item["filename"]  + ".bru"
        # update netloc
        item["request"]["url"] = parse_url(item["request"]["url"],__NETWORK__)

        #delete metadata
        item.pop("metadata",None)
    return item_list

def parse_url(original_url,new_netloc):
    try:
        parsed_url = urlparse(original_url)
        return urlunparse(parsed_url._replace(netloc=new_netloc))
    except Exception:
        return original_url

def write_json_file(filepath, item_to_write):
     # Write filtered entries to a new JSON file
    with open(filepath, 'w', encoding='utf-8') as file:
        json.dump(item_to_write, file, ensure_ascii=False, indent=4)




