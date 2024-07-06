import random
import matplotlib.pyplot as plt
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
                player1.gain_food(1.5)
                player2.gain_food(0.5)
                if random.random() < 0.5:
                    next_population.append(Player('Dove'))
                if player1.food >= 1.5 and random.random() < 0.5:
                    next_population.append(Player('Hawk'))
            elif player1.type == 'Dove' and player2.type == 'Hawk':
                player2.gain_food(1.5)
                player1.gain_food(0.5)
                if random.random() < 0.5:
                    next_population.append(Player('Dove'))
                if player2.food >= 1.5 and random.random() < 0.5:
                    next_population.append(Player('Hawk'))
            elif player1.type == 'Dove' and player2.type == 'Dove':
                player1.gain_food(1)
                player2.gain_food(1)
            elif player1.type == 'Hawk' and player2.type == 'Hawk':
                continue  # Both Hawks die

        for player in self.population:
            if player.food >= 1:
                next_population.append(Player(player.type))   # Survives
            # elif player.food > 0:
            #     next_population.append(Player(player.type)) 

            player.reset_food()

        self.population = next_population

    def run_simulation(self, rounds):
        hawks_count=[]
        doves_count=[]
        for round in range(rounds):
            self.pair_and_play()
            num_hawks = sum(1 for player in self.population if player.type == 'Hawk')
            num_doves = sum(1 for player in self.population if player.type == 'Dove')
            hawks_count.append(num_hawks)
            doves_count.append(num_doves)
            print(f"Round {round + 1}: Hawks = {num_hawks}, Doves = {num_doves}")

        return hawks_count,doves_count

# Initialize and run the simulation
num_hawks = 10
num_doves = 1000
rounds = 15

simulation = Simulation(num_hawks, num_doves)
hawk_counts,dove_counts=simulation.run_simulation(rounds)


# Plotting the results
plt.figure(figsize=(10, 6))
plt.plot(range(1, rounds + 1), hawk_counts, label='Hawks', color='r')
plt.plot(range(1, rounds + 1), dove_counts, label='Doves', color='b')
plt.xlabel('Rounds')
plt.ylabel('Population')
plt.title('Hawk and Dove Population vs Rounds')
plt.legend()
plt.grid(True)
plt.show()
