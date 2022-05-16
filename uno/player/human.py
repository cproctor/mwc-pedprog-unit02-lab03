class HumanUnoPlayer:
    """Represents a human uno player.
    """

    def __init__(self, name):
        self.name = name
        self.is_automated = False

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
        
    
