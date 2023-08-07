from flask import Flask, render_template, request, send_file
import cairo
import svgutils.transform as sg
from zipfile import ZipFile
import os

app = Flask(__name__, template_folder='templates')
app.secret_key = 'bezbozhiye botforty vyvernutsya doslushat kibernetik predrassudok protivoyadiye raskrovenit slyapat'

size = 535
center = size / 2
save_size = 1000

last_values = {
    'measurer': '',
    'date': '',
    'orderer': '',
    'phone-number': '',
    'street': '',
    'flat': '',
    'floor': '',
    'comment': ''
}

polygons_arrays = {}

polygons = []
count = 0


def resize_svg(path, size):
    fig = sg.fromfile(path)
    fig.set_size((f'{size}', f'{size}'))
    fig.save(path)


def create_surface_1d(path, savepath, points=None):
    global size

    img_size = size

    if points:
        max_y1, max_y2, max_width = max([i[0] for i in points]), max([i[1] for i in points]), max(
            [i[2] for i in points])
        img_size = max(size, max_y1 * 2.4, max_y2 * 2.4, max_width * 1.2)

    surface = cairo.SVGSurface(path, img_size, img_size)
    surface_save = cairo.SVGSurface(savepath, img_size, img_size)

    ctx = cairo.Context(surface)
    sctx = cairo.Context(surface_save)

    ctx.rectangle(0, 0, img_size, img_size)
    ctx.set_source_rgb(1, 1, 1)
    ctx.fill()
    sctx.rectangle(0, 0, img_size, img_size)
    sctx.set_source_rgb(1, 1, 1)
    sctx.fill()

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

    if points:
        for cord_arr in points:
            y1, y2, width = cord_arr
            ctx.set_line_width(img_size / 400)
            ctx.set_source_rgb(0, 0, 0)
            ctx.rectangle(img_size / 2 - (width // 2), img_size / 2 - y1, width, y1 + y2)
            ctx.stroke()
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


def create_surface_2d(path, savepath, points=None):
    global size

    img_size = size

    if points:
        max_x1, max_y1, max_x2, max_y2, max_x3, max_y3, max_x4, max_y4 = max([i[0] for i in points]), max(
            [i[1] for i in points]), max([i[2] for i in points]), max([i[3] for i in points]), max(
            [i[4] for i in points]), max([i[5] for i in points]), max([i[6] for i in points]), max(
            [i[7] for i in points])

        img_size = max(size, max_y1 * 2.4, max_y1 * 2.4, max_x2 * 2.4, max_y2 * 2.4, max_x3 * 2.4, max_y3 * 2.4,
                       max_x4 * 2.4, max_y4 * 2.4)

    surface = cairo.SVGSurface(path, img_size, img_size)
    surface_save = cairo.SVGSurface(savepath, img_size, img_size)

    ctx = cairo.Context(surface)
    sctx = cairo.Context(surface_save)

    ctx.rectangle(0, 0, img_size, img_size)
    ctx.set_source_rgb(1, 1, 1)
    ctx.fill()
    sctx.rectangle(0, 0, img_size, img_size)
    sctx.set_source_rgb(1, 1, 1)
    sctx.fill()

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

    if points:
        for cord_arr in points:
            x1, y1, x2, y2, x3, y3, x4, y4 = cord_arr

            ctx.line_to(img_size / 2 + x1, img_size / 2 - y1)
            ctx.line_to(img_size / 2 - x2, img_size / 2 - y2)
            ctx.line_to(img_size / 2 - x3, img_size / 2 + y3)
            ctx.line_to(img_size / 2 + x4, img_size / 2 + y4)
            ctx.line_to(img_size / 2 + x1, img_size / 2 - y1)

            ctx.set_source_rgb(0, 0, 0)
            ctx.set_line_width(img_size / 400)
            ctx.stroke()
            ctx.close_path()

            sctx.line_to(img_size / 2 + x1, img_size / 2 - y1)
            sctx.line_to(img_size / 2 - x2, img_size / 2 - y2)
            sctx.line_to(img_size / 2 - x3, img_size / 2 + y3)
            sctx.line_to(img_size / 2 + x4, img_size / 2 + y4)
            sctx.line_to(img_size / 2 + x1, img_size / 2 - y1)

            sctx.set_source_rgb(0, 0, 0)
            sctx.set_line_width(img_size / 400)
            sctx.stroke()
            sctx.close_path()

    surface.finish()
    surface.flush()
    surface_save.finish()
    surface_save.flush()
    resize_svg(path, size)
    resize_svg(savepath, 1000)


@app.route('/', methods=['GET', 'POST'])
def index():
    global count, polygons_arrays, polygons

    if request.method == 'POST':
        if 'add_draw' in request.form:
            last_values['measurer'] = request.form.get('measurer')
            last_values['date'] = request.form.get('date')
            last_values['orderer'] = request.form.get('orderer')
            last_values['phone-number'] = request.form.get('phone-number')
            last_values['street'] = request.form.get('address')
            last_values['flat'] = request.form.get('flat-number')
            last_values['floor'] = request.form.get('floor-number')
            last_values['comment'] = request.form.get('comments')

            if request.form.get('draw-type') == '1axis':
                polygons.append(f'1d{count}')
                create_surface_1d(f'static/img/polygon{count}.svg', f'static/img_to_save/save_polygon{count}.svg')
                polygons_arrays[f'{count}'] = []
                count += 1

            elif request.form.get('draw-type') == '2axis':
                polygons.append(f'2d{count}')
                create_surface_1d(f'static/img/polygon{count}.svg', f'static/img_to_save/save_polygon{count}.svg')
                polygons_arrays[f'{count}'] = []
                count += 1

        elif 'reset' in request.form:
            count = 0
            polygons_arrays = {}
            polygons = []

            last_values['measurer'] = ''
            last_values['date'] = ''
            last_values['orderer'] = ''
            last_values['phone-number'] = ''
            last_values['street'] = ''
            last_values['flat'] = ''
            last_values['floor'] = ''
            last_values['comment'] = ''

            for filepath in os.listdir('static/img'):
                os.remove(f'static/img/{filepath}')
            for filepath in os.listdir('static/img_to_save'):
                os.remove(f'static/img_to_save/{filepath}')
            os.remove('static/svg_zip_to_save/svg_zip.zip')

        elif "download-svg" in request.form:
            with ZipFile('static/svg_zip_to_save/svg_zip.zip', 'w') as f:
                for filepath in os.listdir('static/img_to_save'):
                    f.write(f'static/img_to_save/{filepath}')

            return send_file('static/svg_zip_to_save/svg_zip.zip')

        elif 'download-pdf' in request.form:
            pass

        else:
            post_form = request.form
            post_arr = sorted(post_form, key=lambda x: 'add_points_' in x, reverse=True)

            if 'add_points_1d_' in post_arr[0]:
                try:
                    window_id = post_arr[0][14:]

                    y1, y2, width = int(post_form[f'y1_{window_id}']), int(post_form[f'y2_{window_id}']), int(
                        post_form[f'width_{window_id}'])
                    polygons_arrays[window_id].append([y1, y2, width])
                    create_surface_1d(f'static/img/polygon{window_id}.svg',
                                      f'static/img_to_save/save_polygon{window_id}.svg',
                                      points=polygons_arrays[window_id])
                except Exception:
                    pass

            elif 'add_points_2d_' in post_arr[0]:
                try:
                    window_id = post_arr[0][14:]

                    x1, y1 = int(post_form[f'x1_{window_id}']), int(post_form[f'y1_{window_id}'])
                    x2, y2 = int(post_form[f'x2_{window_id}']), int(post_form[f'y2_{window_id}'])
                    x3, y3 = int(post_form[f'x3_{window_id}']), int(post_form[f'y3_{window_id}'])
                    x4, y4 = int(post_form[f'x4_{window_id}']), int(post_form[f'y4_{window_id}'])

                    polygons_arrays[window_id].append([x1, y1, x2, y2, x3, y3, x4, y4])
                    create_surface_2d(f'static/img/polygon{window_id}.svg',
                                      f'static/img_to_save/save_polygon{window_id}.svg',
                                      points=polygons_arrays[window_id])
                except Exception:
                    pass

    return render_template('index.html', measurer=last_values['measurer'], date=last_values['date'],
                           orderer=last_values['orderer'], phone_number=last_values['phone-number'],
                           street=last_values['street'], flat=last_values['flat'], floor=last_values['floor'],
                           comment=last_values['comment'], len=len(polygons), polygons=polygons,
                           download_access=True if polygons else False, point_arr=polygons_arrays)


if __name__ == "__main__":
    app.run(debug=True)
