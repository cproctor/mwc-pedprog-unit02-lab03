# test_uno.py
# Tests a player against three random opponents, returning statistics.
# The one required argument is the dotted module path to your player. 
# For example, to train the Eliza reinforcement learning player, run:
#
# python test_uno.py uno.player.example.Eliza

from argparse import ArgumentParser
from importlib import import_module
from tqdm import trange
from uno.model.game import UnoGame
from uno.player.computer import RandomUnoPlayer

parser = ArgumentParser()
parser.add_argument("player")
parser.add_argument('-e', '--epochs', type=int, default=10)
parser.add_argument('-f', '--training-file')
parser.add_argument('-d', '--deck', default='standard')
args = parser.parse_args()

tokens = args.player.split('.')
if len(tokens) == 1:
    raise ValueError("Invalid player. Should be something like uno.player.computer.Eliza")
module = '.'.join(tokens[:-1])
class_name = tokens[-1]
mod = import_module(module)
player_class = getattr(mod, class_name)
player = player_class("Contestant", training_file=args.training_file)
players = [
    player,
    RandomUnoPlayer("Opponent 1"),
    RandomUnoPlayer("Opponent 2"),
    RandomUnoPlayer("Opponent 3"),
]
game = UnoGame(players, deck_name=args.deck)

for epoch in range(10): 
    player.train_epoch(game)
    print(player.training_history)

