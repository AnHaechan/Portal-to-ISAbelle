# Fix the paths in universal_test_theorems/*.json
# More info: https://docs.google.com/document/d/1MqEHY5iTvGhzZk0qVjO_L0byMZtf6rV_CfOJ3G3y8ko/edit#heading=h.t82z9jg3rjka

# "/home/ywu/afp-2021-02-11/thys/Valuation/Valuation1.thy"
# => "/home/haechan.an/afp-2021-10-22/thys/Valuation/Valuation1.thy"

import os
import json

directory_path = './universal_test_theorems'

json_files = [file for file in os.listdir(directory_path) if file.endswith('.json')]

for json_file in json_files:
    file_path = os.path.join(directory_path, json_file)

    try:
        with open(file_path, 'r') as file:
            data = json.load(file)

        # "/home/ywu/afp-2021-02-11/thys/Valuation/Valuation1.thy"
        # => "/home/haechan.an/afp-2021-10-22/thys/Valuation/Valuation1.thy"
        data[0][0] = data[0][0].replace("ywu", "haechan.an").replace("afp-2021-02-11", "afp-2021-10-22")

        with open(file_path, 'w') as file:
            json.dump(data, file, indent=2)

    except Exception as e:
        print(f"Error processing {json_file}: {e}")
