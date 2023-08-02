import math

import cairo
from math import sqrt, atan


def text(ctx, string, pos, theta=0.0, face='Georgia', font_size=18):
    ctx.save()

    # build up an appropriate font
    ctx.set_source_rgb(1, 0, 0)
    ctx.select_font_face(face, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(font_size)
    fascent, fdescent, fheight, fxadvance, fyadvance = ctx.font_extents()
    x_off, y_off, tw, th = ctx.text_extents(string)[:4]
    nx = -tw / 2.0
    ny = fheight / 2

    ctx.translate(pos[0], pos[1])
    ctx.rotate(theta)
    ctx.translate(nx, ny)
    ctx.move_to(0, 0)
    ctx.show_text(string)
    ctx.restore()


def calc_distance(point1, point2):
    return round(sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2), 3)


def calc_angle(point1, point2):
    dx = point2[0] - point1[0]
    if dx == 0:
        return math.pi / 2
    return atan((point2[1] - point1[1]) / dx)
