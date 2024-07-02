import random

class Player:
    def __init__(self, type):
        self.type = type
        self.food = 0

    def reset_food(self):
        self.food = 0

    def gain_food(self, amount):
        self.food += amount

class Simulation:
    def __init__(self, num_hawks, num_doves):
        self.population = [Player('Hawk') for _ in range(num_hawks)] + [Player('Dove') for _ in range(num_doves)]

    def pair_and_play(self):
        random.shuffle(self.population)
        next_population = []

        for i in range(0, len(self.population), 2):
            if i + 1 >= len(self.population):
                break

            player1 = self.population[i]
            player2 = self.population[i + 1]

            if player1.type == 'Hawk' and player2.type == 'Dove':
                player1.gain_food(2)
                player2.food = 0
            elif player1.type == 'Dove' and player2.type == 'Hawk':
                player2.gain_food(2)
                player1.food = 0
            elif player1.type == 'Dove' and player2.type == 'Dove':
                player1.gain_food(1)
                player2.gain_food(1)
            elif player1.type == 'Hawk' and player2.type == 'Hawk':
                player1.food = 0
                player2.food = 0

        for player in self.population:
            if player.food >= 2:
                next_population.append(Player(player.type))
                next_population.append(Player(player.type))
            elif player.food > 0:
                next_population.append(Player(player.type))
            player.reset_food()
            

        self.population = next_population

    def run_simulation(self, rounds):
        for round in range(rounds):
            self.pair_and_play()
            num_hawks = sum(1 for player in self.population if player.type == 'Hawk')
            num_doves = sum(1 for player in self.population if player.type == 'Dove')
            print(f"Round {round + 1}: Hawks = {num_hawks}, Doves = {num_doves}")

# Initialize and run the simulation
num_hawks = 5
num_doves = 51
rounds = 10

simulation = Simulation(num_hawks, num_doves)
simulation.run_simulation(rounds)
