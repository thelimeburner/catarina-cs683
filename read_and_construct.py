#!/usr/bin/env python

import collections
import json
import edge as e


with open('asci_board4.json', 'r') as fh:
    board_roads = json.load(fh)
with open('asci_board_sett.json', 'r') as fh:
    board_setts = json.load(fh)
with open('asci_board_num.json', 'r') as fh:
    board_num = json.load(fh)
with open('asci_board_src.json', 'r') as fh:
    board_src = json.load(fh)
with open('asci_board_rbr.json', 'r') as fh:
    board_rbr = json.load(fh)

# init display 73:44
display = [[" " for y in range(73)] for x in range(44)]

od = collections.OrderedDict(sorted(board_roads["roads"].items()))
edges = []
for idx, road in od.items():
    for sub in road["coords"]:
        edges.append(e.Shape(shape=road["char"], x=sub[0], y=sub[1]))
od = collections.OrderedDict(sorted(board_setts["settlements"].items()))
nodes = []
for idx, road in od.items():
    for sub in road["coords"]:
        nodes.append(e.Shape(shape=road["char"], x=sub[0], y=sub[1]))
od = collections.OrderedDict(sorted(board_num["numbers"].items()))
nums = []
for idx, road in od.items():
    for sub in road["coords"]:
        nums.append(e.Shape(shape=road["char"], x=sub[0], y=sub[1]))
od = collections.OrderedDict(sorted(board_src["resources"].items()))
srcs = []
for idx, road in od.items():
    for sub in road["coords"]:
        srcs.append(e.Shape(shape=road["char"], x=sub[0], y=sub[1]))
od = collections.OrderedDict(sorted(board_rbr["robbers"].items()))
rbrs = []
for idx, road in od.items():
    for sub in road["coords"]:
        rbrs.append(e.Shape(shape=road["char"], x=sub[0], y=sub[1]))

for edge in edges:
    display[edge.get_y()][edge.get_x()] = edge
for node in nodes:
    display[node.get_y()][node.get_x()] = node
for num in nums:
    display[num.get_y()][num.get_x()] = num
for src in srcs:
    display[src.get_y()][src.get_x()] = src
for rbr in rbrs:
    display[rbr.get_y()][rbr.get_x()] = rbr

for row in display:
    print("".join([str(s) for s in row]))
