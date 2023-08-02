from flask import Flask, render_template, request, send_file, redirect, url_for
from funcs import *

app = Flask(__name__, template_folder='templates')
app.secret_key = 'bezbozhiye botforty vyvernutsya doslushat kibernetik predrassudok protivoyadiye raskrovenit slyapat'
polygons = []
points = []

last_size = 0
last_polygon_type = 1

size = 550
center = size // 2


@app.route('/')
def index():
    global polygons, points

    polygons = []
    points = []

    surface = cairo.SVGSurface('static/img/polygon.svg', size, size)

    ctx = cairo.Context(surface)

    ctx.rectangle(0, 0, size, size)
    ctx.set_source_rgb(1, 1, 1)
    ctx.fill()

    ctx.line_to(0, center)
    ctx.line_to(size, center)
    ctx.set_source_rgb(0.5, 0.5, 0.5)
    ctx.set_line_width(size / 400)
    ctx.stroke()

    ctx.line_to(center, 0)
    ctx.line_to(center, size)
    ctx.set_source_rgb(0.5, 0.5, 0.5)
    ctx.set_line_width(size / 400)
    ctx.stroke()

    surface.finish()
    surface.flush()

    surface = cairo.SVGSurface('static/img/save_polygon.svg', size, size)

    ctx = cairo.Context(surface)

    ctx.rectangle(0, 0, size, size)
    ctx.set_source_rgb(1, 1, 1)
    ctx.fill()

    ctx.line_to(0, center)
    ctx.line_to(size, center)
    ctx.set_source_rgb(0.5, 0.5, 0.5)
    ctx.set_line_width(size / 400)
    ctx.stroke()

    ctx.line_to(center, 0)
    ctx.line_to(center, size)
    ctx.set_source_rgb(0.5, 0.5, 0.5)
    ctx.set_line_width(size / 400)
    ctx.stroke()

    surface.finish()
    surface.flush()

    return redirect(url_for('add_polygon1'))


@app.route('/save_project', methods=['GET', 'POST'])
def save_project():
    global polygons

    save_surface = cairo.SVGSurface('static/img/save_polygon.svg', size, size)
    ctx = cairo.Context(save_surface)

    ctx.rectangle(0, 0, size, size)
    ctx.set_source_rgb(1, 1, 1)
    ctx.fill()

    for poly in polygons:
        for point_pair in poly:
            ctx.line_to(point_pair[0], point_pair[1])

        ctx.set_source_rgb(0, 0, 0)
        ctx.set_line_width(size / 400)
        ctx.stroke()
        ctx.close_path()

    save_surface.finish()
    save_surface.flush()

    return send_file('static/img/save_polygon.svg', download_name='polygon.svg', as_attachment=True)


@app.route('/add_polygon1', methods=['GET', 'POST'])
def add_polygon1():
    global last_size, last_polygon_type, points, polygons
    last_polygon_type = 1

    if request.method == 'POST':
        try:
            width, y2, y1 = request.form.get('width'), request.form.get('y1'), request.form.get('y2')
            if all([i is not None for i in [width, y1, y2]]):
                width, y1, y2 = int(width), int(y1), int(y2)

                image_center = (center, center)

                surface = cairo.SVGSurface('static/img/polygon.svg', size, size)

                ctx = cairo.Context(surface)

                ctx.rectangle(0, 0, size, size)
                ctx.set_source_rgb(1, 1, 1)
                ctx.fill()

                ctx.line_to(0, center)
                ctx.line_to(size, center)
                ctx.set_source_rgb(0.5, 0.5, 0.5)
                ctx.set_line_width(size / 400)
                ctx.stroke()
                ctx.close_path()

                ctx.line_to(center, 0)
                ctx.line_to(center, size)
                ctx.set_source_rgb(0.5, 0.5, 0.5)
                ctx.set_line_width(size / 400)
                ctx.stroke()
                ctx.close_path()

                polygons.append([(image_center[0] + width // 2, image_center[1] + y1),
                                 (image_center[0] - width // 2, image_center[1] + y1),
                                 (image_center[0] - width // 2, image_center[1] - y2),
                                 (image_center[0] + width // 2, image_center[1] - y2),
                                 (image_center[0] + width // 2, image_center[1] + y1)])
                points.append(
                    str(f'{(width // 2, y1)}, {(-width // 2, y1)}, {(-width // 2, -y2)}, {(width // 2, -y2)}'))

                for poly in polygons:
                    for point_pair in poly:
                        ctx.line_to(point_pair[0], point_pair[1])

                    ctx.set_source_rgb(0, 0, 0)
                    ctx.set_line_width(size / 400)
                    ctx.stroke()
                    ctx.close_path()

                for poly in polygons:
                    if len(poly) == 5:
                        center1 = (poly[1][0] - (poly[1][0] - poly[0][0]) / 2,
                                   poly[1][1] - (poly[1][1] - poly[0][1]) / 2)
                        center2 = (poly[2][0] - (poly[2][0] - poly[1][0]) / 2,
                                   poly[2][1] - (poly[2][1] - poly[1][1]) / 2)
                        center3 = (poly[3][0] - (poly[3][0] - poly[2][0]) / 2,
                                   poly[3][1] - (poly[3][1] - poly[2][1]) / 2)
                        center4 = (poly[4][0] - (poly[4][0] - poly[3][0]) / 2,
                                   poly[4][1] - (poly[4][1] - poly[3][1]) / 2)

                        text(ctx, str(calc_distance(poly[0], poly[1])), center1, calc_angle(poly[0], poly[1]),
                             font_size=10)
                        text(ctx, str(calc_distance(poly[2], poly[1])), center2, calc_angle(poly[1], poly[2]),
                             font_size=10)
                        text(ctx, str(calc_distance(poly[3], poly[2])), center3, calc_angle(poly[2], poly[3]),
                             font_size=10)
                        text(ctx, str(calc_distance(poly[4], poly[3])), center4, calc_angle(poly[3], poly[4]),
                             font_size=10)

                surface.finish()
                surface.flush()

        except Exception:
            pass

    return render_template('index.html', polygon_type=1, start=0 if len(points) <= 16 else len(points) - 16,
                           ln=len(points), points=points)


@app.route('/add_polygon2', methods=['POST'])
def add_polygon2():
    global last_size, last_polygon_type, points, polygons

    last_polygon_type = 2
    if request.method == 'POST':
        try:
            x1, x2, x3, x4, y1, y2, y3, y4 = [request.form.get(i) for i in
                                              ['x1', 'x2', 'x3', 'x4', 'y1', 'y2', 'y3', 'y4']]
            if all(i is not None for i in [x1, x2, x3, x4, y1, y2, y3, y4]):
                x1 = int(x1)
                x2 = int(x2)
                x3 = int(x3)
                x4 = int(x4)
                y1 = int(y1)
                y2 = int(y2)
                y3 = int(y3)
                y4 = int(y4)

                if all([i >= 0 for i in [x1, x2, x3, x4, y1, y2, y3, y4]]):
                    image_center = (center, center)

                    surface = cairo.SVGSurface('static/img/polygon.svg', size, size)

                    ctx = cairo.Context(surface)

                    ctx.rectangle(0, 0, size, size)
                    ctx.set_source_rgb(1, 1, 1)
                    ctx.fill()

                    ctx.line_to(0, center)
                    ctx.line_to(size, center)
                    ctx.set_source_rgb(0.5, 0.5, 0.5)
                    ctx.set_line_width(size / 400)
                    ctx.stroke()
                    ctx.close_path()

                    ctx.line_to(center, 0)
                    ctx.line_to(center, size)
                    ctx.set_source_rgb(0.5, 0.5, 0.5)
                    ctx.set_line_width(size / 400)
                    ctx.stroke()
                    ctx.close_path()

                    polygons.append([(image_center[0] + x1, image_center[1] - y1),
                                     (image_center[0] - x2, image_center[1] - y2),
                                     (image_center[0] - x3, image_center[1] + y3),
                                     (image_center[0] + x4, image_center[1] + y4),
                                     (image_center[0] + x1, image_center[1] - y1)])
                    points.append(
                        str(f'{(x1, y1)}, {(-x2, y2)}, {(-x3, -y3)}, {(x4, -y4)}'))

                    for poly in polygons:
                        for point_pair in poly:
                            ctx.line_to(point_pair[0], point_pair[1])

                        ctx.set_source_rgb(0, 0, 0)
                        ctx.set_line_width(size / 400)
                        ctx.stroke()
                        ctx.close_path()

                    for poly in polygons:
                        if len(poly) == 5:
                            center1 = (poly[1][0] - (poly[1][0] - poly[0][0]) / 2,
                                       poly[1][1] - (poly[1][1] - poly[0][1]) / 2)
                            center2 = (poly[2][0] - (poly[2][0] - poly[1][0]) / 2,
                                       poly[2][1] - (poly[2][1] - poly[1][1]) / 2)
                            center3 = (poly[3][0] - (poly[3][0] - poly[2][0]) / 2,
                                       poly[3][1] - (poly[3][1] - poly[2][1]) / 2)
                            center4 = (poly[4][0] - (poly[4][0] - poly[3][0]) / 2,
                                       poly[4][1] - (poly[4][1] - poly[3][1]) / 2)

                            text(ctx, str(calc_distance(poly[0], poly[1])), center1, calc_angle(poly[0], poly[1]), font_size=10)
                            text(ctx, str(calc_distance(poly[2], poly[1])), center2, calc_angle(poly[1], poly[2]), font_size=10)
                            text(ctx, str(calc_distance(poly[3], poly[2])), center3, calc_angle(poly[2], poly[3]), font_size=10)
                            text(ctx, str(calc_distance(poly[4], poly[3])), center4, calc_angle(poly[3], poly[4]), font_size=10)

                    surface.finish()
                    surface.flush()

        except Exception:
            pass
        return render_template('index.html', polygon_type=2, start=0 if len(points) <= 16 else len(points) - 16,
                               ln=len(points), points=points)


@app.route('/reset_project', methods=['POST'])
def reset_project():
    global polygons, points

    polygons = []
    points = []

    surface = cairo.SVGSurface('static/img/polygon.svg', size, size)

    ctx = cairo.Context(surface)

    ctx.rectangle(0, 0, size, size)
    ctx.set_source_rgb(1, 1, 1)
    ctx.fill()

    ctx.line_to(0, center)
    ctx.line_to(size, center)
    ctx.set_source_rgb(0.5, 0.5, 0.5)
    ctx.set_line_width(size / 400)
    ctx.stroke()

    ctx.line_to(center, 0)
    ctx.line_to(center, size)
    ctx.set_source_rgb(0.5, 0.5, 0.5)
    ctx.set_line_width(size / 400)
    ctx.stroke()

    surface.finish()
    surface.flush()

    return redirect(url_for('add_polygon1'))


if __name__ == "__main__":
    app.run(debug=True)