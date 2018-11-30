#!/usr/bin/env python

import collections
import json
import edge as e


def initialize_board():
    # import the asci board json
    with open('whole_asci_board.json', 'r') as fh:
        view_json = json.load(fh)
    global BOARD_VIEW
    BOARD_VIEW = view_json


def update_view(board):

    # init display 73:44
    display = [[" " for y in range(73)] for x in range(44)]

    od = collections.OrderedDict(sorted(BOARD_VIEW["roads"].items()))
    roads = []
    for road_id, idx in od.items():
        for pixel in idx["coords"]:
            r = e.Shape(shape=idx["char"], x=pixel[0], y=pixel[1])
            if board.roads[int(road_id)].owner:
                color = board.roads[int(road_id)].owner.color
                r.set_color(color.lower())
            roads.append(r)
    od = collections.OrderedDict(sorted(BOARD_VIEW["settlements"].items()))
    setts = []
    for sett_id, idx in od.items():
        for pixel in idx["coords"]:
            s = e.Shape(shape=idx["char"], x=pixel[0], y=pixel[1])
            if board.settelments[int(sett_id)].owner:
                color = board.settelments[int(sett_id)].owner.color
                s.set_color(color.lower())
            setts.append(s)

    for road in roads:
        display[road.get_y()][road.get_x()] = road
    for sett in setts:
        display[sett.get_y()][sett.get_x()] = sett

    for row in display:
        print("".join([str(s) for s in row]))
