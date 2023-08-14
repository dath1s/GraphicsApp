from functions import *
from config import *

from flask import Flask, render_template, request, send_file

from zipfile import ZipFile
import os
# from fpdf import FPDF

app = Flask(__name__, template_folder='templates')
app.secret_key = secret_key

# user variables
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

    ask_fields()
    if request.method == 'POST':
        if 'add_draw' in request.form:
            polygons.append(f'{request.form.get("draw-type")[0]}d{count}')
            create_surface_1d(f'{img_dir}/polygon{count}.svg', f'{img_to_save_dir}/save_polygon{count}.svg')
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

            path_to_clear = [img_dir, img_to_save_dir, svg_zip_dir, svg_for_pdf_dir, pdf_dir]
            for path in path_to_clear:
                for filepath in os.listdir(path):
                    os.remove(f'{path}/{filepath}')

        elif "download-svg" in request.form:
            with ZipFile(f'{svg_zip_dir}/svg_zip.zip', 'w') as f:
                for filepath in os.listdir(img_to_save_dir):
                    f.write(f'{img_to_save_dir}/{filepath}')

            return send_file(f'{svg_zip_dir}/svg_zip.zip')

        elif 'download-pdf' in request.form:
            # pdf = FPDF(format='A4')
            #
            # pdf.add_font('DejaVu', '', 'static/fonts/DejaVuSansCondensed.ttf', uni=True)
            #
            # for path in range(count):
            #     pdf.add_page()
            #     pdf.set_font('DejaVu', '', 10)
            #
            #     pdf.cell(0, 5, txt=f'Исполнитель: {last_values["measurer"]}  Дата: {last_values["date"]}', ln=1)
            #     pdf.cell(0, 5,
            #              txt=f'Заказчик: {last_values["orderer"]}  Телефон: {last_values["phone-number"]}' +
            #                  f'  Улица: {last_values["street"]}  Квартира: {last_values["flat"]}' +
            #                  f'  Этаж: {last_values["floor"]}',
            #              ln=1)
            #     pdf.cell(0, 5, txt=f'Комментарий: {last_values["comment"]}', ln=1)
            #     pdf.cell(0, 120, txt="", ln=1)
            #
            #     pdf.image(f'{svg_for_pdf_dir}/pdf_polygon{path}.svg', x=0, y=40)
            #
            #     pdf.cell(0, 5, txt='Заданные фигуры:', ln=1)
            #     for point_arr in polygons_arrays[str(path)]:
            #         def point_arr_to_pdf(arr):
            #             if len(arr) == 3:
            #                 return f'y1: {arr[0]}   y2: {arr[1]}   width: {arr[2]}'
            #             return f'({arr[0]}, {arr[1]}), ({arr[2]}, {arr[3]}), ({arr[4]}, {arr[5]}), ({arr[6]}, {arr[7]})'
            #
            #         pdf.cell(0, 5, txt=point_arr_to_pdf(point_arr), ln=1)
            #
            # pdf.output(f'{pdf_dir}/out.pdf')
            # return send_file(f'{pdf_dir}/out.pdf')
            return render_template("blank.html",
                                   measurer=last_values['measurer'] if last_values['measurer'] else '',
                                   date=last_values['date'] if last_values['date'] else '',
                                   orderer=last_values['orderer'] if last_values['orderer'] else '',
                                   phone_number=last_values['phone-number'] if last_values['phone-number'] else '',
                                   street=last_values['street'] if last_values['street'] else '',
                                   flat=last_values['flat'] if last_values['flat'] else '',
                                   floor=last_values['floor'] if last_values['floor'] else '',
                                   comment=last_values['comment'] if last_values['comment'] else '',
                                   count=count,
                                   polygons_arrays=polygons_arrays,
                                   polyg_type_arr=polygons
                                   )

        else:
            post_form = request.form
            post_arr = sorted(post_form, key=lambda x: 'add_points_' in x, reverse=True)

            if 'add_points_1d_' in post_arr[0]:
                try:
                    window_id = post_arr[0][14:]

                    y1, y2, width = int(post_form[f'y1_{window_id}']), int(post_form[f'y2_{window_id}']), int(
                        post_form[f'width_{window_id}'])

                    polygons_arrays[window_id].append([y1, y2, width])
                    create_surface_1d(f'{img_dir}/polygon{window_id}.svg',
                                      f'{img_to_save_dir}/save_polygon{window_id}.svg',
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
                    create_surface_2d(f'{img_dir}/polygon{window_id}.svg',
                                      f'{img_to_save_dir}/save_polygon{window_id}.svg',
                                      points=polygons_arrays[window_id])
                except Exception:
                    pass

    return render_template('index.html',
                           measurer=last_values['measurer'] if last_values['measurer'] else '',
                           date=last_values['date'] if last_values['date'] else '',
                           orderer=last_values['orderer'] if last_values['orderer'] else '',
                           phone_number=last_values['phone-number'] if last_values['phone-number'] else '',
                           street=last_values['street'] if last_values['street'] else '',
                           flat=last_values['flat'] if last_values['flat'] else '',
                           floor=last_values['floor'] if last_values['floor'] else '',
                           comment=last_values['comment'] if last_values['comment'] else '',
                           len=len(polygons),
                           polygons=polygons,
                           download_access=True if polygons else False,
                           point_arr=polygons_arrays)


if __name__ == "__main__":
    app.run(debug=True)
