import json

people_string = """
{
"people" : [
    {
    "name" : "Irfan",
    "last" : "Pasha",
    "dob"  : "18-July-1989",
    "email" : ["abc@gmail.com","1234@yahoo.com","abc123@hotmail.com"],
    "phone" : null,
    "Indian" : true
    },
    {
    "name" : "Kevin",
    "last" : "Wang",
    "dob"  : "11-July-1991",
    "email" : ["abc1@gmail.com","1234a@yahoo.com","abc1231@hotmail.com"],
    "phone" : null,
    "Indian" : false 
    }
]
}
"""

data = json.loads(people_string)  # loads convert Json object to python dictionary


print(data)
print(type(data))

for person in data["people"]:
    print(person["Indian"])

new_string = json.dumps(
    data, indent=2
)  # Dumps convert python dictionary to jsonn object,

print(new_string)

print(json.dumps(data, indent=2, sort_keys=True))

with open("states.json") as f:
    data = json.load(
        f
    )  # Note we should use load not loads, loads need to string load need file oject

print(data)

with open("json_from_python.json", "w+") as f:
    json.dump(data, f, indent=2)

