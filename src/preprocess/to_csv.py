import pandas as pd
import json

# Path to your JSON file
json_file_path = "path/to/your/json/file.json"

# Load JSON data from the file
with open(json_file_path, "r", encoding="utf-8") as file:
    data = json.load(file)

# Flatten the nested JSON structure
def flatten_json(y):
    out = {}

    def flatten(x, name=""):
        if type(x) is dict:
            for a in x:
                flatten(x[a], name + a + "_")
        elif type(x) is list:
            i = 0
            for a in x:
                flatten(a, name + str(i) + "_")
                i += 1
        else:
            out[name[:-1]] = x

    flatten(y)
    return out

# Flatten the main JSON data
flattened_data = flatten_json(data)

# Convert the flattened data into a DataFrame
df = pd.DataFrame([flattened_data])

# Save the DataFrame to a CSV file
output_csv_path = "path/to/output/file.csv"
df.to_csv(output_csv_path, index=False, encoding="utf-8")

print(f"CSV file saved to: {output_csv_path}")