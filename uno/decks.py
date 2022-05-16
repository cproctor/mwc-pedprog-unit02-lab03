"""Defines various decks for the uno card game.
"""

basic_deck = []
for color in ['R', 'B', 'G', 'Y']:
    for rank in range(10):
        basic_deck.append(f"{color}{rank}")
        if rank > 0:
            basic_deck.append(f"{color}{rank}")

standard_deck = basic_deck.copy()
for color in ['R', 'B', 'G', 'Y']:
    for rank in ['S', 'D', 'R']:
        standard_deck.append(f"{color}{rank}")
        standard_deck.append(f"{color}{rank}")
for i in range(4):
    standard_deck.append('WW')
    standard_deck.append('WX')

debug_wild_deck = ['WW', 'WX'] * 50

decks = {
    "basic": basic_deck,
    "standard": standard_deck,
    "debug_wild": debug_wild_deck,
}
