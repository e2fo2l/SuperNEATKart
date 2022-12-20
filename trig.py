#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module commun contenant des fonctions trigonométriques
"""

import math
from numba import jit

@jit(nopython=True)
def cosd(angle):
    """
    Calcule le cosinus d'un angle
    Args:
        angle: Angle en °
    Returns:
        Le cosinus de l'angle
    """
    return math.cos(2*3.14159265359*angle/360)

@jit(nopython=True)
def sind(angle):
    """
    Calcule le cosinus d'un angle
    Args:
        angle: Angle en °
    Returns:
        Le cosinus de l'angle
    """
    return math.sin(2*3.14159265359*angle/360)

# くコ:彡