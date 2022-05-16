from random import choice

class RandomUnoPlayer:
    """Represents an automated Uno player who plays random moves.
    """
    def __init__(self, name):
        self.name = name
        self.is_automated = True

    def choose_action(self, state, actions):
        action = choice(actions)
        message = self.action_message(action)
        return action

    def action_message(self, action):
        if action["action"] == "pass":
            return f"{self.name} passes."
        elif action["action"] == "draw":
            return f"{self.name} draws a card."
        elif action["action"] == "play":
            if "color" in action:
                return f"{self.name} plays {action['card']} and sets the color to {action['color']}."
            else:
                return f"{self.name} plays {action['card']}."
        
    
