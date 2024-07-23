import random
import time
from matplotlib import pyplot as plt

# Constants
ENV_WIDTH = 100
ENV_HEIGHT = 100
FOOD_SPAWN_RATE = 200
STARTING_PLAYERS = 50
ROUNDS = 10
DAY_LENGTH = 15
NIGHT_LENGTH = 5
STARTING_ENERGY = 150
ENERGY_GAIN_FROM_FOOD = 50
BASE_ENERGY_REQUIRED_FOR_LIVING = 20
BASE_ENERGY_REQUIRED_FOR_REPRODUCTION = 200
STATUS_ACTIVE = "active"
STATUS_RESTING = "resting"

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

class Agent:
    def __init__(self, x, y, genome):
        self.energy = STARTING_ENERGY
        self.x = x
        self.y = y
        self.genome = genome
        self.fitness = genome.fitness
        self.fitness_factor = 100 / (self.fitness + 1)  # Inverse proportion
        self.energy_required_for_living = BASE_ENERGY_REQUIRED_FOR_LIVING * self.fitness_factor
        self.energy_required_for_reproduction = BASE_ENERGY_REQUIRED_FOR_REPRODUCTION * self.fitness_factor
        self.status = STATUS_ACTIVE

    def move(self, env_width, env_height):
        self.x = (self.x + random.choice([-1, 0, 1])) % env_width
        self.y = (self.y + random.choice([-1, 0, 1])) % env_height

    def eat(self, food_positions):
        if (self.x, self.y) in food_positions:
            self.energy += ENERGY_GAIN_FROM_FOOD
            food_positions.remove((self.x, self.y))

class Environment:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.food_positions = []

    def spawn_food(self):
        for _ in range(FOOD_SPAWN_RATE):
            self.food_positions.append((random.randint(0, self.width - 1), random.randint(0, self.height - 1)))

class Simulation:
    def __init__(self, env_width, env_height, starting_players, rounds):
        self.env = Environment(env_width, env_height)
        self.players = self.init_players(starting_players)
        self.rounds = rounds
        self.graph_player_points = []

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
            self.day_phase()
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

    def day_phase(self):
        for day in range(DAY_LENGTH):
            for player in self.players:
                player.move(self.env.width, self.env.height)
                player.eat(self.env.food_positions)
                player.energy -= player.energy_required_for_living

    def night_phase(self):
        for night in range(NIGHT_LENGTH):
            for player in self.players:
                player.energy -= player.energy_required_for_living

    def cull(self):
        dead_players = 0
        new_players = []
        for player in self.players:
            if player.energy < player.energy_required_for_living:
                dead_players += 1
            else:
                new_players.append(player)
        self.players = new_players
        return dead_players

    def breed(self):
        player_babies = 0
        new_players = []
        for player in self.players:
            if player.energy >= player.energy_required_for_reproduction:
                player.energy //= 2
                genome_sequence = ''.join(random.choices('ATGC', k=4))
                genome = Genome(genome_sequence)
                new_players.append(Agent(random.randint(0, ENV_WIDTH - 1), random.randint(0, ENV_HEIGHT - 1), genome))
                player_babies += 1
        self.players.extend(new_players)
        return player_babies

    def get_count(self):
        return len(self.players)

    def plot_results(self):
        plt.plot(self.graph_player_points, label="players")
        plt.xlabel("Rounds")
        plt.ylabel("Population")
        plt.legend()
        plt.show()

if __name__ == "__main__":
    simulation = Simulation(ENV_WIDTH, ENV_HEIGHT, STARTING_PLAYERS, ROUNDS)
    simulation.run()
