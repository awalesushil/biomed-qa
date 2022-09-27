"""
    Evaluate the quality of the responses of the system
"""

import os
import json

responses = {}

for file in os.listdir("responses"):
    with open(os.path.join("responses", file), "r", encoding="utf-8") as f:
        response = json.load(f)
        responses.setdefault(response["question"], [])
        responses[response["question"]].append(response["data"])

overall_precision = {}

for question, data in responses.items():
    print(question)
    print("=========================================")
    ranks = {}

    for each in data:
        for rank, value in each.items():
            if value == "Relevant":
                ranks[rank] = 1
            else:
                ranks[rank] = 0
    COUNT = 0
    for rank, value in ranks.items():
        COUNT += value
        print(f"P@{int(rank)+1}: {COUNT/(int(rank)+1)}")
        overall_precision.setdefault(rank, [])
        overall_precision[rank].append(COUNT/(int(rank)+1))

print("=========================================")
print("Mean Average Precision")
for rank, values in overall_precision.items():
    print(f"P@{int(rank)+1}: {sum(values)/len(values)}")
