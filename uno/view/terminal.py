import re
from click import style
from uno.model.card import Card

class TerminalUnoView:
    """A view of the Uno card game for the Terminal.
    """

    def __init__(self):
        self.last_message_seen = 0

    def play(self, game):
        "Plays a game"
        self.greet()
        while not game.is_over():
            action = self.get_action(game)
            game.play_action(action)
            self.show_unseen_messages(game)
        self.conclude(game)

    def greet(self):
        print("Welcome to Uno!")

    def get_action(self, game):
        "gets an action from a player."
        player = game.current_player()
        print('-' * 80)
        print(f"It's {player.name}'s turn.")
        state = game.get_state()
        actions = game.get_actions()
        if player.is_automated:
            action = player.choose_action(state, actions)
        else:
            print("Opponent hands:", state["opponent_hands"])
            print("Your hand: ", ', '.join(self.color_card(card) for card in state["hand"]))
            print("Top card: ", self.color_card(state["top_card"]))
            print("Choose an action:")
            for i, action in enumerate(actions):
                print(f"{i}. {self.choice_text(action)}")
            choice = self.get_integer_input(len(actions))
            action = actions[choice]
        return action

    def choice_text(self, action):
        if action["action"] == "pass":
            return "Pass."
        elif action["action"] == "draw":
            return f"Draw a card."
        elif action["action"] == "play":
            card_text = self.color_card(action['card'])
            if "color" in action:
                return f"Play {card_text} and set the color to {action['color']}."
            else:
                return f"Play {card_text}."

    def show_unseen_messages(self, game):
        """Prints out all messages which have not yet been seen, and then 
        updates self.last_message_seen to record that these messages have
        been seen.
        """
        unseen_messages = game.messages[self.last_message_seen:]
        for message in unseen_messages:
            print(' - ' + self.color_message(message))
        self.last_message_seen = len(game.messages)

    def get_integer_input(self, maximum):
        "Gets an integer from the user less than maximum."
        while True:
            response = input("> ")
            if response.isdigit():
                num = int(response)
                if 0 <= num and num < maximum:
                    return num
            print("Invalid input.")

    def conclude(self, game):
        print(f"Congratulations to {game.winner().name}")

    def color_card(self, card):
        "Formats a card's code using color for the Terminal"
        if card.color == "RED":
            return style(card.code, fg="red")
        elif card.color == "YELLOW":
            return style(card.code, fg="yellow")
        elif card.color == "GREEN":
            return style(card.code, fg="green")
        elif card.color == "BLUE":
            return style(card.code, fg="blue")
        elif card.color == "WILD":
            return style(card.code, fg="bright_black")

    def color_message(self, message):
        """Searches for card codes in a message. If found, replaces them with colored text.
        This method uses regular expressions, an extremely powerful form of pattern-matching
        which you haven't learned yet.
        """
        pattern = "[RYGBW][0123456789SRDWX]"
        matches = re.findall(pattern, message)
        for match in matches:
            message = message.replace(match, self.color_card(Card(match)))
        return message
        
        
