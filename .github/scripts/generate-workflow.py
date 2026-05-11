import hcl2
import json

with open("infra/variables.tf", "r") as f:
    data = hcl2.load(f)

inputs = {}

for var in data.get("variable", []):
    for name, body in var.items():
        desc = body.get("description", f"Variable {name}")
        required = "default" not in body

        inputs[name] = {
            "description": desc,
            "required": required,
            "type": "string"
        }

print(json.dumps(inputs, indent=2))
