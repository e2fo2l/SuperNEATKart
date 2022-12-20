#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module contenant les différents types d'objets présents
sur la course (karts, bananes, carapaces, etc...)
"""


import pygame
from numpy import arange

from trig import cosd, sind


class CourseObj:
    """
    Objet par défaut, ne fait rien quand il est mis à jour.
    """
    x = 0
    y = 0
    z = 0
    angle = 0
    anim_id = 0
    sprite_id = 0
    frames = 1
    maxframes = 22
    size = 3
    flip = False
    flip_index = 0


    def __init__(self, coords, sprite_id, anim_id):
        self.x = coords[0]
        self.y = coords[1]
        self.z = coords[2]
        self.angle = coords[3]
        self.sprite_id = sprite_id
        self.anim_id = anim_id

    def update(self, map1_collision, inputs):
        pass


class Kart(CourseObj):
    """
    Objet de type Kart. Avance en fonction des entrées fournies.
    """
    username = "Mario"
    frames = 22
    state = 0
    speed = 0
    acceleration = 0
    item = 0
    size = 4.5
    drift = 0

    def __init__(self, coords, sprite_id, anim_id):
        super().__init__(coords, sprite_id, anim_id)
        self.frameflaque = 0
        self.prevx = 0
        self.prevy = 0
        self.maxspeed = 2.5
        self.zspeed = 0
        self.speed = 0
        self.drifting = False
        self.tourne_dest = 0
        self.tourne_frames = 0
        self.smallmap = []
        for _ in range(10):
            self.smallmap.append([0]*10)

    def generate_smallmap(self, map1_collision):

        a = 90-self.angle
        ca = cosd(a)
        sa = sind(a)
        for Y in range(0, 10):
            for X in range(0, 10):
                XP = 20*(X-1)
                YP = 15*(Y-5)
                smallmap_x = self.x + XP*ca + YP*sa
                smallmap_y = self.y - XP*sa + YP*ca
                if smallmap_x >= 0 and smallmap_x < 1024 and smallmap_y >= 0 and smallmap_y < 1024:
                    self.smallmap[Y][9-X] = map1_collision.getpixel((smallmap_x, smallmap_y))
                else:
                    self.smallmap[Y][9-X] = (255, 0, 0)

        return self.smallmap

    def update(self, map1_collision, inputs):

        #Empêche de sortir de la course
        if self.x <= 8:
            self.x = 12
        if self.x >= 1016:
            self.x = 1012
        if self.y <= 8:
            self.y = 12
        if self.y >= 1016:
            self.y = 1012

        if self.x >= 5 and self.y >= 5 and self.x < 1020 and self.y < 1020:
            xmax = self.x + self.speed * sind(self.angle)
            ymax = self.y - self.speed * cosd(self.angle)
            collision = map1_collision.getpixel((int(xmax), int(ymax)))
        # print(collision)
        else:
            collision = (255, 0, 0)
        # PISTE
        if collision == (96, 96, 96):
            self.state = 1
            self.maxspeed = 2.5
        # HORS PISTE
        if collision == (0, 0, 0):
            self.state = 1
            self.maxspeed = 1.2
            self.drifting = False
        # BOOST
        if collision == (0, 255, 0) or inputs[pygame.K_SPACE]:
            self.state = 2
            self.speed = 6
            self.maxspeed = 2.5
        # FLAQUE D'HUILE
        if collision == (255, 0, 110) or self.frameflaque != 0:
            if self.frameflaque == 0:
                self.frameflaque = 90
            self.frameflaque -= 1
            self.speed = 1.2
            self.maxspeed = 2.5
            self.state = 3
            self.drifting = False
        # FAIRE TOURNER LE KART PAS LA CAM
        # MUR
        if collision == (255, 0, 0):
            self.state = 2
            self.drifting = False
            if self.speed > 0.3:
                self.speed = self.speed / (-5)
            elif self.speed != 0:
                self.speed = self.speed / abs(self.speed) * -0.15
            else:
                self.speed = -0.15
        else:
            (self.prevx, self.prevy) = (self.x, self.y)

        if self.state == 1 or self.state == 2:
            # Accélération
            if inputs[pygame.K_UP]:
                if self.speed <= self.maxspeed:
                    self.speed = min(self.speed + 0.013, self.maxspeed)
                else:
                    self.speed = max(self.speed - 0.038, self.maxspeed)
            # Recul
            elif inputs[pygame.K_DOWN]:
                if self.speed > (self.maxspeed) / -3:
                    self.speed = max(self.speed - 0.063, (self.maxspeed) / -3)
            # Décélération
            else:
                if self.speed > 0 and self.speed <= self.maxspeed:
                    self.speed = max(self.speed - 0.02, 0)
                elif self.speed > self.maxspeed:
                    self.speed = max(self.speed - 0.063, self.maxspeed)
                else:
                    self.speed = min(self.speed + 0.038, 0)

            #Dérapage
            if inputs[pygame.K_LCTRL] and self.speed > 1.25 and self.state == 1:
                # Derapage gauche
                if ((inputs[pygame.K_LEFT] and self.drift == 0) or self.drift == 1):
                    self.drift = 2
                    self.tourne_dest = 3
                    if self.zspeed == 0 and not self.drifting:
                        self.zspeed = 0.0005
                        self.drifting = True
                    self.angle = (self.angle - 1.3) % 3600
                    if inputs[pygame.K_LEFT]:
                        self.x += self.speed / 6 * sind(self.angle - 90)
                        self.y -= self.speed / 6 * cosd(self.angle - 90)
                    elif inputs[pygame.K_RIGHT]:
                        self.x += self.speed / 6 * sind(self.angle + 90)
                        self.y -= self.speed / 6 * cosd(self.angle + 90)
                # Derapage droit
                if ((inputs[pygame.K_RIGHT] and self.drift == 0) or self.drift == -1):
                    self.drift = -2
                    self.tourne_dest = -3
                    if self.zspeed == 0 and not self.drifting:
                        self.zspeed = 0.0005
                        self.drifting = True
                    self.angle = (self.angle + 1.3) % 3600
                    if inputs[pygame.K_LEFT]:
                        self.x += self.speed / 6 * sind(self.angle - 90)
                        self.y -= self.speed / 6 * cosd(self.angle - 90)
                    elif inputs[pygame.K_RIGHT]:
                        self.x += self.speed / 6 * sind(self.angle + 90)
                        self.y -= self.speed / 6 * cosd(self.angle + 90)

            # Tourner Gauche/Droite
            elif inputs[pygame.K_LEFT]:
                self.angle = (self.angle - 1.0) % 360
                if self.tourne_dest != -3:
                    self.tourne_dest = 2
                #elif self.tourne_dest < -2:
                #    self.tourne_dest = -2
            elif inputs[pygame.K_RIGHT]:
                self.angle = (self.angle + 1.0) % 360
                if self.tourne_dest != 3:
                    self.tourne_dest = -2
                #elif self.tourne_dest > 2:
                #    self.tourne_dest = 2

            if not inputs[pygame.K_LCTRL]:
                self.drifting = False

            if (not inputs[pygame.K_LEFT]) and (not inputs[pygame.K_RIGHT]):
                self.tourne_dest = 0

            if self.tourne_frames % 3 == 0:
                if self.anim_id > self.tourne_dest:
                    self.anim_id -= 1
                if self.anim_id < self.tourne_dest:
                    self.anim_id += 1

            self.tourne_frames += 1

        if self.drift > 0:
            self.drift -= 1
        if self.drift < 0:
            self.drift += 1

        incrementation = 0.1
        if self.speed < 0:
            incrementation = -0.1

        for i in arange(0, self.speed, incrementation):
            collision = map1_collision.getpixel(
                (int(self.x + i * sind(self.angle)), int(self.y + i * cosd(self.angle))))
            if collision == (255, 0, 0):
                (self.x, self.y) = (self.prevx, self.prevy)
                break
        else:
            self.x += self.speed * sind(self.angle)
            self.y -= self.speed * cosd(self.angle)

        self.z += self.zspeed
        if self.z <= 0:
            self.z = 0
            self.zspeed = 0
        if self.z >= 0.0025:
            self.zspeed = -0.0005


class ItemBox(CourseObj):
    """
    Une boîte à objet qui donne un objet aléatoire au contact d'un Kart.
    Lorsqu'un contact se produit, la caisse disparaît pendant plusieurs secondes.
    """
    hue = 0
    frames = 20
    speed = 4

    def update(self, map1_collision, inputs):
        self.angle = (self.angle + self.speed) % 360

class GreenShell(CourseObj):
    """
    Une carapace qui rebondit contre les murs.
    Au bout de 5 rebonds, ou à la collision contre
    un Kart, la carapace se détruit.
    """
    speed = 3
    def update(self, map1_collision, inputs):
        self.x += self.speed*sind(self.angle)
        self.y -= self.speed*cosd(self.angle)

class Banana(CourseObj):
    """
    Une banane qui ne bouge pas et reste toute la course.
    Se détruit au contact d'un Kart.
    """
    pass

# くコ:彡