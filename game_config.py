"""
                        Red Player
                     , - ~ ~ ~ - ,
                 , '               ' ,
               ,                       ,
              ,                         ,
             ,                           ,
Orange Player,                           , Blue Player
             ,                           ,
              ,                         ,
               ,                       ,
                 ,                  , '
                   ' - , _ _ _ ,  '
                        White Player
"""

PLAYERS_ORDER = {
    3: {
        'Red': 'Blue',
        'Blue': 'White',
        'White': 'Red'
    },
    4: {
        'Red': 'Blue',
        'Blue': 'White',
        'White': 'Orange',
        'Orange': 'Red'
    }
}

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

MOCK_UP = [31, 32, 33, 35, 35, 38, 37, 41, 39, 44, 41, 68]
FRIENDLY_ROBBER = True
