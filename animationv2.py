import random
import time
from matplotlib import pyplot as plt
from matplotlib.lines import Line2D

# Constants
ENV_WIDTH = 100
ENV_HEIGHT = 100
FOOD_SPAWN_RATE = 500
STARTING_PLAYERS = 50
ROUNDS = 45
ROUND_DURATION = 500
NIGHT_LENGTH = 5
ENERGY_LOSS_PER_NIGHT = 5
ENERGY_LOSS_PER_DAY = 25
STARTING_ENERGY = 150
ENERGY_GAIN_FROM_FOOD = 35
BASE_ENERGY_REQUIRED_FOR_LIVING = 100
BASE_ENERGY_REQUIRED_FOR_REPRODUCTION = 200
STATUS_ACTIVE = "active"
STATUS_RESTING = "resting"
MUTATION_PROBABILITY = 0.1

# Function to mutate the genome sequence
def mutate_genome_sequence(sequence):
    sequence_list = list(sequence)
    for i in range(len(sequence_list)):
        if random.random() < MUTATION_PROBABILITY:
            sequence_list[i] = random.choice('ATGC')
    return ''.join(sequence_list)

# Genome class
class Genome:
    def __init__(self, sequence):
        self.sequence = sequence
        self.fitness = self.calculate_fitness()

    def calculate_fitness(self):
        count_A = self.sequence.count('A')
        count_C = self.sequence.count('C')
        count_G = self.sequence.count('G')
        count_T = self.sequence.count('T')
        fitness = count_A * 4 + count_C * 3 + count_G * 2 + count_T * 1
        return fitness

# Agent class
class Agent:
    def __init__(self, x, y, genome):
        self.energy = STARTING_ENERGY
        self.x = x
        self.y = y
        self.genome = genome
        self.fitness = genome.fitness
        self.fitness_factor = 1 / (self.fitness)  # Inverse proportion
        self.energy_required_for_living = BASE_ENERGY_REQUIRED_FOR_LIVING
        self.energy_required_for_reproduction = BASE_ENERGY_REQUIRED_FOR_REPRODUCTION
        self.status = STATUS_ACTIVE

    def move(self, env_width, env_height):
        # Calculate the new position
        new_x = (self.x + random.choice([-1, 0, 1])) % env_width
        new_y = (self.y + random.choice([-1, 0, 1])) % env_height
        
        # Ensure the new position is within the environment boundaries
        self.x = max(0, min(new_x, env_width - 1))
        self.y = max(0, min(new_y, env_height - 1))

    def eat(self, food_positions):
        if (self.x, self.y) in food_positions:
            self.energy += ENERGY_GAIN_FROM_FOOD
            food_positions.remove((self.x, self.y))

# Environment class
class Environment:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.food_positions = []

    def spawn_food(self):
        for _ in range(FOOD_SPAWN_RATE):
            self.food_positions.append((random.randint(0, self.width - 1), random.randint(0, self.height - 1)))

# Simulation class
class Simulation:
    def __init__(self, env_width, env_height, starting_players, rounds):
        self.env = Environment(env_width, env_height)
        self.players = self.init_players(starting_players)
        self.rounds = rounds
        self.graph_player_points = []

        # Initialize plot
        plt.ion()
        self.fig, self.ax = plt.subplots(figsize=(8, 8))
        self.ax.set_xlim(0, ENV_WIDTH)
        self.ax.set_ylim(0, ENV_HEIGHT)
        self.food_scatter = self.ax.scatter([], [], c='green', label='Food', marker='*')
        self.player_scatters = {}
        self.ax.legend()
        self.ax.grid()

    def init_players(self, players):
        players_list = []
        for _ in range(players):
            genome_sequence = ''.join(random.choices('ATGC', k=4))  # Example genome sequence
            genome = Genome(genome_sequence)
            players_list.append(Agent(random.randint(0, ENV_WIDTH - 1), random.randint(0, ENV_HEIGHT - 1), genome))
        return players_list

    def run(self):
        current_round = 1
        death_count = 0
        breed_count = 0

        while current_round <= self.rounds and len(self.players) > 2:
            print(f"ROUND {current_round}")

            self.env.spawn_food()
            self.day_phase(current_round)
            self.night_phase()
            round_dead_players = self.cull()
            round_player_babies = self.breed()
            death_count += round_dead_players
            breed_count += round_player_babies
            
            player_count = self.get_count()
            print(f"players: {player_count}")
            print(f"Dead agents: {round_dead_players}")
            print(f"player babies: {round_player_babies}")
            print("----")

            self.graph_player_points.append(player_count)
            current_round += 1

        print("=============================================================")
        print(f"Total dead agents: {death_count}")
        print(f"Total breeding agents: {breed_count}")
        print(f"Total rounds completed: {current_round - 1}")
        print(f"Total population size: {len(self.players)}")
        print("=============================================================")

        self.plot_results()

    def day_phase(self, round):
        start_time = 1
        for player in self.players:
            boundary_position = random.choice([
                (random.randint(0, self.env.width - 1), 0),  # Top boundary
                (random.randint(0, self.env.width - 1), self.env.height - 1),  # Bottom boundary
                (0, random.randint(0, self.env.height - 1)),  # Left boundary
                (self.env.width - 1, random.randint(0, self.env.height - 1))  # Right boundary
            ])
            player.x, player.y = boundary_position
        while True:
            for player in self.players:
                player.move(self.env.width, self.env.height)
                player.eat(self.env.food_positions)
                player.energy -= ENERGY_LOSS_PER_DAY / ROUND_DURATION
            self.update_plot(round, start_time)
            start_time += 1
            if start_time >= ROUND_DURATION:
                break
        self.env.food_positions = []

    def night_phase(self):
        for night in range(NIGHT_LENGTH):
            for player in self.players:
                player.energy -= ENERGY_LOSS_PER_NIGHT / NIGHT_LENGTH

    def cull(self):
        dead_players = 0
        new_players = []
        total_fitness = sum(player.fitness for player in self.players)

        for player in self.players:
            survival_probability = player.fitness * 20 / total_fitness
            if player.energy < player.energy_required_for_living or random.random() > survival_probability:
                dead_players += 1
            else:
                new_players.append(player)
        self.players = new_players
        return dead_players

    def breed(self):
        player_babies = 0
        new_players = []

        total_fitness = sum(player.fitness for player in self.players)

        for player in self.players:
            reproduction_probability = player.fitness * 20 / total_fitness
            if player.energy >= player.energy_required_for_reproduction and random.random() <= reproduction_probability:
                player.energy //= 2
                genome_sequence = mutate_genome_sequence(player.genome.sequence)
                genome = Genome(genome_sequence)
                new_players.append(Agent(random.randint(0, ENV_WIDTH - 1), random.randint(0, ENV_HEIGHT - 1), genome))
                player_babies += 1

        self.players.extend(new_players)
        return player_babies

    def get_count(self):
        return len(self.players)

    def update_plot(self, round, duration):
        food_x, food_y = zip(*self.env.food_positions) if self.env.food_positions else ([], [])
        
        genome_color_map = {
            'A': 'blue',
            'T': 'red',
            'G': 'yellow',
            'C': 'purple',
        }
        
        player_positions = {}
        for player in self.players:
            color = genome_color_map[player.genome.sequence[0]]  # Use the first character of the genome sequence for color
            if color not in player_positions:
                player_positions[color] = ([], [])
            player_positions[color][0].append(player.x)
            player_positions[color][1].append(player.y)

        self.food_scatter.set_offsets(list(zip(food_x, food_y)))
        
        for color, (x_positions, y_positions) in player_positions.items():
            if color in self.player_scatters:
                self.player_scatters[color].set_offsets(list(zip(x_positions, y_positions)))
            else:
                scatter = self.ax.scatter(x_positions, y_positions, c=color, label=f'Players ({color})', marker='o')
                self.player_scatters[color] = scatter

        self.ax.set_title(f"ROUND {round}")
        self.fig.suptitle(f"TIME {duration}")

        self.fig.canvas.draw()
        self.fig.canvas.flush_events()
        time.sleep(0.01)

        # Update the legend
        self.ax.legend(handles=[self.food_scatter] + [Line2D([0], [0], marker='o', color='w', label=f'Players ({color})', markerfacecolor=color) for color in player_positions.keys()])

    def plot_results(self):
        plt.plot(self.graph_player_points, label="players")
        plt.xlabel("Rounds")
        plt.ylabel("Population")
        plt.legend()
        plt.show()

if __name__ == "__main__":
    simulation = Simulation(ENV_WIDTH, ENV_HEIGHT, STARTING_PLAYERS, ROUNDS)
    simulation.run()
    plt.ioff()  # Turn off interactive mode after simulation is done
    plt.show()
