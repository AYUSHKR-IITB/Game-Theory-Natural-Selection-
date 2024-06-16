import matplotlib.pyplot as plt
import numpy as np
class Player:
    def __init__(self, name, size, speed, strategy):
        self.name = name
        self.size = size
        self.speed = speed
        self.strategy = strategy  # Pure strategy: {'action': utility}, Mixed strategy: {'action': probability}
        self.utility = 0  # Total utility gained by the player
    
    def choose_action(self):
        if isinstance(self.strategy, dict):
            # Mixed strategy
            actions, probabilities = zip(*self.strategy.items())
            return np.random.choice(actions, p=probabilities)
        else:
            # Pure strategy
            return self.strategy
class Game:
    def __init__(self, payoff_matrix):
        self.payoff_matrix = payoff_matrix  # A dictionary with keys as (action1, action2) and values as (utility1, utility2)
    
    def play(self, player1, player2):
        action1 = player1.choose_action()
        action2 = player2.choose_action()
        utility1, utility2 = self.payoff_matrix[(action1, action2)]
        player1.utility += utility1
        player2.utility += utility2
        return action1, action2, utility1, utility2
import matplotlib.pyplot as plt
import numpy as np

class Simulation:
    def __init__(self, players, game, num_rounds):
        self.players = players
        self.game = game
        self.num_rounds = num_rounds
        self.utilities_over_time = {player.name: [] for player in players}
    
    def run(self):
        for _ in range(self.num_rounds):
            for i, player1 in enumerate(self.players):
                for j, player2 in enumerate(self.players):
                    if i != j:
                        self.game.play(player1, player2)
            for player in self.players:
                self.utilities_over_time[player.name].append(player.utility)
    
    def plot_utilities(self):
        for player_name, utilities in self.utilities_over_time.items():
            plt.plot(range(self.num_rounds), utilities, label=player_name)
        plt.xlabel('Rounds')
        plt.ylabel('Utility')
        plt.title('Utility Variation Over Time')
        plt.legend()
        plt.show()

        
# Define players
player1 = Player('Player 1', size=1, speed=1, strategy={'A': 0.5, 'B': 0.5})  # Mixed strategy
player2 = Player('Player 2', size=1, speed=1, strategy='A')  # Pure strategy

# Define the payoff matrix
payoff_matrix = {
    ('A', 'A'): (3, 3),
    ('A', 'B'): (0, 5),
    ('B', 'A'): (5, 0),
    ('B', 'B'): (1, 1),
}

# Create the game
game = Game(payoff_matrix)

# Run the simulation
simulation = Simulation([player1, player2], game, num_rounds=100)
simulation.run()

# Plot the results
simulation.plot_utilities()
