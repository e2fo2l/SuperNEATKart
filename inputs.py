#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module permettant la gestion des entrées de l'utilisateur (clavier et manette)
"""

import pygame
from pygame.locals import K_UP, K_DOWN, K_LEFT, K_RIGHT, K_LCTRL, K_RETURN, K_SPACE, K_ESCAPE, K_BACKSPACE

PREV_KEYS = {}
CURRENT_KEYS = {}
SUPPORTED_KEYS = [K_UP, K_DOWN, K_LEFT, K_RIGHT, K_LCTRL, K_RETURN, K_SPACE, K_ESCAPE, K_BACKSPACE]

def update():
    """
    Mettre à jour les entrées au clavier et à la manette
    """
    global PREV_KEYS, CURRENT_KEYS
    
    pressed = pygame.key.get_pressed()
    PREV_KEYS = CURRENT_KEYS
    CURRENT_KEYS = {k: pressed[k] for k in SUPPORTED_KEYS}


def k_up(i):
    """
    Permet de savoir si une touche a été relâchée
    Args:
        i: Nom de la touche à analyser
    Returns:
        True si la touche a été relâchée, False sinon

    """
    try:
        return (not CURRENT_KEYS[i]) and PREV_KEYS[i]
    except KeyError:
        return False

def k_down(i):
    """
    Permet de savoir si une touche a été pressée (une seule fois)
    Args:
        i: Nom de la touche à analyser
    Returns:
        True si la touche a été pressée, False sinon

    """
    try:
        return (not PREV_KEYS[i]) and CURRENT_KEYS[i]
    except KeyError:
        return False

def k_held(i):
    """
    Permet de savoir si une touche est maintenue
    Args:
        i: Nom de la touche à analyser
    Returns:
        True si la touche est maintenue, False sinon

    """
    try:
        return CURRENT_KEYS[i]
    except KeyError:
        return False

# くコ:彡