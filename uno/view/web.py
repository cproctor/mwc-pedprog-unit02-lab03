from flask import Flask, request, render_template
from threading import Thread
import webbrowser
import time
import sys

class WebUnoView:
    """A view of the Uno card game for a web browser.
    The structure of the web view is somewhat different from the structure of the terminal view, 
    largely due to the fact that the terminal view actively solicits user input while the web view
    processes automated players and then sits and waits for user input.
    """

    def __init__(self):
        self.app = self.create_app()

    def play(self, game):
        "Plays a game"
        self.game = game
        self.play_automated_turns()
        Thread(target=self.app.run).start()
        webbrowser.open_new("http://127.0.0.1:5000")
        while True:
            try:
                time.sleep(1)
            except KeyboardInterrupt:
                sys.exit(0)

    def play_automated_turns(self):
        "Plays all automated turns."
        while not self.game.is_over() and self.game.current_player().is_automated:
            state = self.game.get_state()
            actions = self.game.get_actions()
            action = self.game.current_player().choose_action(state, actions)
            self.game.play_action(action)

    def handle_post(self, formdata):
        """A POST request is sent when submitting a form.
        In Uno, this happens when a user clicks a card causing it to be played.
        """
        if "restart" in formdata:
            self.game.reset()
        else:
            action = {
                "action": formdata["action"]
            }
            if "card_index" in formdata:
                card_index = int(formdata["card_index"])
                action["card"] = self.game.current_hand()[card_index]
            if "color" in formdata:
                action["color"] = formdata["color"]
            self.game.play_action(action)
            self.play_automated_turns()

    def render_page(self):
        """Assembles a HTML page based on the current game state.
        """
        cp = self.game.current_player()
        opponent_names = [opp.name for opp in self.game.opponents()]
        opponent_hands = self.game.opponent_hands()
        action_verbs = [action["action"] for action in self.game.get_actions()]
        params = {
            "current_player": {"name": cp.name, "hand": self.game.current_hand()},
            "opponents": [{"name": name, "hand": hand} for name, hand in zip(opponent_names, opponent_hands)],
            "play_pile": self.game.play_pile,
            "playable_cards": [a["card"] for a in self.game.get_actions() if "card" in a.keys()],
            "messages": self.game.messages,
            "can_draw": "draw" in action_verbs,
            "can_pass": "pass" in action_verbs,
            "winner": self.game.winner(),
        }
        return render_template("uno.html", **params)

    def create_app(self):
        """Creates a Flask app and returns it.
        Note that this method uses some advanced techniques you have not yet learned.
        """
        app = Flask(__name__)

        @app.route('/', methods=["GET", "POST"])
        def handle_request():
            if request.method == "POST":
                self.handle_post(request.form)
            return self.render_page()

        return app


