from flask import Flask, render_template, request
import cairo

app = Flask(__name__, template_folder='templates')
app.secret_key = 'bezbozhiye botforty vyvernutsya doslushat kibernetik predrassudok protivoyadiye raskrovenit slyapat'

size = 535
center = size / 2

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


def create_surface_1d(path, points=None, size=535, center=535 / 2):
    surface = cairo.SVGSurface(path, size, size)

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

    if points:
        for cord_arr in points:
            y1, y2, width = cord_arr
            ctx.set_line_width(size / 400)
            ctx.set_source_rgb(0, 0, 0)
            ctx.rectangle(center - (width // 2), center - y1, width, y1 + y2)
            ctx.stroke()

    surface.finish()
    surface.flush()


def create_surface_2d(path, points=None, size=535, center=535 / 2):
    surface = cairo.SVGSurface(path, size, size)

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

    if points:
        for cord_arr in points:
            x1, y1, x2, y2, x3, y3, x4, y4 = cord_arr

            ctx.line_to(center + x1, center - y1)
            ctx.line_to(center - x2, center - y2)
            ctx.line_to(center - x3, center + y3)
            ctx.line_to(center + x4,  center + y4)
            ctx.line_to(center + x1, center - y1)

            ctx.set_source_rgb(0, 0, 0)
            ctx.set_line_width(size / 400)
            ctx.stroke()
            ctx.close_path()

    surface.finish()
    surface.flush()


@app.route('/', methods=['GET', 'POST'])
def index():
    global count, polygons_arrays

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
                create_surface_1d(f'static/img/polygon{count}.svg')
                polygons_arrays[f'{count}'] = []
                count += 1

            elif request.form.get('draw-type') == '2axis':
                polygons.append(f'2d{count}')
                create_surface_1d(f'static/img/polygon{count}.svg')
                polygons_arrays[f'{count}'] = []
                count += 1

        else:
            post_form = request.form
            post_arr = sorted(post_form, key=lambda x: 'add_points_' in x, reverse=True)

            if 'add_points_1d_' in post_arr[0]:
                window_id = post_arr[0][14:]

                y1, y2, width = int(post_form[f'y1_{window_id}']), int(post_form[f'y2_{window_id}']), int(
                    post_form[f'width_{window_id}'])
                polygons_arrays[window_id].append([y1, y2, width])
                create_surface_1d(f'static/img/polygon{window_id}.svg', points=polygons_arrays[window_id])

            elif 'add_points_2d_' in post_arr[0]:
                window_id = post_arr[0][14:]

                x1, y1 = int(post_form[f'x1_{window_id}']), int(post_form[f'y1_{window_id}'])
                x2, y2 = int(post_form[f'x2_{window_id}']), int(post_form[f'y2_{window_id}'])
                x3, y3 = int(post_form[f'x3_{window_id}']), int(post_form[f'y3_{window_id}'])
                x4, y4 = int(post_form[f'x4_{window_id}']), int(post_form[f'y4_{window_id}'])

                polygons_arrays[window_id].append([x1, y1, x2, y2, x3, y3, x4, y4])
                create_surface_2d(f'static/img/polygon{window_id}.svg', points=polygons_arrays[window_id])

    return render_template('index.html', measurer=last_values['measurer'], date=last_values['date'],
                           orderer=last_values['orderer'], phone_number=last_values['phone-number'],
                           street=last_values['street'], flat=last_values['flat'], floor=last_values['floor'],
                           comment=last_values['comment'], len=len(polygons), polygons=polygons)


if __name__ == "__main__":
    app.run(debug=True)
