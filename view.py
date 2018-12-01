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


def fixed_shape(board_unit, shape_type):
    od = collections.OrderedDict(sorted(BOARD_VIEW[shape_type].items()))
    units = []
    for unit_id, idx in od.items():
        for pixel in idx["coords"]:
            unit = board_unit[int(unit_id)]
            r = e.Shape(shape=idx["char"], x=pixel[0], y=pixel[1])
            if unit.owner:
                color = unit.owner.color
                r.set_color(color.lower())
            units.append(r)
    return units


def text_in_shape(board_unit, shape_type):
    unit_shape = BOARD_VIEW[shape_type]
    units = []
    for tile in board_unit:
        if shape_type == "numbers":
            if tile.number:
                txt_shape = str(tile.number)
                for idx, char in enumerate(txt_shape):
                    x = unit_shape[str(tile.tile_id)]["coords"][idx][0]
                    y = unit_shape[str(tile.tile_id)]["coords"][idx][1]
                    units.append(e.Shape(shape=char, x=x, y=y))
        if shape_type == "resources":
            txt_shape = str(tile.resource)
            for idx, char in enumerate(txt_shape):
                x = unit_shape[str(tile.tile_id)]["coords"][idx][0]
                y = unit_shape[str(tile.tile_id)]["coords"][idx][1]
                units.append(e.Shape(shape=char, x=x, y=y))
    return units


def update_view(board):
    # init display 73:44
    display = [[" " for _ in range(73)] for _ in range(44)]

    # iterate through all roads
    roads = fixed_shape(board.roads, "roads")
    # iterate through all settelments
    setts = fixed_shape(board.settelments, "settlements")
    # iterate through all numbers on tiles
    nums = text_in_shape(board.tiles, "numbers")
    # iterate through all resources on tiles
    srcs = text_in_shape(board.tiles, "resources")

    for road in roads:
        display[road.get_y()][road.get_x()] = road
    for sett in setts:
        display[sett.get_y()][sett.get_x()] = sett
    for num in nums:
        display[num.get_y()][num.get_x()] = num
    for src in srcs:
        display[src.get_y()][src.get_x()] = src

    for row in display:
        print("".join([str(s) for s in row]))
