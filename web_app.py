from flask import Flask, render_template, request, send_file
import cairo
import svgutils.transform as sg
from zipfile import ZipFile
import os
from fpdf import FPDF
from math import pi

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


def text(ctx, string, pos, theta=0.0, face='Georgia', font_size=14):
    ctx.save()

    ctx.set_source_rgb(1, 0, 0)
    ctx.select_font_face(face, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(font_size)

    fascent, fdescent, fheight, fxadvance, fyadvance = ctx.font_extents()
    x_off, y_off, tw, th = ctx.text_extents(string)[:4]
    nx = -tw / 2
    ny = fheight / 2

    ctx.translate(pos[0], pos[1])
    ctx.rotate(theta)
    ctx.translate(nx, ny)
    ctx.move_to(0, 0)
    ctx.show_text(string)
    ctx.restore()


def resize_svg(path, size, savepath=None):
    fig = sg.fromfile(path)
    fig.set_size((f'{size}', f'{size}'))
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
    ctx.set_source_rgba(255, 255, 255, 1)
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

    ctx.set_source_rgb(1, 0, 0)
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
    resize_svg(path, 100, f'static/svg_for_pdf/{path[11:]}')

    percent_to_int_svg(f'static/svg_for_pdf/{path[11:]}', f'static/svg_for_pdf/pdf_{path[11:]}')


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
    resize_svg(path, 100, f'static/svg_for_pdf/{path[11:]}')

    percent_to_int_svg(f'static/svg_for_pdf/{path[11:]}', f'static/svg_for_pdf/pdf_{path[11:]}')


@app.route('/', methods=['GET', 'POST'])
def index():
    global count, polygons_arrays, polygons

    def ask_fields():
        measurer = request.form.get('measurer')
        date = request.form.get('date')
        orderer = request.form.get('orderer')
        phone = request.form.get('phone-number')
        address = request.form.get('address')
        flat = request.form.get('flat-number')
        floor = request.form.get('floor-number')
        comments = request.form.get('comments')

        last_values['measurer'] = measurer if measurer else last_values['measurer']
        last_values['date'] = date if date else last_values['date']
        last_values['orderer'] = orderer if orderer else last_values['orderer']
        last_values['phone-number'] = phone if phone else last_values['phone-number']
        last_values['street'] = address if address else last_values['street']
        last_values['flat'] = flat if flat else last_values['flat']
        last_values['floor'] = floor if floor else last_values['floor']
        last_values['comment'] = comments if comments else last_values['comment']

    if request.method == 'POST':
        if 'add_draw' in request.form:
            ask_fields()
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
            for filepath in os.listdir('static/svg_zip_to_save'):
                os.remove(f'static/svg_zip_to_save/{filepath}')
            for filepath in os.listdir('static/svg_for_pdf'):
                os.remove(f'static/svg_for_pdf/{filepath}')
            for filepath in os.listdir('static/pdf'):
                os.remove(f'static/pdf/{filepath}')

        elif "download-svg" in request.form:
            ask_fields()
            with ZipFile('static/svg_zip_to_save/svg_zip.zip', 'w') as f:
                for filepath in os.listdir('static/img_to_save'):
                    f.write(f'static/img_to_save/{filepath}')

            return send_file('static/svg_zip_to_save/svg_zip.zip')

        elif 'download-pdf' in request.form:
            ask_fields()

            pdf = FPDF()
            pdf.add_font('DejaVu', '', 'static/fonts/DejaVuSansCondensed.ttf', uni=True)

            for i in [i for i in os.listdir('static/svg_for_pdf') if i[:3] == 'pdf']:
                try:
                    pdf.add_page()

                    pdf.set_font('DejaVu', '', 10)
                    pdf.write_html(f"""
                        Замерщик: {last_values["measurer"] if last_values["measurer"] else '-'}&nbsp;&nbsp;&nbsp;&nbsp;
                        Дата: {last_values["date"] if last_values["date"] else '-'}<br>
                        Заказчик: {last_values["orderer"] if last_values["orderer"] else '-'} &nbsp;&nbsp;&nbsp;&nbsp; 
                        Телефон: {last_values["phone-number"] if last_values["phone-number"] else '-'} &nbsp;&nbsp;&nbsp;&nbsp; 
                        Улица: {last_values["street"] if last_values["street"] else '-'} &nbsp;&nbsp;&nbsp;&nbsp; 
                        Квартира: {last_values["flat"] if last_values["flat"] else '-'} &nbsp;&nbsp;&nbsp;&nbsp; 
                        Этаж: {last_values["floor"] if last_values["floor"] else '-'} &nbsp;&nbsp;&nbsp;&nbsp;<br>
                        Комментарий: {last_values["comment"] if last_values["comment"] else '-'}<br><br><br>
                        <br><br><br><br>
                        <img src={"static/svg_for_pdf/" + i}>
                        <br><br><br><br>
                        Заданные фигуры:<br><br>
                        {"<br><br>".join([f'{(i[0], i[1])}, {(i[2], i[3])}, {(i[4], i[5])}, {(i[6], i[7])}' if len(i) == 8 else f'y1: {i[0]} y2: {i[1]} width: {i[2]}' for i in polygons_arrays[i[11:][:-4]]])}
                    """)
                except Exception:
                    pass

            pdf.output('static/pdf/out.pdf')

            return send_file('static/pdf/out.pdf')

        else:
            ask_fields()
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

    return render_template('index.html', measurer=last_values['measurer'],
                           date=last_values['date'] if last_values['date'] else '',
                           orderer=last_values['orderer'] if last_values['orderer'] else '',
                           phone_number=last_values['phone-number'] if last_values['phone-number'] else '',
                           street=last_values['street'] if last_values['street'] else '',
                           flat=last_values['flat'] if last_values['flat'] else '',
                           floor=last_values['floor'] if last_values['floor'] else '',
                           comment=last_values['comment'] if last_values['comment'] else '',
                           len=len(polygons), polygons=polygons,
                           download_access=True if polygons else False, point_arr=polygons_arrays)


if __name__ == "__main__":
    app.run(debug=True)
