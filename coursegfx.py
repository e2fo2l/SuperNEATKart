import os
import math
import numba
import pygame
import random
import colorsys
import courseobj
from trig import *
from numba import jit
from pygame.locals import *

from OpenGL.GL import *
from OpenGL.GLU import *



COORDS = (0, 0, 0, 0, 0, 0)
SCREEN_SIZE = None
SCREEN_ZOOM = None

PLANE_TEX_ID = 0
OOB_TEX_ID = 0
SKY_TEX_ID = 0
OBJ_TEX_ID = 0
UI_TEX_ID = 0

def init(window_size, map_name, coords, assets):
    """
    Initialise les graphismes
    Args:
        window_size: La taille de la fenêtre
        map_name: Le nom de la map à charger
        coords: Les coordonnées de départ de la caméra
        assets: Le dossier qui contient les données
    """

    global COORDS, PLANE_TEX_ID, OOB_TEX_ID, SKY_TEX_ID, OBJ_TEX_ID, UI_TEX_ID

    gluPerspective(45, (window_size[0]/window_size[1]), 0.01, 200.0)


    PLANE_TEX_ID = init_texture(assets, "maps/" + map_name)
    OOB_TEX_ID = init_texture(assets, "maps/" + map_name + "_oob")
    SKY_TEX_ID = init_texture(assets, "sky")
    OBJ_TEX_ID = init_texture(assets, "courseobj")
    UI_TEX_ID = init_texture(assets, "ui")

    #On met en cache tous les caractères

    draw_text_3D(UI_TEX_ID, "ABCDEFGHIJKLMNOPQRSTUVWXYZ.:?_", 0, 0, 0, 0, 0)

    COORDS = coords
    glRotatef(COORDS[3], 1, 0, 0)
    glRotatef(COORDS[4], 0, 1, 0)
    glRotatef(COORDS[5], 0, 0, 1)
    glTranslatef(COORDS[0], COORDS[1], COORDS[2])


def init_texture(assets, tex_path):
    """
    Initialise la texture
    Args:
        assets: Le dossier qui contient les données
        tex_path: Chemin de la texture à charger
    """
    planeTexSurface = pygame.image.load(os.path.join(assets, tex_path + ".png"))
    planeTexData  = pygame.image.tostring(planeTexSurface, "RGBA", 1)
    (w, h) = (planeTexSurface.get_width(), planeTexSurface.get_height())
    glEnable(GL_TEXTURE_2D)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    texid = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texid)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, w, h, 0, GL_RGBA, GL_UNSIGNED_BYTE, planeTexData)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
   
    return texid

def map_plane(texid):
    """
    Dessine la course
    """

    glBindTexture(GL_TEXTURE_2D, texid)
    glBegin(GL_QUADS)
    glTexCoord2f(0, 0)
    glVertex3f(0, 0, 0)
    glTexCoord2f(0, 1)
    glVertex3f(0, 1, 0)
    glTexCoord2f(1, 1)
    glVertex3f(1, 1, 0)
    glTexCoord2f(1, 0)
    glVertex3f(1, 0, 0)
    glEnd()

def oob_plane(texid):
    """
    Dessine le sol en dehors de la course
    """

    glBindTexture(GL_TEXTURE_2D, texid)
    glBegin(GL_QUADS)
    glTexCoord2f(0, 0)
    glVertex3f(-100, -100, 0)
    glTexCoord2f(0, 25600)
    glVertex3f(-100, 100, 0)
    glTexCoord2f(25600, 25600)
    glVertex3f(100, 100, 0)
    glTexCoord2f(25600, 0)
    glVertex3f(100, -100, 0)
    glEnd()

def skybox(texid, pos):
    """
    Dessine le ciel de la course
    """

    glBindTexture(GL_TEXTURE_2D, texid)
    slices = 4
    for i in range(0, 360, slices):
        glBegin(GL_QUADS)
        glTexCoord2f(i/90, 1)
        glVertex3f(pos[0]+5*cosd(i), pos[1]+5*sind(i), 2)
        glTexCoord2f(i/90, 0)
        glVertex3f(pos[0]+5*cosd(i), pos[1]+5*sind(i), 0)
        glTexCoord2f((i+slices)/90, 0)
        glVertex3f(pos[0]+5*cosd(i+slices), pos[1]+5*sind(i+slices), 0)
        glTexCoord2f((i+slices)/90, 1)
        glVertex3f(pos[0]+5*cosd(i+slices), pos[1]+5*sind(i+slices), 2)
        glEnd()

def draw_course_obj(texid, UI_TEX_ID, COORDS, obj):
    """
    Dessine un objet sur la course (voir CourseObj)
    """

    (x, y, z, angle, viewangle) = ((obj.x/1024)-0.07*sind(COORDS[5]), 
    	                           (1-obj.y/1024)-0.07*cosd(COORDS[5]), obj.z, COORDS[5], 
                                   (COORDS[5]-obj.angle) % 360)
    rz = 0
    if obj.__class__ == courseobj.Kart:
        rz = random.random()/7000
        if (viewangle > (obj.maxframes-1)*360/obj.maxframes
        	or viewangle < 360/obj.maxframes) and obj.anim_id == 0:
            obj.flip_index += 1
            valuemax = 600
            if abs(obj.speed) >= 0.25: valuemax = 8/abs(obj.speed)
            if obj.flip_index >= valuemax:
                obj.flip_index = 0
                obj.flip = not obj.flip
        else:
            obj.flip_index = 0
            obj.flip = False

    ro = 0#random.random()/7000-0.000007143
    a = (angle + obj.size) % 360
    b = (angle - obj.size) % 360
    glBindTexture(GL_TEXTURE_2D, texid)
    glBegin(GL_QUADS)
    xp = x + 0.07*sind(a) + ro
    yp = y + 0.07*cosd(a) + ro
    xpp = x + 0.07*sind(b) + ro
    ypp = y + 0.07*cosd(b) + ro
    coordindex = (int((viewangle / 360) * obj.frames + 0.5) + obj.anim_id) % (obj.frames)
    tx = coordindex/obj.maxframes
    txp = (coordindex+1)/obj.maxframes
    ty = 1-obj.sprite_id*32/512
    typ = 1-(obj.sprite_id+1)*32/512
    if obj.flip: (tx, txp) = (txp, tx)
    h = math.sqrt((xp-xpp)**2+(yp-ypp)**2)
    glTexCoord2f(txp, typ)
    glVertex3f(xp, yp, z+rz)
    glTexCoord2f(txp, ty)
    glVertex3f(xp, yp, z+h+rz)
    glTexCoord2f(tx, ty)
    glVertex3f(xpp, ypp, z+h+rz)
    glTexCoord2f(tx, typ)
    glVertex3f(xpp, ypp, z+rz)
    glEnd()

    if obj.__class__ == courseobj.Kart:
        draw_text_3D(UI_TEX_ID, obj.username, xpp, ypp, obj.z+h+h/len(obj.username), 90-COORDS[5], h/len(obj.username))

@jit
def get_texture_coords(xy, wh):
    """
    Renvoie les coordonnées d'un point donné d'une texture
    """

    return (xy[0]/wh[0], xy[1]/wh[1])

def draw_texture_at_coords(texid, twh, txywh, pxywh):
    """
    Dessine une texture à des coordonnées spécifiées
    """

    tl = get_texture_coords((txywh[0], txywh[1]), twh)
    tr = get_texture_coords((txywh[0]+txywh[2], txywh[1]), twh)
    bl = get_texture_coords((txywh[0], txywh[1]+txywh[3]), twh)
    br = get_texture_coords((txywh[0]+txywh[2], txywh[1]+txywh[3]), twh)
    glBindTexture(GL_TEXTURE_2D, texid)
    glBegin(GL_QUADS)
    glTexCoord2f(bl[0], 1-tl[1])
    glVertex2f(pxywh[0], pxywh[1])
    glTexCoord2f(tl[0], 1-bl[1])
    glVertex2f(pxywh[0], (pxywh[1]+pxywh[3]))
    glTexCoord2f(tr[0], 1-br[1])
    glVertex2f(pxywh[0]+pxywh[2], (pxywh[1]+pxywh[3]))
    glTexCoord2f(br[0], 1-tr[1])
    glVertex2f(pxywh[0]+pxywh[2], pxywh[1])
    glEnd()

def get_char_texture_pos(c):
    """
    Renvoie la position sur la texture d'un caractère
    """

    (tx, ty) = (64, 0)
    if ord(c) >= 65 and ord(c) <= 76:
        (tx, ty) = ((ord(c)-65)*8, 48)
    elif ord(c) >= 77 and ord(c) <= 88:
        (tx, ty) = ((ord(c)-77)*8, 56)
    elif ord(c) >= 89 and ord(c) <= 90:
        (tx, ty) = ((ord(c)-89)*8, 64)
    elif ord(c) >= 48 and ord(c) <= 57:
        (tx, ty) = (16+(ord(c)-48)*8, 64)
    elif c == "_":
        (tx, ty) = (88, 0)
    elif c == ".":
        (tx, ty) = (80, 0)
    elif c == ":":
        (tx, ty) = (72, 0)
    elif c == " ":
        (tx, ty) = (56, 0)
    return (tx, ty)

char_cache = {}

def draw_text_3D(texid, text, x, y, z, angle, size):
    """
    Dessine du texte en 3D
    """

    global char_cache
    text = text.upper()
    (drawx, drawy, drawz) = (x, y, z)
    (xoffset, yoffset) = (size*sind(angle), -size*cosd(angle))
    glBindTexture(GL_TEXTURE_2D, texid)
    glBegin(GL_QUADS)
    for c in text:
        if c == "\n":
            drawz -= size
            (drawx, drawy) = (x, y)
        else:
            tpos = get_char_texture_pos(c)
            (tl, br) = ((0, 0), (0, 0))
            if c not in char_cache:
                tl = get_texture_coords(tpos, (96, 72))
                br = get_texture_coords((tpos[0]+8, tpos[1]+8), (96, 72))
                char_cache[c] = [tl, br]
            else:
                (tl, br) = char_cache[c]
            (drawxp, drawyp) = (drawx + xoffset, drawy + yoffset)
            drawzp = drawz - size
            glTexCoord2f(tl[0], 1-tl[1])
            glVertex3f(drawx,  drawy,  drawz)
            glTexCoord2f(br[0], 1-tl[1])
            glVertex3f(drawxp, drawyp, drawz)
            glTexCoord2f(br[0], 1-br[1])
            glVertex3f(drawxp, drawyp, drawzp)
            glTexCoord2f(tl[0], 1-br[1])
            glVertex3f(drawx,  drawy,  drawzp)
            (drawx, drawy) = (drawxp, drawyp)
    glEnd()


def draw_text(texid, text, x, y, size):
    """
    Dessine du texte en 2D (pour l'UI)
    """

    text = text.upper()
    (drawx, drawy) = (x, y)
    for c in text:
        if c == "\n":
            drawx = x
            drawy += size
        else:
            (tx, ty) = get_char_texture_pos(c)
            draw_texture_at_coords(texid, (96, 72), (tx, ty, 8, 8), (drawx, drawy, size, size))
            drawx += size



def draw_chrono(texid, t, x, y):
    """
    Dessine un chronomètre
    """

    m = int((t/1000) / 60) % 100
    s = int(t/1000) % 60
    ms = int(t % 1000)
    if t >= 6000000:
        m = 99
        s = 59
        ms = 999
    draw_texture_at_coords(texid, (96, 72), (8*(int(m/10)%10) , 20, 8, 14), (x+0*0.04, y, 0.04, 0.07))
    draw_texture_at_coords(texid, (96, 72), (8*(int(m) % 10)  , 20, 8, 14), (x+1*0.04, y, 0.04, 0.07))
    draw_texture_at_coords(texid, (96, 72), (8*(10)           , 20, 8, 14), (x+2*0.04, y, 0.04, 0.07))
    draw_texture_at_coords(texid, (96, 72), (8*(int(s/10)%10) , 20, 8, 14), (x+3*0.04, y, 0.04, 0.07))
    draw_texture_at_coords(texid, (96, 72), (8*(int(s) % 10)  , 20, 8, 14), (x+4*0.04, y, 0.04, 0.07))
    draw_texture_at_coords(texid, (96, 72), (8*(11)           , 20, 8, 14), (x+5*0.04, y, 0.04, 0.07))
    draw_texture_at_coords(texid, (96, 72), (8*(int(ms/100))  , 20, 8, 14), (x+6*0.04, y, 0.04, 0.07))
    draw_texture_at_coords(texid, (96, 72), (8*(int(ms/10)%10), 20, 8, 14), (x+7*0.04, y, 0.04, 0.07))

def draw_UI(texid, best, t, obj):
    """
    Dessine l'UI
    """

    #Item Box
    draw_texture_at_coords(texid, (96, 72), (0, 0, 20, 20), (0.03, 0.03, 0.175, 0.175))
    #Item
    if obj.__class__ == courseobj.Kart:
        if obj.item > 0:
            draw_texture_at_coords(texid, (96, 72), ((obj.item-1)*16, 34, 16, 14), (0.0675, 0.0675, 0.1, 0.1))
    #Best
    draw_texture_at_coords(texid, (96, 72), (21, 1, 35, 9), (0.525, 0.04, 0.105, 0.027))
    #Best Time
    draw_chrono(texid, best, 0.65, 0.04)
    #Current time
    draw_chrono(texid, t, 0.65, 0.11)
    
@jit(nopython=True)
def distance_to_camera(cx, cy, cz, ca, x, y, z):
    """
    Renvoie la distance d'un objet par rapport à la caméra
    """

    xp = x-cx
    if xp == 0:
        xp = 0.00000000001
    yp = y-cy
    distance = math.sqrt((xp)**2 + (yp)**2 + (cz-z)**2)
    return distance

def draw(objs, kartindex, best, t, debugText="", debugInputs=[], smallmap = []):
    """
    Dessine la course et les objets qui sont dessus
    Args:
        objs: Le tableau d'objets à dessiner
        kartindex: L'index de l'objet sur lequel la caméra est centrée
        best: Le meilleur temps
        t: Le temps actuel
        debugText: Le texte à afficher
        debugInputs: Les entrées de utilisateur à afficher
        smallmap: La carte des collisions à afficher
    """

    global COORDS, PLANE_TEX_ID, OOB_TEX_ID, SKY_TEX_ID, OBJ_TEX_ID, UI_TEX_ID

    kart = objs[kartindex]

    old_coords = COORDS
    COORDS = ((kart.x/1024)-0.07*sind(kart.angle), (1-kart.y/1024)-0.07*cosd(kart.angle), 0.03, COORDS[3], COORDS[4], kart.angle)

    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

    glTranslatef(old_coords[0], old_coords[1], old_coords[2])
    glRotatef(old_coords[5], 0, 0, -1)
    glRotatef(old_coords[4], 0, -1, 0)
    glRotatef(old_coords[3], -1, 0, 0)
    glRotatef(COORDS[3], 1, 0, 0)
    glRotatef(COORDS[4], 0, 1, 0)
    glRotatef(COORDS[5], 0, 0, 1)
    glTranslatef(-COORDS[0], -COORDS[1], -COORDS[2])


    #print(COORDS)

    skybox(SKY_TEX_ID, (COORDS[0], COORDS[1]))
    oob_plane(OOB_TEX_ID)
    map_plane(PLANE_TEX_ID)

    objs_distance = sorted(objs, key=lambda x: distance_to_camera(COORDS[0], COORDS[1], COORDS[2], COORDS[5], (x.x/1024), (1-x.y/1024), x.z), reverse=True)

    start = max(0, len(objs_distance) - 500)
    end = len(objs_distance)
    name_angle = -kart.angle+90 
    for o in range(start, end):
        if objs[o] != None:
            draw_course_obj(OBJ_TEX_ID, UI_TEX_ID, COORDS, objs_distance[o])
            #if objs[o].__class__ == courseobj.Kart and o < 10:
            #    name_size  = len(objs[o].username)*0.00125/2
            #    draw_text_3D(UI_TEX_ID, objs[o].username, (objs[o].x/1024)-name_size*sind(name_angle),
            #                                          (1-objs[o].y/1024)+name_size*cosd(name_angle), objs[o].z+0.0125, 
            #                                          name_angle, 0.00125)

    #2D GUI
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1, 1, 0)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    draw_UI(UI_TEX_ID, best, t, kart)
    if debugText != "":
        draw_text(UI_TEX_ID, debugText, 0.03, 0.21, 0.03)
    if debugInputs != []:
        draw_text(UI_TEX_ID, "Inputs:", 0.03, 0.3, 0.03)
        if debugInputs[0] > 0.5:
            draw_text(UI_TEX_ID, "UP", 0.03, 0.33, 0.03)
        if debugInputs[1] > 0.5:
            draw_text(UI_TEX_ID, "DOWN", 0.03, 0.36, 0.03)
        if debugInputs[2] > 0.5:
            draw_text(UI_TEX_ID, "LEFT", 0.03, 0.39, 0.03)
        if debugInputs[3] > 0.5:
            draw_text(UI_TEX_ID, "RIGHT", 0.03, 0.42, 0.03)
        if len(debugInputs) > 4:
            if debugInputs[4] > 0.5:
                draw_text(UI_TEX_ID, "CTRL", 0.03, 0.45, 0.03)
        if len(debugInputs) > 5:
            if debugInputs[5] > 0.5:
                draw_text(UI_TEX_ID, "SPACE", 0.03, 0.48, 0.03)

    if smallmap != []:
        glBindTexture(GL_TEXTURE_2D, 0)
        glBegin(GL_QUADS)
        for y in range(0, 10): #x = 0.65, y = 0.2
            for x in range(0, 10):
                bc = (0.7+0.025*x, 0.2+0.025*y)
                glColor3f(smallmap[x][y][0]/255, smallmap[x][y][1]/255, smallmap[x][y][2]/255)
                glVertex2f(bc[0]      , bc[1])
                glVertex2f(bc[0]      , bc[1]+0.025)
                glVertex2f(bc[0]+0.025, bc[1]+0.025)
                glVertex2f(bc[0]+0.025, bc[1])
        glEnd()
        glColor(255, 255, 255)

    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glPopMatrix()

# くコ:彡