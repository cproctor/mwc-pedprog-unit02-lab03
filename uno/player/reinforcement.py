import yaml
from tqdm import trange
from random import random, choice
from pathlib import Path
from tabulate import tabulate

yaml.Dumper.ignore_aliases = lambda *args : True

class ReinforcementLearningUnoPlayer:
    """A player who learns using reinforcement learning.

    Here, we use the TD(memory_factor) algorithm.

    """
    experiences_per_epoch = 100000
    chance_of_random_action = 0.2
    learning_rate = 0.9
    learning_rate_decay = 0.9
    memory_factor = 0.8

    def __init__(self, name, training_file=None, load_params=True):
        self.name = name
        self.is_automated = True
        self.training_file = training_file
        self.reset_trace()
        if training_file and Path(training_file).exists():
            training_data = yaml.safe_load(Path(training_file).read_text())
            self.load_training_data(training_data, load_params=load_params)
        else:
            feature_names = self.get_feature_names()
            self.weights = {feature: 1/len(feature_names) for feature in feature_names}
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
        for sample in trange(self.experiences_per_epoch, desc="TRAIN", leave=False):
            self.train_sarsa_experience(game)
        test_wins = self.test(game, test_samples)
        win_ratio = test_wins / test_samples
        params = {
            'epoch': epoch_num,
            'win_ratio': win_ratio, 
            'learning_rate': self.learning_rate,
        }
        reportable = {k: [v] for k, v in (params | self.weights).items()}
        print(tabulate(reportable, headers="keys"))
        self.training_history.append({
            'weights': self.weights, 
            'test_results': test_wins / test_samples,
            'params': {
                'experiences_per_epoch': self.experiences_per_epoch,
                'learning_rate': self.learning_rate,
                'learning_rate_decay': self.learning_rate_decay,
                'chance_of_random_action': self.chance_of_random_action,
                'memory_factor': self.memory_factor,
            }
        })
        if self.training_file:
            self.save_training_data()
        self.learning_rate = self.learning_rate * self.learning_rate_decay

    def train_sarsa_experience(self, game):
        """Conducts a single training experience and learns from the results.
        The training experience is called SARSA because it involves 
        a State, an Action, a Reward, another State, and another Action. 
        Basically, we compare the quality we predicted for the initial (state, action)
        with the observed reward plus the predicted quality for the result
        (state, action). After a single step, how has our perception of quality 
        changed? We update the feature weights accordingly.
        """
        self.prepare_game(game)
        state = game.get_state()
        actions = game.get_actions()
        action = self.choose_action(state, actions)
        predicted_quality = self.quality(state, action)
        result_state = game.get_state()
        reward = game.get_reward(result_state)
        if game.is_over():
            result_quality = reward
        else:
            next_actions = game.get_actions()
            next_action = self.choose_action(result_state, next_actions)
            next_quality = self.quality(result_state, next_action)
            result_quality = reward + next_quality
        quality_diff = result_quality - predicted_quality

        for f in self.get_feature_names():
            f_function = getattr(self, f)
            f_value = f_function(state, action)
            self.trace[f] = self.trace[f] * self.memory_factor + f_value
            self.weights[f] += self.learning_rate * quality_diff * self.trace[f]
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
        for i in trange(trials, desc="TEST", leave=False):
            game.reset()
            while not game.is_over():
                state = game.get_state()
                actions = game.get_actions()
                action = game.current_player().choose_action(state, actions)
                game.play_action(action)
            if game.winner() == self:
                wins += 1
        return wins

    def save_training_data(self):
        "Saves the learned weights, as well as information about the training history."
        with open(self.training_file, 'w') as file_handler:
            file_handler.write(yaml.dump(self.training_history))

    def load_training_data(self, training_data, load_params=False):
        "Loads training data"
        self.validate_training_data(training_data)
        self.training_history = training_data
        self.weights = self.training_history[-1]['weights']
        if load_params:
            for key, value in self.training_history[-1]['params'].items():
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

    def prepare_game(self, game):
        """Makes sure that the game is ready for this player to play. 
        If not, lets other players play until it's this player's turn. 
        If the game ends, resets the game.
        """
        while not game.is_over() and game.current_player() != self:
            game.current_player().choose_action(game.get_state(), game.get_actions())
        if game.is_over():
            game.reset()
            self.reset_trace()
            while game.current_player() != self:
                game.current_player().choose_action(game.get_state(), game.get_actions())

    def reset_trace(self):
        "Sets the trace to zero."
        self.trace = {feature: 0 for feature in self.get_feature_names()}

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
        
    
