#!/usr/bin/env python

from game_config import VIEW_CHARS
import globals
import collections
import json
import edge as e


def initialize_board():
    # import the asci board json
    with open('whole_asci_board.json', 'r') as fh:
        view_json = json.load(fh)
    globals.BOARD_VIEW = view_json


def set_board_background():
    water_key = ["0"]
    outline_keys = ["9", "8", "7"]
    ports = ["$"]
    units = []
    for unit_id, idx in globals.BOARD_VIEW["background"].items():
        for pixel in idx["coords"]:
            r = e.Shape(shape=idx["char"], x=pixel[0], y=pixel[1])
            if unit_id in outline_keys:
                pass
            elif unit_id in water_key:
                r.set_color('blue')
            elif unit_id in ports:
                r.set_color('grey', highlights='on_cyan')
            else:
                r.set_color('grey', highlights='on_cyan')
            units.append(r)
    return units


def fixed_shape(board_unit, shape_type):
    od = collections.OrderedDict(sorted(globals.BOARD_VIEW[shape_type].items()))
    units = []
    for unit_id, idx in od.items():
        for pixel in idx["coords"]:
            unit = board_unit[int(unit_id)]
            r = e.Shape(shape=idx["char"], x=pixel[0], y=pixel[1])
            if shape_type == 'settlements':
                r.set_shape(VIEW_CHARS["available_sett"])
            if unit.owner:
                color = unit.owner.color
                if shape_type == 'roads':
                    r.set_color('grey', highlights='on_{}'.format(color.lower()), color_attr='bold')
                if shape_type == 'settlements':
                    r.set_shape(VIEW_CHARS["owned_sett"])
                    if unit.city:
                        r.set_shape(VIEW_CHARS["city"])
                    r.set_color(color.lower(), color_attr='bold')
            units.append(r)
    return units


def text_in_shape(board_unit, shape_type):
    unit_shape = globals.BOARD_VIEW[shape_type]
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
                u = e.Shape(shape=char, x=x, y=y)
                u.set_color('white', color_attr='bold')
                units.append(u)
        if shape_type == "robbers":
            txt_shape = VIEW_CHARS["robber"]
            if tile.blocked:
                for idx, char in enumerate(txt_shape):
                    x = unit_shape[str(tile.tile_id)]["coords"][idx][0]
                    y = unit_shape[str(tile.tile_id)]["coords"][idx][1]
                    u = e.Shape(shape=char, x=x, y=y)
                    u.set_color('red', color_attr='bold')
                    units.append(u)
    return units


def update_view(board):
    # init display 73:44
    display = [[" " for _ in range(73)] for _ in range(44)]

    # init board background
    background = set_board_background()
    # iterate through all roads
    roads = fixed_shape(board.roads, "roads")
    # iterate through all settelments
    setts = fixed_shape(board.settelments, "settlements")
    # iterate through all numbers on tiles
    nums = text_in_shape(board.tiles, "numbers")
    # iterate through all resources on tiles
    srcs = text_in_shape(board.tiles, "resources")
    # iterate through all tiles and place robber
    rbrs = text_in_shape(board.tiles, "robbers")

    for back in background:
        display[back.get_y()][back.get_x()] = back
    for road in roads:
        display[road.get_y()][road.get_x()] = road
    for sett in setts:
        display[sett.get_y()][sett.get_x()] = sett
    for num in nums:
        display[num.get_y()][num.get_x()] = num
    for src in srcs:
        display[src.get_y()][src.get_x()] = src
    for rbr in rbrs:
        display[rbr.get_y()][rbr.get_x()] = rbr

    for row in display:
        print("".join([str(s) for s in row]))
