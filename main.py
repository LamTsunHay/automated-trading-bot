import datetime
import gzip
import os
import random
import neat
import pickle

from indicators import Indicators
from player import Player
import os.path
from pathlib import Path
import utils


class Trade:
    def __init__(self):
        self.indicators = Indicators()
        self.df = self.indicators.get_df()
        self.traders = Player(self.df)

    def test_ai(self, net):
        utils.result_checkdir(self.indicators.SYMBOL)
        self.df = self.indicators.get_df
        index = 0
        self.f = open(f'{self.indicators.SYMBOL}_result.csv', "a")
        while True:
            trader_info = self.traders.update()
            self.decision_to_action(net, index, trader_info.position, False)
            if index == len(self.df) - 1:
                break
            index += 1
        self.f.close()
        print(self.traders.cash_total)

    def train_ai(self, genome, config, i):
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        self.genome = genome

        index = 0
        while True:
            trader_info = self.traders.update()
            self.decision_to_action(net, index, trader_info.position, True)

            if index == len(self.df) - 1:
                profit = self.traders.close(len(self.df) - 1)
                self.genome.fitness += profit
                print(f'Genome {i+1}: {"%.2f" %self.genome.fitness}')
                break
            index += 1

    def decision_to_action(self, net, index, position, is_train):
        price, volume = self.indicators.get_past_data(index, 15)

        if position > 0:
            position = 1
        elif position < 0:
            position = -1
        output = net.activate((price[0], price[1], price[2], price[3], price[4], price[5], price[6], price[7], price[8], price[9], price[10], price[11], price[12], price[13], price[14], volume[0], volume[1], volume[2], volume[3], volume[4], volume[5], volume[6], volume[7], volume[8], volume[9], volume[10], volume[11], volume[12], volume[13], volume[14], position))
        decision = output.index(max(output))

        if decision == 0:
            if self.traders.buy(index) and not is_train:
                print(f'Buy Price: {price[-1]}')
                self.f.write(self.df.iloc[index].index, 'Buy', price[-1], 0)

        elif decision == 1:
            if self.traders.sell(index) and not is_train:
                print(f'Sell Price: {price[-1]}')
                self.f.write(self.df.iloc[index].index, 'Sell', price[-1], 0)

        elif decision == 2:
            profit = self.traders.close(index)
            if is_train:
                self.genome.fitness += profit
            else:
                print(f'Close Price: {price[-1]}, Profit: {profit}')
                self.f.write(self.df.iloc[index].index, 'Close', price[-1], profit)


def eval_genomes(genomes, config):
    for i, (genome_id, genome) in enumerate(genomes):
        genome.fitness = 0
        trade = Trade()
        trade.train_ai(genome, config, i)


def run_neat(config_path):
    p = None
    # Restore checkpoint if checkpoint exists
    if os.path.exists('neat-checkpoint-4'):
        p = neat.Checkpointer.restore_checkpoint('neat-checkpoint-4')
    else:
        p = neat.Population(config)

    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    p.add_reporter(neat.Checkpointer(5))  # overwrite checkpoint every 5 generations

    winner = p.run(eval_genomes, 5)

    with open("checkpoints/best.pickle", "wb") as f:
        pickle.dump(winner, f)


def test_best_network(config):
    with open("checkpoints/best.pickle", "rb") as f:
        winner = pickle.load(f)
    winner_net = neat.nn.FeedForwardNetwork.create(winner, config)

    trade = Trade()
    trade.test_ai(winner_net)


def start_train():
    # add training config in the first training
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config.txt')
    global config
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_path)
    run_neat(config)


if __name__ == '__main__':
    start_train()
    today = (2012, 5, 12)
    while True:
        today = utils.update_date(today)  # update df before each training
        utils.get_deque(today, 'train', 'EURUSD')  # fetch new csv to data/csv
        run_neat(config)

        # break the training loop if arrived current date
        if datetime.datetime(today[0], today[1], today[2]) > datetime.datetime(2022, 7, 14):
            break
