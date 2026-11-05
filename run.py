#!/usr/bin/env python3

import csv
import sys
import pydot

dirname = sys.argv[-1]
csv.field_size_limit(sys.maxsize)

CRATES = {}
VERSIONS = {}  # version_id -> crate_id

# read list of crates
with open("{}/data/crates.csv".format(dirname)) as f:
    reader = csv.DictReader(f)
    for row in reader:
        crate_name = row["name"]
        crate_id = row["id"]
        CRATES[crate_id] = {
            "name": crate_name,
            # crates this crate depends on
            "dependencies": [],
            # crates that depend on this crate
            "rev_dependencies": []

        }


# find latest crate version, ignore all others
with open("{}/data/versions.csv".format(dirname)) as f:
    reader = csv.DictReader(f)
    for row in reader:
        crate_id = row["crate_id"]
        ver_id = row["id"]
        ver_no = row["num"]
        VERSIONS[ver_id] = crate_id
        if crate_id not in CRATES:
            print(f"missing crate: {crate_id}")
        else:
            if "version_id" not in CRATES[crate_id]:
                CRATES[crate_id]["version_id"] = ver_id
                CRATES[crate_id]["version_no"] = ver_no
            elif CRATES[crate_id]["version_id"] < ver_id:
                CRATES[crate_id]["version_id"] = ver_id
                CRATES[crate_id]["version_no"] = ver_no


with open("{}/data/dependencies.csv".format(dirname)) as f:
    reader = csv.DictReader(f)
    for row in reader:
        dependency_id = row["crate_id"]
        ver_id = row["version_id"]
        crate_id = VERSIONS[ver_id]
        if ver_id == CRATES[crate_id]["version_id"]:
            CRATES[crate_id]["dependencies"].append(dependency_id)
            CRATES[dependency_id]["rev_dependencies"].append(crate_id)


graph = pydot.Dot("Rust crates", graph_type="graph")


with open('nodes.csv', 'w') as nodes_file:
    writer = csv.writer(nodes_file)
    writer.writerow(["id", "label"])
    for crate_id, data in CRATES.items():
        if len(data["rev_dependencies"]) > 0 or len(data["dependencies"]) > 0:
            node = pydot.Node(crate_id, label=data["name"])
            writer.writerow([crate_id, data["name"]])
            graph.add_node(node)
            CRATES[crate_id]["node"] = node


with open('edges.csv', 'w') as nodes_file:
    writer = csv.writer(nodes_file)
    writer.writerow(["source", "taget"])

    for crate_id, data in CRATES.items():
        if len(data["dependencies"]) > 0:
            node = data["node"]
            for dep_id in data["dependencies"]:
                dep_node = CRATES[dep_id]["node"]
                my_edge = pydot.Edge(crate_id, dep_id)
                graph.add_edge(my_edge)
                writer.writerow([crate_id, dep_id])

graph.write_raw("graph.dot")
