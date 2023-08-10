import cairo
import svgutils.transform as sg
from math import pi, sqrt, atan
from config import *

size = 535
save_size = 1000


def text(ctx, string, pos, theta=0.0, face='Georgia', font_size=14):
    ctx.save()

    ctx.set_source_rgb(1, 0, 0)
    ctx.select_font_face(face, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(font_size)

    _, _, fheight, _, _ = ctx.font_extents()
    x_off, y_off, tw, th = ctx.text_extents(string)[:4]
    nx = -tw / 2
    ny = fheight / 2

    ctx.translate(pos[0], pos[1])
    ctx.rotate(theta)
    ctx.translate(nx, ny)
    ctx.move_to(0, 0)
    ctx.show_text(string)
    ctx.restore()


def resize_svg(path, resized_size, savepath=None):
    fig = sg.fromfile(path)
    fig.set_size((f'{resized_size}', f'{resized_size}'))
    if savepath is None:
        fig.save(path)
    else:
        fig.save(savepath)


def percent_to_int_svg(path, savepath):
    with open(savepath, 'w+') as out_svg_for_pdf:
        with open(path, 'r') as svg_to_read:
            svg_data = ''.join(svg_to_read.readlines()).replace("rgb(100%, 100%, 100%)", "rgb(255, 255, 255)").replace(
                "rgb(50%, 50%, 50%)", "rgb(127, 127, 127)").replace("rgb(0%, 0%, 0%)", "rgb(0, 0, 0)").replace(
                "rgb(100%, 0%, 0%)", "rgb(255, 0, 0)").replace("rgb(0%, 0%, 100%)", "rgb(0, 0, 255)")
        out_svg_for_pdf.write(svg_data)


def create_axis(ctx, img_size):
    ctx.line_to(0, img_size / 2)
    ctx.line_to(img_size, img_size / 2)
    ctx.set_source_rgb(0.5, 0.5, 0.5)
    ctx.set_line_width(img_size / 400)
    ctx.stroke()

    ctx.line_to(img_size / 2, 0)
    ctx.line_to(img_size / 2, img_size)
    ctx.set_source_rgb(0.5, 0.5, 0.5)
    ctx.set_line_width(img_size / 400)
    ctx.stroke()


def create_surface_1d(path, savepath, points=None):
    img_size = 150

    if points:
        max_y1, max_y2, max_width = max([i[0] for i in points]), max([i[1] for i in points]), max(
            [i[2] for i in points])
        img_size = max(img_size, max_y1 * 2.4, max_y2 * 2.4, max_width * 1.2)

    surface = cairo.SVGSurface(path, img_size, img_size)
    surface_save = cairo.SVGSurface(savepath, img_size, img_size)

    ctx = cairo.Context(surface)
    sctx = cairo.Context(surface_save)

    for surf in [ctx, sctx]:
        surf.rectangle(0, 0, img_size, img_size)
        surf.set_source_rgb(1, 1, 1)
        surf.fill()

    create_axis(ctx, img_size)

    ctx.select_font_face('Georgia', cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(img_size // 38)
    _, _, fheight, _, _ = ctx.font_extents()

    if points:
        for cord_arr in points:
            y1, y2, width = cord_arr
            ctx.set_line_width(img_size / 400)
            ctx.set_source_rgb(0, 0, 0)
            ctx.rectangle(img_size / 2 - (width // 2), img_size / 2 - y1, width, y1 + y2)

            text(ctx, str(width), (img_size / 2, img_size / 2 - y1 - fheight), font_size=img_size // 38)
            text(ctx, str(width), (img_size / 2, img_size / 2 + y2 + fheight * 0.4), font_size=img_size // 38)
            text(ctx, str(y1 + y2), (img_size / 2 - width / 2 - fheight, (img_size / 2 - y1) + (y1 + y2) / 2),
                 theta=3 * pi / 2, font_size=img_size // 38)
            text(ctx, str(y1 + y2), (img_size / 2 + width / 2 + fheight * 0.4, (img_size / 2 - y1) + (y1 + y2) / 2),
                 theta=3 * pi / 2, font_size=img_size // 38)

            ctx.stroke()

            ctx.rectangle(img_size / 2 - (width // 2), img_size / 2 - y1, min(width, y1 + y2) * 0.2,
                          min(width, y1 + y2) * 0.2)
            ctx.set_source_rgba(0, 0, 1, 0.5)
            ctx.fill()

            ctx.rectangle(img_size / 2 + (width // 2) - min(width, y1 + y2) * 0.2, img_size / 2 - y1,
                          min(width, y1 + y2) * 0.2,
                          min(width, y1 + y2) * 0.2)
            ctx.set_source_rgba(0, 0, 1, 0.5)
            ctx.fill()

            ctx.rectangle(img_size / 2 - (width // 2), img_size / 2 + y2 - min(width, y1 + y2) * 0.2,
                          min(width, y1 + y2) * 0.2,
                          min(width, y1 + y2) * 0.2)
            ctx.set_source_rgba(0, 0, 1, 0.5)
            ctx.fill()

            ctx.rectangle(img_size / 2 + (width // 2) - min(width, y1 + y2) * 0.2,
                          img_size / 2 + y2 - min(width, y1 + y2) * 0.2, min(width, y1 + y2) * 0.2,
                          min(width, y1 + y2) * 0.2)
            ctx.set_source_rgba(0, 0, 1, 0.5)
            ctx.fill()

            sctx.set_line_width(img_size / 400)
            sctx.set_source_rgb(0, 0, 0)
            sctx.rectangle(img_size / 2 - (width // 2), img_size / 2 - y1, width, y1 + y2)
            sctx.stroke()

    surface.finish()
    surface.flush()

    surface_save.finish()
    surface_save.flush()

    resize_svg(path, size)
    resize_svg(savepath, 1000)
    resize_svg(path, 100, f'{svg_for_pdf_dir}/{path.split("/")[-1]}')

    percent_to_int_svg(f'{svg_for_pdf_dir}/{path.split("/")[-1]}', f'{svg_for_pdf_dir}/pdf_{path.split("/")[-1]}')


def create_surface_2d(path, savepath, points=None):
    img_size = 150

    if points:
        max_x1, max_y1, max_x2, max_y2, max_x3, max_y3, max_x4, max_y4 = max([i[0] for i in points]), max(
            [i[1] for i in points]), max([i[2] for i in points]), max([i[3] for i in points]), max(
            [i[4] for i in points]), max([i[5] for i in points]), max([i[6] for i in points]), max(
            [i[7] for i in points])

        img_size = max(img_size, max_x1 * 2.4, max_y1 * 2.4, max_x2 * 2.4, max_y2 * 2.4, max_x3 * 2.4, max_y3 * 2.4,
                       max_x4 * 2.4, max_y4 * 2.4)

    surface = cairo.SVGSurface(path, img_size, img_size)
    surface_save = cairo.SVGSurface(savepath, img_size, img_size)

    ctx = cairo.Context(surface)
    sctx = cairo.Context(surface_save)

    for surf in [ctx, sctx]:
        surf.rectangle(0, 0, img_size, img_size)
        surf.set_source_rgb(1, 1, 1)
        surf.fill()

    create_axis(ctx, img_size)

    ctx.select_font_face('Georgia', cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(img_size // 38)

    _, _, fheight, _, _ = ctx.font_extents()

    if points:
        for cord_arr in points:
            x1, y1, x2, y2, x3, y3, x4, y4 = cord_arr
            for surf in [ctx, sctx]:
                surf.line_to(img_size / 2 + x1, img_size / 2 - y1)
                surf.line_to(img_size / 2 - x2, img_size / 2 - y2)
                surf.line_to(img_size / 2 - x3, img_size / 2 + y3)
                surf.line_to(img_size / 2 + x4, img_size / 2 + y4)
                surf.line_to(img_size / 2 + x1, img_size / 2 - y1)

                surf.set_source_rgb(0, 0, 0)
                surf.set_line_width(img_size / 400)
                surf.stroke()
                surf.close_path()

        for cord_arr in points:
            x1, y1, x2, y2, x3, y3, x4, y4 = cord_arr
            x2 = -x2
            x3 = -x3
            y3 = -y3
            y4 = -y4

            def side_len(x1, y1, x2, y2):
                return round(sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2), 3)

            def calc_theta(x1, y1, x2, y2):
                return atan((y1 + y2) / (x1 + x2)) if x1 + x2 else 0 if y1 + y2 else pi/2

            text(ctx, str(side_len(x1, y1, x2, y2)), (img_size / 2 + (x2 + x1) / 2, img_size / 2 - (y1 + y2) / 2),
                 font_size=img_size // 38, theta=calc_theta(x1, y1, x2, y2))
            text(ctx, str(side_len(x2, y2, x3, y3)), (img_size / 2 + (x2 + x3) / 2, img_size / 2 - (y2 + y3) / 2),
                 font_size=img_size // 38, theta=calc_theta(x2, y2, x3, y3))
            text(ctx, str(side_len(x3, y3, x4, y4)), (img_size / 2 + (x3 + x4) / 2, img_size / 2 - (y3 + y4) / 2),
                 font_size=img_size // 38, theta=calc_theta(x3, y3, x4, y4))
            text(ctx, str(side_len(x4, y4, x1, y1)), (img_size / 2 + (x4 + x1) / 2, img_size / 2 - (y4 + y1) / 2),
                 font_size=img_size // 38, theta=calc_theta(x4, y4, x1, y1))

    surface.finish()
    surface.flush()

    surface_save.finish()
    surface_save.flush()

    resize_svg(path, size)
    resize_svg(savepath, 1000)
    resize_svg(path, 100, f'{svg_for_pdf_dir}/{path.split("/")[-1]}')

    percent_to_int_svg(f'{svg_for_pdf_dir}/{path.split("/")[-1]}', f'{svg_for_pdf_dir}/pdf_{path.split("/")[-1]}')
