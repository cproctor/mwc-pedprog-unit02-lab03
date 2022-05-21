import yaml
from tqdm import trange
from random import random, choice
from pathlib import Path

class ReinforcementLearningUnoPlayer:
    """A player who learns using reinforcement learning.

    Q-learning Uno:

     - Start a game.
     - For each trial:
       - Choose an action. With some probability ε, choose a random
         action. Otherwise, choose the action for which Q(s, a) is highest.
       - Estimate the value of Q(s, a). 
       - Take the action. Then 

    """
    samples_per_epoch = 100000
    chance_of_random_action = 0.3
    learning_rate = 0.99

    def __init__(self, name, training_file=None, load_params=False):
        self.name = name
        self.is_automated = True
        if training_file and Path(training_file).exists():
            training_data = yaml.safe_load(training_file)
            self.load_training_data(training_data, load_params=load_params)
        else:
            feature_names = self.get_feature_names()
            self.weights = {feature: 0 for feature in feature_names}
            self.training_history = []

    def get_feature_names(self):
        """Returns a list of strings naming feature functions. 
        Each should be the name of a method defined for this class.
        Only the feature functions listed here will be used.
        """
        return []

    def get_features(self, state, action):
        """Converts a (state, action) into a dict of {feature_name: float}
        """
        return {f: getattr(self, f)(state, action) for f in self.get_feature_names()}

    def quality(self, state, action):
        """Returns an estimage of the quality of a (state, action).
        The quality of a (state, action) is estimated by multiplying each
        feature value by the learned feature weights. 
        """
        features = self.get_features(state, action)
        return sum(value * self.weights[key] for key, value in features.items())

    def train_epoch(self, game, test_samples=1000):
        "Runs one epoch of training."
        epoch_num = len(self.training_history)
        print(f"TRAINING EPOCH #{epoch_num} WITH {self.samples_per_epoch} SAMPLES")
        for sample in trange(self.samples_per_epoch):
            self.train_sample(game)
        print("TESTING")
        test_wins = self.test(game, test_samples)
        win_ratio = test_wins / test_samples
        print(f"WIN RATIO: {win_ratio}")
        self.training_history.append({
            'weights': self.weights, 
            'test_results': (test_wins, test_samples),
            'params': {
                'samples_per_epoch': self.samples_per_epoch,
                'learning_rate': self.learning_rate,
                'chance_of_random_action': self.chance_of_random_action,
            }
        })

    def train_sample(self, game):
        """Runs a single training sample, updating weights.
        """
        self.ensure_game_is_ready(game)
        state = game.get_state()
        actions = game.get_actions()
        action = self.choose_action(state, actions)
        predicted_quality = self.quality(state, action)
        result_state = game.get_state()
        reward = game.get_reward(result_state)
        if game.is_over():
            observed_quality = reward
        else:
            next_actions = game.get_actions()
            next_action = self.choose_action(result_state, next_actions)
            next_quality = self.quality(result_state, next_action)
            observed_quality = reward + next_quality
        quality_diff = predicted_quality - observed_quality

        for feature in self.get_feature_names():
            feature_function = getattr(self, feature)
            feature_value = feature_function(state, action)
            self.weights[feature] += self.learning_rate * quality_diff * feature_value
        self.normalize_weights()

    def choose_action(self, state, actions):
        """Chooses an action give the state. Returns quality of (state, action) and action.
        With some probability (self.chance_of_random_action), chooses a random action. 
        Otherwise, chooses the action whose quality with this state is highest.
        """
        should_behave_randomly = random() < self.chance_of_random_action
        if should_behave_randomly:
            action = choice(actions)
        else:
            qualities_and_actions = [(self.quality(state, a), a) for a in actions]
            quality = max(q for q, a in qualities_and_actions)
            best_actions = [a for q, a in qualities_and_actions if q == quality]
            action = choice(best_actions)
        return action

    def test(self, game, trials=1000):
        "Runs a test"
        wins = 0
        for i in trange(trials):
            game.reset()
            while not game.is_over():
                state = game.get_state()
                actions = game.get_actions()
                action = game.current_player().choose_action(state, actions)
                game.play_action(action)
            if game.winner() == self:
                wins += 1
        return wins

    def save_training_data(self, filename):
        "Saves the learned weights, as well as information about the training history."
        with open(filename, 'w') as file_handler:
            file_handler.write(yaml.dump(self.training_history))

    def load_training_data(self, training_data, load_params=False):
        "Loads training data"
        self.validate_training_data(training_data)
        self.training_history = training_data
        self.weights = self.training_history[-1]['weights']
        if load_params:
            for key, value in self.training_history[-1]['params']:
                setattr(self, key, value)

    def validate_training_data(self, training_data):
        "Checks to make sure loaded training data is compabible with this class."
        if len(training_data) == 0:
            raise ValueError("Training data is empty.")
        for epoch in training_data:
            if set(self.get_feature_names()) != epoch['weights'].keys():
                raise ValueError("Training data has different features from this class.")

    def normalize_weights(self):
        """Normalizes the feature weights. 
        If the sum of the absolute values of weights is greater than 1, then divides all 
        weights by the weight sum, so that the sum of weights now equals 1.  The magnitude 
        of the weights isn't important; all that matters is the ration between them. Normalizing
        them keeps weights from becoming huge for very important features.
        """
        weight_sum = sum(abs(w) for w in self.weights.values())
        if weight_sum > 1:
            for feature in self.get_feature_names():
                self.weights[feature] = self.weights[feature] / weight_sum

    def ensure_game_is_ready(self, game):
        """Makes sure that the game is ready for this player to play. 
        If not, lets other players play until it's this player's turn. 
        If the game ends, resets the game.
        """
        while not game.is_over() and game.current_player() != self:
            game.current_player().choose_action(game.get_state(), game.get_actions())
        if game.is_over():
            game.reset()
        while game.current_player() != self:
            game.current_player().choose_action(game.get_state(), game.get_actions())

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
        
    
