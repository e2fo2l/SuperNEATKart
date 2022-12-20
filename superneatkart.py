#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module principal permettant d'entraîner et voir les générations et jouer au jeu
"""

#Standard Imports
import os
import json
import argparse

#3rd Party Imports
import numpy
import pygame
from PIL import Image
from pygame.locals import DOUBLEBUF, OPENGL
from shapely.geometry import Point, Polygon

#Neat
import neat
from neat.six_util import itervalues

#Local Imports
import inputs
import coursegfx
import courseobj
from agent import NeatAgent
from inputs import k_up, k_down, k_held

#Global Variables
MAP_COLLISION = None
CHECKPOINTS = []
BEST_SCORE = 0

def main():
    """
    Fonction principale. Parse les arguments et appelle train, watch et play
    en fonction de ces arguments.
    """

    #Argument Parsing
    assets = os.path.join(os.path.dirname(
        os.path.abspath(os.path.realpath(__file__))), "checkpoints")
    games_available = [int(i.replace("neat-checkpoint-", "")) \
    for i in os.listdir(assets) if os.path.isfile(os.path.join(assets, i))
                       and 'neat-checkpoint-' in i]
    games_available.sort()
    lastplayed = games_available[-1]

    j = {}
    with open(os.path.join(os.path.dirname(os.path.abspath( \
              os.path.realpath(__file__))), "data/maps/checkpoints.json")) as checkpoints_file:
        j = json.load(checkpoints_file)
    maps_available = list(j.keys())

    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--map", help="Map to load (Located in \"data/maps/\")",
                        choices=maps_available, metavar="X", nargs="?", const=maps_available[0])
    parser.add_argument("-t", "--train", help="Train for X generations (Unlimited if unspecified)",
                        metavar="X", nargs="?", const=99999999, type=int)
    parser.add_argument("-w", "--watch",
                        help="Watch generation X play (Last trained if unspecified)",
                        choices=games_available, metavar="X", nargs="?", const=lastplayed, type=int)
    parser.add_argument("-p", "--play", help="Play the game (no IAs)", action="store_true")
    args = parser.parse_args()

    course_map = maps_available[0]
    if args.map:
        course_map = args.map
    load_map(course_map)

    if not args.train and not args.watch and not args.play:
        print("No argument specified (use --help for more details)")
        print("Training for 1 generation and showing results.")
        watch(lastplayed, course_map)
    if args.train:
        train(load_agent(lastplayed), lastplayed, args.train)
        lastplayed += args.train
    if args.watch:
        watch(args.watch, course_map)
    if args.play:
        play(course_map)

def train(agent, generation, amount):
    """
    Entraîne le modèle pour un nombre de générations donné
    Args:
        agent: Un objet NeatAgent contenant le modèle
        generation: La génération de départ
        amount: Le nombre de générations à entraîner
    Returns:
        Le meilleur génome de la dernière génération entraînée
    """

    pygame.init()
    amount = abs(amount) # Emêche les nombres négatifs
    print("Loading generation", generation)
    if amount < 2:
        print("Training for", amount, "generation")
    else:
        print("Training for", amount, "generations")
        winner = agent.run(eval_genomes, amount-1)
        print("\nDisplaying graphs. Close the windows to save the generation.")
        agent.visualize(winner)
    agent.checkpointer.generation_interval = 1
    winner = agent.run(eval_genomes, 1) #On assure une sauvegarde sur la dernière génération

    pygame.quit()

    return winner

def watch(generation, course_map):
    """
    Affiche les 50 parties d'une génération donnée
    Args:
        generation: La génération à afficher
        course_map: Le nom de la map à charger
    """

    agent = load_agent(generation)
    winner = train(agent, generation, 1)
    gfx_init(course_map)
    play_games(MAP_COLLISION, CHECKPOINTS, agent.population.population,
               winner, agent.population.generation, 1, agent.config)
    pygame.quit()

def play(course_map):
    """
    Lance une partie contrôlée par le joueur
    Args:
        course_map: Le nom de la map à charger
    """

    gfx_init(course_map)
    inputs.update()
    play_games(MAP_COLLISION, CHECKPOINTS, None, None, 0, 2, None)
    pygame.quit()

def load_map(course_map):
    """
    Charge dans les variables globales MAP_COLLISION et
    CHECKPOINTS les données correspondantes à la map
    Args:
        course_map: Le nom de la map à charger
    """

    script_path = os.path.abspath(os.path.realpath(__file__))  # compatible interactive Python Shell
    script_dir = os.path.dirname(script_path)
    assets = os.path.join(script_dir, "data")
    global MAP_COLLISION
    MAP_COLLISION = Image.open(os.path.join(assets,
                                            os.path.join("maps", course_map +
                                            "_col.png"))).convert("RGB")

    global CHECKPOINTS
    CHECKPOINTS = []
    with open(os.path.join(assets, "maps/checkpoints.json")) as checkpoints_file:
        checkpoints = json.load(checkpoints_file)[course_map]
        for polygon in checkpoints:
            CHECKPOINTS.append(Polygon(polygon))

def load_agent(generation):
    """
    Charge un NeatAgent à la génération donnée
    Args:
        generation: La génération à charger
    Returns:
        Un objet NeatAgent chargé
    """

    script_path = os.path.abspath(os.path.realpath(__file__))
    script_dir = os.path.dirname(script_path)
    agent = NeatAgent(os.path.join(script_dir, "checkpoints"), "config")
    agent.restore(generation)
    return agent

def gfx_init(course_map):
    """
    Initialise les graphismes
    Args:
        course_map: Le nom de la map à charger
    """

    os.environ['SDL_VIDEO_CENTERED'] = '1'
    screen_size = (256, 224)
    screen_zoom = 3
    window_size = (int(screen_size[0] * screen_zoom), int(screen_size[1] * screen_zoom))
    script_path = os.path.abspath(os.path.realpath(__file__))  # compatible interactive Python Shell
    script_dir = os.path.dirname(script_path)
    assets = os.path.join(script_dir, "data")
    pygame.init()
    pygame.display.set_mode(window_size, DOUBLEBUF | OPENGL)
    coursegfx.init(window_size, course_map, (0, 0, 0, -85, 0, 0), assets)


def eval_genomes(genomes, config):
    """
    Fonction lançant une partie pour chaque génération.
    Elle est appellée pour entraîner le modèle.
    Args:
        generation: La génération à afficher
        course_map: Le nom de la map à charger
    """
    global BEST_SCORE, CHECKPOINTS, MAP_COLLISION

    for _, genome in genomes:
        score = play_games(MAP_COLLISION, CHECKPOINTS, genome, None, 0, 0, config)
        genome.fitness = score
        print(genome.fitness)
        if BEST_SCORE < score:
            BEST_SCORE = score
            print("new best score=" + str(BEST_SCORE))


def play_games(map_collision, checkpoints, population, winner, generation, mode, config):
    """
    Lance une partie
    Args:
        map_collision: Le fichier de collisions de la course
        checkpoints: Tableau contenant les "checkpoints"
        population: Soit une population de génomes, soit un seul génome
        winner: Le meilleur génome (peut être None)
        generation: Le numéro de la génération
        mode: Si 0: Entraînement; si 1: Affichage de génération; si 2: Partie jouée par le joueur
        config: Fichier de configuration du modèle
    Returns:
        Le meilleur score des parties
    """

    global BEST_SCORE
    done = False
    objs = []
    games = 0
    best_index = 0

    score = []
    networks = []
    checkpoints_passed = []
    remaining_checkpoints = []
    prev_checkpoints_passed = []
    frames_without_checkpoint = []

    if mode == 0: # Mode 0: Training
        objs.append(courseobj.Kart((64, 622, 0, 0), 8, 0))
        networks.append(neat.nn.FeedForwardNetwork.create(population, config)
                        if population is not None else None)
        objs[-1].username = "Game " + str(games)
        remaining_checkpoints.append(checkpoints.copy())
        score.append(0)
        checkpoints_passed.append(0)
        prev_checkpoints_passed.append(0)
        frames_without_checkpoint.append(0)
        games += 1

    if mode == 1: # Mode 1: Watching Generation
        for i in itervalues(population):
            if i == winner:
                best_index = games
            objs.append(courseobj.Kart((64, 622, 0, 0), 8, 0))
            networks.append(neat.nn.FeedForwardNetwork.create(i, config) if i is not None else None)
            objs[-1].username = "Game " + str(games)
            remaining_checkpoints.append(checkpoints.copy())
            score.append(0)
            checkpoints_passed.append(0)
            prev_checkpoints_passed.append(0)
            frames_without_checkpoint.append(0)
            games += 1

    if mode == 2: # Mode 2: Player playing
        objs.append(courseobj.Kart((64, 622, 0, 0), 8, 0))
        networks.append(None)
        objs[-1].username = "Player"
        remaining_checkpoints.append(checkpoints.copy())
        score.append(0)
        checkpoints_passed.append(0)
        prev_checkpoints_passed.append(0)
        frames_without_checkpoint.append(0)
        games += 1

    frame = 0
    game_state = 2
    clock = pygame.time.Clock()
    karts = [k for k in objs if k.__class__ == courseobj.Kart]
    best_smallmap = []

    while not done:
        frame += 1

        event = pygame.event.Event(pygame.USEREVENT)
        pygame.event.pump()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True

        best_outputs = []
        for j in range(len(karts)):
            frames_without_checkpoint[j] += 1
            if game_state == 2:
                kart = karts[j]
                if kart is not None:
                    smallmap = kart.generate_smallmap(map_collision)
                    if j == best_index:
                        best_smallmap = smallmap
                    state = numpy.zeros(102)
                    for smallmap_x in range(10):
                        for smallmap_y in range(10):
                            color = smallmap[smallmap_x][smallmap_y]
                            value = 0
                            # road
                            if color in ((96, 96, 96), (0, 0, 255), (255, 0, 0)):
                                value = 0.2
                            # wall
                            elif color == (255, 0, 0):
                                value = 1
                            # offroad
                            elif color == (0, 0, 0):
                                value = .95
                            # finish
                            elif color == (255, 255, 255):
                                value = 0.2
                            # boost
                            elif color == (0, 255, 0):
                                value = 0.1
                            # oil
                            elif color == (255, 0, 110):
                                value = 0.9
                            else:
                                value = 1
                            state[smallmap_x + smallmap_y * 10 + 2] = value

                    state[0] = kart.angle
                    state[1] = kart.speed

                    outputs = []
                    if mode in (0, 1):
                        outputs = networks[j].activate(state)
                    if mode == 2:
                        outputs.append(int(k_held(pygame.K_UP)))
                        outputs.append(int(k_held(pygame.K_DOWN)))
                        outputs.append(int(k_held(pygame.K_LEFT)))
                        outputs.append(int(k_held(pygame.K_RIGHT)))
                        outputs.append(int(k_held(pygame.K_LCTRL)))

                    if j == best_index:
                        best_outputs = outputs

                    input_map = {
                        pygame.K_UP: outputs[0] > .5,
                        pygame.K_DOWN: outputs[1] > .5,
                        pygame.K_LEFT: outputs[2] > .5,
                        pygame.K_RIGHT: outputs[3] > .5,
                        pygame.K_LCTRL: outputs[4] > .5,
                        pygame.K_SPACE: False
                    }
                    kart.update(map_collision, input_map)
                    if map_collision.getpixel((kart.x, kart.y)) == (0, 0, 0):
                        if score[j] > 0:
                            score[j] = max(score[j]-20, 1)
                        else:
                            score[j] -= 20
                    point = Point(kart.x, kart.y)
                    for i in range(min(9, len(remaining_checkpoints[j]))):
                        checkpoint = remaining_checkpoints[j][i]
                        if point.within(checkpoint):
                            remaining_checkpoints[j].pop(i)
                            checkpoints_passed[j] += 1
                            score[j] += (90000 - frames_without_checkpoint[j]**2)/300
                            frames_without_checkpoint[j] = 0
                            break

                    if len(remaining_checkpoints[j]) > 9:
                        for i in range(len(remaining_checkpoints[j]) - 1,
                                       len(remaining_checkpoints[j])-10, -1):
                            checkpoint = remaining_checkpoints[j][i]
                            if point.within(checkpoint):
                                score[j] -= 50
                                break

                    if (len(remaining_checkpoints[j]) <= 8 and
                            map_collision.getpixel((karts[j].x, karts[j].y)) == (255, 255, 255)):
                        print("Alors là c'est terminé " + str(frame))
                        #score[j] += (2400-frame)*10
                        score[j] = len(checkpoints)*300+(2400-frame)
                        if j == best_index:
                            return score[j]
                        karts[j] = None

                    if frames_without_checkpoint[j] == 400:
                        if j == best_index:
                            return score[j]
                        karts[j] = None

        if mode in (1, 2):
            coursegfx.draw(objs, best_index, 300 * 1000, (frame/60) * 1000,
                           "Generation: "    + str(generation) +
                           "\nBest score: "  + str(int(BEST_SCORE)) +
                           "\nScore: "       + str(int(score[best_index])),
                           best_outputs, best_smallmap)
            pygame.display.flip()
            clock.tick(60)
            inputs.update()


if __name__ == '__main__':
    main()

# くコ:彡