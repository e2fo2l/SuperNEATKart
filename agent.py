#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module permettant la gestion du modèle
"""

import os
import neat

import visualize

class NeatAgent():
    def __init__(self, assets, config_file):
        self.assets = assets
        self.config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet,
                                  neat.DefaultStagnation, os.path.join(self.assets, config_file))

        self.population = neat.Population(self.config)
        self.configure()

    def run(self, eval_genomes, generations):
        winner = self.population.run(eval_genomes, generations)
        return winner

    def visualize(self, genome):
        self.stats.save()
        visualize.draw_net(self.config, genome, True)
        visualize.plot_stats(self.stats, ylog=False, view=True)
        visualize.plot_species(self.stats, view=True)

    def restore(self, number):
        self.population = neat.Checkpointer.restore_checkpoint(os.path.join(self.assets, 'neat-checkpoint-' + str(number)))
        self.configure()

    def configure(self):
        self.population.add_reporter(neat.StdOutReporter(True))
        self.stats = neat.StatisticsReporter()
        self.population.add_reporter(self.stats)
        self.checkpointer = neat.Checkpointer(filename_prefix=os.path.join(self.assets, 'neat-checkpoint-'), generation_interval=10)
        self.population.add_reporter(self.checkpointer)

# くコ:彡