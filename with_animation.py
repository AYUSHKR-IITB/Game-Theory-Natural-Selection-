import random
import time
from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation

# Constants
ENV_WIDTH = 100
ENV_HEIGHT = 100
FOOD_SPAWN_RATE = 500
STARTING_PLAYERS = 50
ROUNDS = 50
DAY_LENGTH = 15
NIGHT_LENGTH = 5
ENERGY_LOSS_PER_NIGHT = 10
ENERGY_LOSS_PER_DAY = 25
STARTING_ENERGY = 150
ENERGY_GAIN_FROM_FOOD = 35
BASE_ENERGY_REQUIRED_FOR_LIVING = 100
BASE_ENERGY_REQUIRED_FOR_REPRODUCTION = 200
STATUS_ACTIVE = "active"
STATUS_RESTING = "resting"
MUTATION_PROBABILITY=0.1
# increase no. of ilteration in a day so that population get chance to eat food.
def mutate_genome_sequence(sequence):
    sequence_list = list(sequence)
    for i in range(len(sequence_list)):
        if random.random() < MUTATION_PROBABILITY:
            sequence_list[i] = random.choice('ATGC')
    return ''.join(sequence_list)
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
        # print(self.fitness)
        self.fitness_factor = 1 / (self.fitness)  # Inverse proportion
        self.energy_required_for_living = BASE_ENERGY_REQUIRED_FOR_LIVING 
        self.energy_required_for_reproduction = BASE_ENERGY_REQUIRED_FOR_REPRODUCTION 
        # print(self.energy_required_for_living,self.energy_required_for_reproduction)
        self.status = STATUS_ACTIVE

    def move(self, env_width, env_height):
        self.x = (self.x + random.choice([-1, 0, 1])) % env_width
        self.y = (self.y + random.choice([-1, 0, 1])) % env_height
        # print(self.x,self.y)

    def eat(self, food_positions):
        if (self.x, self.y) in food_positions:
            # print("yes")
            self.energy += ENERGY_GAIN_FROM_FOOD
            # print(self.energy)
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
            # print(genome_sequence)
            genome = Genome(genome_sequence)
            players_list.append(Agent(random.randint(0, ENV_WIDTH - 1), random.randint(0, ENV_HEIGHT - 1), genome))
        return players_list

    
    def run(self):
        fig, ax = plt.subplots()
        ax.set_xlim(0, ENV_WIDTH)
        ax.set_ylim(0, ENV_HEIGHT)

        player_scat = ax.scatter([player.x for player in self.players], 
                          [player.y for player in self.players], 
                          c='blue', marker='*')

        food_scat = ax.scatter([food[0] for food in self.env.food_positions],
                               [food[1] for food in self.env.food_positions],
                               c='green',marker=".")

        def update(frame):
            # Simulate a day
            for _ in range(DAY_LENGTH):
                for player in self.players:
                    player.move(self.env.width, self.env.height)
                    player.eat(self.env.food_positions)
                    player.energy -= player.energy_required_for_living/DAY_LENGTH

                # self.normalize_fitness_values()
                self.cull()
                self.breed()

                xdata = [player.x for player in self.players]
                ydata = [player.y for player in self.players]

                player_scat.set_offsets(list(zip(xdata, ydata)))

                food_xdata = [food[0] for food in self.env.food_positions]
                food_ydata = [food[1] for food in self.env.food_positions]
                food_scat.set_offsets(list(zip(food_xdata, food_ydata)))

            # Simulate a night
            for _ in range(NIGHT_LENGTH):
                for player in self.players:
                    player.energy -= player.energy_required_for_living/NIGHT_LENGTH

            # Spawn new food for the next day
            self.env.spawn_food()
            return player_scat, food_scat

        animation = FuncAnimation(fig, update, frames=range(self.rounds), blit=True, repeat=False)
        plt.show()

    def day_phase(self):
        for day in range(DAY_LENGTH):
            for player in self.players:
                player.move(self.env.width, self.env.height)
                player.eat(self.env.food_positions)
                # print(player.genome.sequence)
                player.energy -= ENERGY_LOSS_PER_DAY/DAY_LENGTH
                # [print(player.energy)]
            # self.plot_environment(day) 
            yield

    def night_phase(self):
        for night in range(NIGHT_LENGTH):
            for player in self.players:
                player.energy -= ENERGY_LOSS_PER_NIGHT/NIGHT_LENGTH
                
        yield

    def cull(self):
        dead_players = 0
        new_players = []
        total_fitness = sum(player.fitness for player in self.players)
    
        for player in self.players:
            survival_probability = player.fitness*20 / total_fitness
            # print(survival_probability,random.random())
            # print(player.fitness)
            # print(player.energy,player.genome)
            if player.energy < player.energy_required_for_living or random.random() > survival_probability:
                dead_players += 1
                # print("dead")
            else:
                new_players.append(player)
                # print("append")
        self.players = new_players
        return dead_players

    def breed(self):
        player_babies = 0
        new_players = []

        total_fitness = sum(player.fitness for player in self.players)
        
        for player in self.players:
            reproduction_probability = player.fitness*20 / total_fitness
            if player.energy >= player.energy_required_for_reproduction and random.random() <= reproduction_probability:
                player.energy //= 2
                genome_sequence =mutate_genome_sequence(player.genome.sequence)
                # print(player.genome.sequence,genome_sequence)
                genome = Genome(genome_sequence)
                new_players.append(Agent(random.randint(0, ENV_WIDTH - 1), random.randint(0, ENV_HEIGHT - 1), genome))
                player_babies += 1

        self.players.extend(new_players)
        return player_babies


    def get_count(self):
        return len(self.players)
    
    def plot_environment(self, day):
        plt.figure(figsize=(8, 8))
        plt.xlim(0, ENV_WIDTH)
        plt.ylim(0, ENV_HEIGHT)

        food_x, food_y = zip(*self.env.food_positions)
        plt.scatter(food_x, food_y, c='green', label='Food', marker='*')

        player_x = [player.x for player in self.players]
        player_y = [player.y for player in self.players]
        plt.scatter(player_x, player_y, c='blue', label='Players', marker='x')

        plt.title(f"Day {day}")
        plt.legend()
        plt.grid()
        plt.show()
        plt.show(block=False)
        plt.close('all')

    def plot_results(self):
        plt.plot(self.graph_player_points, label="players")
        plt.xlabel("Rounds")
        plt.ylabel("Population")
        plt.legend()
        plt.show()

if __name__ == "__main__":
    simulation = Simulation(ENV_WIDTH, ENV_HEIGHT, STARTING_PLAYERS, ROUNDS)
    simulation.run()
