import json
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def load_pricing():
    with open("pricing.json", "r") as f:
        return json.load(f)

def calculate_cost(model, input_tokens, output_tokens):
    pricing = load_pricing()

    if model not in pricing:
        return "Model not found in pricing.json"

    input_cost = (input_tokens / 1_000_000) * pricing[model]["input"]
    output_cost = (output_tokens / 1_000_000) * pricing[model]["output"]

    return round(input_cost + output_cost, 6)

print("AI Cost Tool is ready!")
print("AI Cost Tool is ready!")
print(calculate_cost("gpt-4.1", 500000, 200000))
import os
import pandas as pd

def read_vendor_quotes(folder_path):
    vendor_costs = {}  # initialize dictionary

    # Loop through all Excel files in the folder
    for file in os.listdir(folder_path):
        if file.endswith(".xlsx"):
            vendor_name = file.replace(".xlsx", "")  # filename becomes vendor name
            file_path = os.path.join(folder_path, file)

            # Read the Excel file
            df = pd.read_excel(file_path)

            # Sum the Total column
            total_cost = df["Total"].sum()

            vendor_costs[vendor_name] = total_cost

    return vendor_costs

def compare_vendors(folder_path):
    vendor_costs = read_vendor_quotes(folder_path)

    # Find the vendor with the lowest total cost
    cheapest_vendor = min(vendor_costs, key=vendor_costs.get)
    cheapest_cost = vendor_costs[cheapest_vendor]

    print("\nVendor Cost Summary:")
    for vendor, cost in vendor_costs.items():
        print(f"{vendor}: {cost}")

    print("\nCheapest Vendor:", cheapest_vendor)
    print("Total Cost:", cheapest_cost)

compare_vendors("vendor_quotes")
# -------------------------
# AI Cost Tool (your existing code)
# -------------------------

import json
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def load_pricing():
    ...

def calculate_cost(model, input_tokens, output_tokens):
    ...

print("AI Cost Tool is ready!")

# -------------------------
# Vendor Comparison Tool (paste the improved code here)
# -------------------------

import os
import pandas as pd

def compare_vendor_quotes(folder_path="Vendor_quotes"):
    ...  # <-- paste the entire improved code here

compare_vendor_quotes()

# -------------------------
# End of file
# -------------------------
