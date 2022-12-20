#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Outil permettant la génération simple de checkpoints pour les courses
"""


import os
import sys
import math
import json
import pygame


def main(opened_map):
    """
    Lance l'outil
    Args:
        opened_map: Nom de la course à modifier (sans extension)
    """

    os.environ['SDL_VIDEO_CENTERED'] = '1'
    window_size = (918, 868)

    script_path = os.path.abspath(os.path.realpath(__file__))  # compatible interactive Python Shell
    script_dir  = os.path.dirname(script_path)
    assets = os.path.join(script_dir, "data")

    pygame.init()
    screen = pygame.display.set_mode(window_size)

    ui_spr  = pygame.image.load(os.path.join(assets, "gencheckpoints.png"))
    map_spr = pygame.image.load(os.path.join(assets, "maps/" + opened_map + ".png"))

    checkpoints = []
    sel = [(0, 0), (0, 0)]

    mode = 0
    done = False
    while not done:
        event = pygame.event.Event(pygame.USEREVENT)
        pygame.event.pump()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True

        screen.fill((0, 0, 0))

        screen.blit(ui_spr, (868, 0))
        screen.blit(pygame.transform.scale(map_spr, (768, 768)), (50, 50))

        mpos = pygame.mouse.get_pos()

        if mode == 0:
            if pygame.mouse.get_pressed()[0]:
                if mpos[0] >= 868 and mpos[0] < 918:
                    if mpos[1] < 50: #Plus
                        mode = 1
                    if mpos[1] >= 50 and mpos[1] < 100 and len(checkpoints) > 0: #Moins
                        mode = 5
                        checkpoints.remove(checkpoints[-1])

                    if mpos[1] >= 100 and mpos[1] <= 150: #Save
                        mode = 5
                        checkpoints_scaled = []
                        for c in checkpoints:
                            checkpoints_scaled.append([(int((c[0][0]-50)*(1024/768)), int((c[0][1]-50)*(1024/768))),
                                                       (int((c[1][0]-50)*(1024/768)), int((c[1][1]-50)*(1024/768))),
                                                       (int((c[2][0]-50)*(1024/768)), int((c[2][1]-50)*(1024/768))),
                                                       (int((c[3][0]-50)*(1024/768)), int((c[3][1]-50)*(1024/768)))])
                        j = {}
                        with open(os.path.join(assets, "maps/checkpoints.json")) as f:
                            j = json.load(f)
                        j[opened_map] = checkpoints_scaled
                        with open(os.path.join(assets, "maps/checkpoints.json"), "w") as f:
                            json.dump(j, f)
                        print("Saved")

        if mode == 1:
            if not pygame.mouse.get_pressed()[0]:
                mode = 2

        if mode == 2:
            if pygame.mouse.get_pressed()[0] and mpos[0] < 868:
                sel[0] = mpos
                mode = 3

        if mode == 3:
            sel[1] = mpos
            theta = math.atan2(sel[1][1]-sel[0][1], sel[1][0] - sel[0][0])
            ox = 3*math.sin(theta)
            oy = 3*math.cos(theta)
            poly = [(sel[0][0]+ox, sel[0][1]-oy), (sel[0][0]-ox, sel[0][1]+oy), (sel[1][0]-ox, sel[1][1]+oy), (sel[1][0]+ox, sel[1][1]-oy)]
            pygame.draw.polygon(screen, (255, 0, 255), poly)
            if not pygame.mouse.get_pressed()[0]:
                checkpoints.append(poly)
                mode = 0


        if mode == 5:
            if not pygame.mouse.get_pressed()[0]:
                mode = 0

        for p in checkpoints:
            pygame.draw.polygon(screen, (255, 0, 255), p)

        pygame.display.flip()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Spécifier le nom d'une map en paramètre")
        sys.exit()
    main(sys.argv[1].split(".png")[0])

# くコ:彡