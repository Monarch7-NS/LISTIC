import json

# Chemin vers ton fichier
json_path = "data\Enseignants.json"

with open(json_path, encoding="utf-8") as f:
    data = json.load(f)
c = 0
for key in data:
    if isinstance(data[key], list):
        print(f"{key} : {len(data[key])} éléments")
        c += len(data[key])
print(f"Total : {c} éléments")