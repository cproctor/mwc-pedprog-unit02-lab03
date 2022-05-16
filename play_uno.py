from uno.model.game import UnoGame
from uno.view.terminal import TerminalUnoView
from uno.view.web import WebUnoView
from uno.player.human import HumanUnoPlayer
from uno.player.computer import RandomUnoPlayer

players = [
    #HumanUnoPlayer(input("What is your name? ")),
    HumanUnoPlayer("Chris"),
    RandomUnoPlayer("Bot 1"),
    RandomUnoPlayer("Bot 2"),
    RandomUnoPlayer("Bot 3"),
]
game = UnoGame(players, "basic")
#view = TerminalUnoView()
view = WebUnoView()
view.play(game)
