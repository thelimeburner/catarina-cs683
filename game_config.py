"""
                            Red Player
                         , - ~ ~ ~ - ,
                     , '               ' ,
                   ,                       ,
                  ,                         ,
                 ,                           ,
   Magenta Player,                           , Blue Player
                 ,                           ,
                  ,                         ,
                   ,                       ,
                     ,                  , '
                       ' - , _ _ _ ,  '
                            Yellow Player
"""

PLAYERS_ORDER = {
    3: {
        'Red': 'Blue',
        'Blue': 'Yellow',
        'Yellow': 'Red'
    },
    4: {
        'Red': 'Blue',
        'Blue': 'Yellow',
        'Yellow': 'Magenta',
        'Magenta': 'Red'
    }
}

# PLAYERS_SPECIES = ['BasicSearchAI', 'RandomAI', 'RandomAI', 'Player']
PLAYERS_SPECIES = ['RandomAI', 'RandomAI', 'RandomAI', 'Player']

# the target number of victory points
VP = 8

# the maximum number of turns a game should run for before giving up
MAX_TURNS = 120

"""
User input options:
    Keyboard
    TODO: GPIO
"""
USER_INPUT = 'keyboard'


"""
Player colors options:
    Default = Red, Blue, Orange, White
    TODO: Custom colors
"""
PLAYER_COLORS = 'default'

#MOCK_UP = [31, 32, 33, 35, 35, 38, 37, 41, 39, 44, 41, 68]
#MOCK_UP = 'random'
MOCK_UP = False
FRIENDLY_ROBBER = False

VIEW_CHARS = {
    "available_sett": "*",
    "owned_sett": "@",
    "city": "Q",
    "robber": "rbbr"
}
