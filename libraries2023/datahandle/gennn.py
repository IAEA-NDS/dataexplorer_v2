import json
dict = {}

for i in range(50,99):
    dict[f"N{i-50}"] = {
    "mt": str(i),
    "reaction": f"(n,n{i-50})",
    "sf5-8": "PAR,SIG"
    }
    
print(json.dumps(dict, indent=1))

