import random
import time
from matplotlib import pyplot as plt

# Constants
ENV_WIDTH = 100
ENV_HEIGHT = 100
FOOD_SPAWN_RATE = 1000
STARTING_DOVES = 50
STARTING_HAWKS = 50
ROUNDS = 10
DAY_LENGTH = 10
NIGHT_LENGTH = 5
STARTING_ENERGY = 300
ENERGY_REQUIRED_FOR_REPRODUCTION = 200
ENERGY_LOSS_PER_DAY = 5
ENERGY_LOSS_PER_NIGHT = 1
ENERGY_GAIN_FROM_FOOD = 50
STATUS_ACTIVE = "active"
STATUS_RESTING = "resting"
TYPE_HAWK = "hawk"
TYPE_DOVE = "dove"

class Agent:
    def __init__(self, agent_type, x, y):
        self.type = agent_type
        self.energy = STARTING_ENERGY
        self.x = x
        self.y = y
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
    def __init__(self, env_width, env_height, starting_doves, starting_hawks, rounds):
        self.env = Environment(env_width, env_height)
        self.agents = self.init_agents(starting_doves, starting_hawks)
        self.rounds = rounds
        self.graph_hawk_points = []
        self.graph_dove_points = []

    def init_agents(self, doves, hawks):
        agents = []
        for _ in range(doves):
            agents.append(Agent(TYPE_DOVE, random.randint(0, ENV_WIDTH - 1), random.randint(0, ENV_HEIGHT - 1)))
        for _ in range(hawks):
            agents.append(Agent(TYPE_HAWK, random.randint(0, ENV_WIDTH - 1), random.randint(0, ENV_HEIGHT - 1)))
        return agents

    def run(self):
        current_round = 1
        death_count = 0
        breed_count = 0

        while current_round <= self.rounds and len(self.agents) > 2:
            print(f"ROUND {current_round}")

            self.env.spawn_food()
            self.day_phase()
            self.night_phase()
            round_dead_hawks, round_dead_doves = self.cull()
            round_hawk_babies, round_dove_babies = self.breed()
            death_count += (round_dead_hawks + round_dead_doves)
            breed_count += (round_hawk_babies + round_dove_babies)

            hawk_count = self.get_agent_count_by_type(TYPE_HAWK)
            dove_count = self.get_agent_count_by_type(TYPE_DOVE)
            print(f"Hawks: {hawk_count}, Doves: {dove_count}")
            print(f"Dead hawks: {round_dead_hawks}, Dead doves: {round_dead_doves}")
            print(f"Hawk babies: {round_hawk_babies}, Dove babies: {round_dove_babies}")
            print("----")

            self.graph_hawk_points.append(hawk_count)
            self.graph_dove_points.append(dove_count)
            current_round += 1

        print("=============================================================")
        print(f"Total dead agents: {death_count}")
        print(f"Total breeding agents: {breed_count}")
        print(f"Total rounds completed: {current_round - 1}")
        print(f"Total population size: {len(self.agents)}")
        print(f"Hawks: {self.get_percentage_by_type(TYPE_HAWK)}")
        print(f"Doves: {self.get_percentage_by_type(TYPE_DOVE)}")
        print("=============================================================")

        self.plot_results()

    def day_phase(self):
        for day in range(DAY_LENGTH):
            for agent in self.agents:
                agent.move(self.env.width, self.env.height)
                agent.eat(self.env.food_positions)
                agent.energy -= ENERGY_LOSS_PER_DAY

    def night_phase(self):
        for night in range(NIGHT_LENGTH):
            for agent in self.agents:
                agent.energy -= ENERGY_LOSS_PER_NIGHT

    def cull(self):
        dead_hawks = 0
        dead_doves = 0
        self.agents = [agent for agent in self.agents if agent.energy >= 0]
        for agent in self.agents:
            if agent.energy < 0:
                if agent.type == TYPE_HAWK:
                    dead_hawks += 1
                else:
                    dead_doves += 1
        return dead_hawks, dead_doves

    def breed(self):
        hawk_babies = 0
        dove_babies = 0
        new_agents = []
        for agent in self.agents:
            if agent.energy >= ENERGY_REQUIRED_FOR_REPRODUCTION:
                baby_energy = agent.energy // 2
                agent.energy //= 2
                new_agents.append(Agent(agent.type, random.randint(0, ENV_WIDTH - 1), random.randint(0, ENV_HEIGHT - 1)))
                new_agents.append(Agent(agent.type, random.randint(0, ENV_WIDTH - 1), random.randint(0, ENV_HEIGHT - 1)))
                if agent.type == TYPE_HAWK:
                    hawk_babies += 2
                else:
                    dove_babies += 2
        self.agents.extend(new_agents)
        return hawk_babies, dove_babies

    def get_agent_count_by_type(self, agent_type):
        return sum(1 for agent in self.agents if agent.type == agent_type)

    def get_percentage_by_type(self, agent_type):
        total_agents = len(self.agents)
        if total_agents == 0:
            return '0%'
        count = self.get_agent_count_by_type(agent_type)
        return f"{(count / total_agents) * 100:.2f}%"

    def plot_results(self):
        plt.plot(self.graph_dove_points, label="Doves")
        plt.plot(self.graph_hawk_points, label="Hawks")
        plt.xlabel("Rounds")
        plt.ylabel("Population")
        plt.legend()
        plt.show()

if __name__ == "__main__":
    simulation = Simulation(ENV_WIDTH, ENV_HEIGHT, STARTING_DOVES, STARTING_HAWKS, ROUNDS)
    simulation.run()
