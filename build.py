import json
from entry_parser import *
from bruno_builder import *
import os

# MAIN
migration_dict = {
    1:{
        "name": "User Connection",
        "data": {
            "har_file": "HAR_files/1-User_Connection.har",
            "dest_file": "Import/1-User_Connection.json",
            "folder name" : "1 - User Connection"
        }
    },
    2:{
        "name": "User Management",
        "data": {
            "har_file": "HAR_files/2-User_Management.har",
            "dest_file": "Import/2-User_Management.json",
            "folder name" : "2 - User Management"
        }
    },
    3:{
        "name": "Account Management",
        "data": {
            "har_file": "HAR_files/3-Account_Management.har",
            "dest_file": "Import/3-Account_Management.json",
            "folder name" : "3 - Account Management"
        }
    },
    4:{
        "name": "Cash Transfer",
        "data": {
            "har_file": "HAR_files/7-Cash_Transfer.har",
            "dest_file": "Import/7-Cash_Transfer.json",
            "folder name" : "7 - Cash Transfer"

        }
    }
}



# har files to extract
user_connection = "HAR_files/1-User_Connection.har"
user_management = "HAR_files/2-User_Management.har"
account_management = "HAR_files/3-Account_Management.har"
cash_transfer = "HAR_files/7-Cash_Transfer.har"

# destination file to import

user_connection_dest = "Import/1-User_Connection.json"
user_management_dest = "Import/2-User_Management.json"
account_management__dest = "Import/3-Account_Management.json"
cash_transfer_dest = "Import/7-Cash_Transfer.json"


# Loop until a valid ID is entered
# while True:
#     try:
#         # Display available testing sets
#         for id, testing_set in migration_dict.items():
#                 print(f"{id}. {testing_set['name']}")

#         selected_set_id = int(input("Please select the number of the testing set you want to convert to Bruno collection config: "))

#         # Check if the selected ID is valid
#         if selected_set_id in migration_dict:
#             selected_set = migration_dict[selected_set_id]
#             print(f"Selected set: {selected_set['name']}")
#             selected_set_data = selected_set['data']
#             break
#         else:
#             print("Invalid ID. Please enter a number corresponding to a valid testing set.")
#             print("*******")
#     except ValueError:
#         print("Invalid input. Please enter a valid number.")


# with open(selected_set_data['har_file'], "r") as file:
#         data = json.load(file)
#         log = Log(data)

# to_write = build(log, selected_set)
# write_json_file(selected_set_data['dest_file'],to_write)
# print(log.logAnalyzer())

def list_files_in_directory(path):
    if os.path.isfile(path):
        print(f"'{path}' is a file.")
    elif os.path.isdir(path):
        try:
            collection_dict = {}
            files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
            print(f"Files in directory '{path}':")
            for file in files:
                parts = file.split('-')
                if len(parts) > 1:
                    numeric_key = int(parts[1])
                    name_without_number = '-'.join(parts[2:])
                    collection_name = name_without_number.replace('.har', '').strip()
                    item_data = {
                        "name": collection_name,
                        "data": {
                            "har_file": os.path.join(path, file),
                            "dest_file": os.path.join("Import", name_without_number.replace('.har', '.json')),
                            "folder name" : collection_name
                        }
                    }
                    collection_dict[numeric_key] = item_data
                    
                    # build (log, collection_dict[numeric_key])
                    with open(item_data['data']['har_file'], "r") as file:
                            data = json.load(file)
                            log = Log(data)

                    to_write = build(log, item_data)
                    write_json_file(item_data['data']['dest_file'],to_write)
                    # print(log.logAnalyzer())
            # print(f"Collection dictionary: {collection_dict}")
        except Exception as e:
            print(f"An error occurred while accessing '{path}': {e}")
    else:
        print(f"'{path}' does not exist.")
path = "HAR_files/User Management"
list_files_in_directory(path)