import json
colors = {}
if colors == {}:
    print("Loading colors...")
    with open('data/colors.json','r') as file:
        colors = json.load(file)