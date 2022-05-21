"""Defines various decks for the uno card game.
"""

basic_deck = []
for color in ['R', 'B', 'G', 'Y']:
    for rank in range(10):
        basic_deck.append(f"{color}{rank}")
        if rank > 0:
            basic_deck.append(f"{color}{rank}")


special_cards = []
for color in ['R', 'B', 'G', 'Y']:
    for rank in ['S', 'D', 'R']:
        special_cards.append(f"{color}{rank}")
        special_cards.append(f"{color}{rank}")
for i in range(4):
    special_cards.append('WW')
    special_cards.append('WX')

standard_deck = basic_deck.copy() + special_cards
special_deck = special_cards * 4

decks = {
    "basic": basic_deck,
    "standard": standard_deck,
    "special": special_deck,
}
