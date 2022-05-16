# test_uno.py
# Tests a player against three random opponents, returning statistics.
# The one required argument is the dotted module path to your player. 
# For example, to test the RandomUnoPlayer, run:
#
# python test_uno.py uno.player.computer.RandomUnoPlayer

from argparse import ArgumentParser
from importlib import import_module
from tqdm import trange
from uno.model.game import UnoGame
from uno.player.computer import RandomUnoPlayer

parser = ArgumentParser()
parser.add_argument("player")
parser.add_argument('-t', '--trials', type=int, default=1000)
parser.add_argument('-d', '--deck', default='standard')
args = parser.parse_args()

tokens = args.player.split('.')
if len(tokens) == 1:
    raise ValueError("Invalid player. Should be something like uno.player.computer.RandomUnoPlayer")
module = '.'.join(tokens[:-1])
class_name = tokens[-1]
mod = import_module(module)
player_class = getattr(mod, class_name)
player = player_class("Contestant")
if not player.is_automated:
    raise ValueError("Can only run tests with automated players.")
players = [
    player,
    RandomUnoPlayer("Opponent 1"),
    RandomUnoPlayer("Opponent 2"),
    RandomUnoPlayer("Opponent 3"),
]
game = UnoGame(players, deck_name=args.deck)
wins = 0

for i in trange(args.trials):
    game.reset()
    while not game.is_over():
        state = game.get_state()
        actions = game.get_actions()
        action = game.current_player().choose_action(state, actions)
        game.play_action(action)
    if game.winner() == player:
        wins += 1
print(f"Result: {args.player} won {wins}/{args.trials} games.")
    
    


