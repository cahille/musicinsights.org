#!/usr/local/bin/python3.8

import json
import os

# {
#     "in": "Reunion.mscz",
#     "out": "Reunion-coloured.pdf",
#     "plugin": "colornotes.qml"
# },

jobs = []

fromDirectory = "musicxml-out"
toDirectory = "pdf"

for root, dirs, fromFiles in os.walk(fromDirectory, topdown=False, ):
    for fromFile in sorted(fromFiles):
        if not fromFile.endswith(".xml"):
            continue

        print(f"{fromFile=}")
        thisToDirectory = root.replace(fromDirectory, toDirectory)

        toFile = fromFile.replace(".xml", ".pdf")
        jobs.append({
            "in": f"{root}/{fromFile}",
            "out": f"{thisToDirectory}/{toFile}"
        })

print(f"{len(jobs)}")

with open('jobs.json', 'w') as outfile:
    json.dump(jobs, outfile, indent=4)
