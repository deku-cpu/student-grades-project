from io import BytesIO
from xml.sax.saxutils import escape
from zipfile import ZipFile, ZIP_DEFLATED
from decimal import Decimal

from django.http import HttpResponse, JsonResponse

from .grading import grade_label


def excel_response(rows, filename):
    # Небольшой XLSX без внешних библиотек. Текст не выполняется как формула.
    output = BytesIO()
    worksheet = []
    for row_index, row in enumerate(rows, 1):
        cells = []
        for column, value in enumerate(row, 1):
            letters = ''
            while column:
                column, remainder = divmod(column - 1, 26)
                letters = chr(65 + remainder) + letters
            if isinstance(value, (int, float, Decimal)) and not isinstance(value, bool):
                cells.append(f'<c r="{letters}{row_index}" t="n"><v>{value}</v></c>')
                continue
            text = str('' if value is None else value)
            text = ''.join(char for char in text if ord(char) >= 32 or char in '\n\t\r')
            cells.append(f'<c r="{letters}{row_index}" t="inlineStr"><is><t xml:space="preserve">{escape(text)}</t></is></c>')
        worksheet.append(f'<row r="{row_index}">{"".join(cells)}</row>')
    with ZipFile(output, 'w', ZIP_DEFLATED) as archive:
        archive.writestr('[Content_Types].xml', '<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/><Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/></Types>')
        archive.writestr('_rels/.rels', '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/></Relationships>')
        archive.writestr('xl/workbook.xml', '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets><sheet name="Отчёт" sheetId="1" r:id="rId1"/></sheets></workbook>')
        archive.writestr('xl/_rels/workbook.xml.rels', '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/></Relationships>')
        archive.writestr('xl/worksheets/sheet1.xml', '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData>' + ''.join(worksheet) + '</sheetData></worksheet>')
    result = HttpResponse(output.getvalue(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    result['Content-Disposition'] = f'attachment; filename="{filename}.xlsx"'
    return result


def report_response(request, data, kind):
    if request.GET.get('format') != 'xlsx':
        return JsonResponse(data, safe=isinstance(data, dict), json_dumps_params={'ensure_ascii': False})
    if kind == 'statement':
        rows = [['Группа', data['group_name']], ['Дисциплина', data['discipline_name']], ['Семестр', data['semester']],
                ['Преподаватель', data['teacher']], ['Студент'] + [a['title'] for a in data['assignments']] + ['Итог']]
        rows += [[s['full_name']] + [grade_label(s['grades'].get(a['id'])) for a in data['assignments']] + [grade_label(s['final_grade'])] for s in data['students']]
        rows += [['Средний балл', data['avg_grade']], ['Качество знаний, %', data['quality_percent']]]
    elif kind == 'student-summary':
        rows = [['Студент', data['full_name']], ['Группа', data['group_name']], ['Средний балл', data['avg_grade']],
                ['Дисциплина', 'Группа', 'Семестр', 'Преподаватель', 'Форма контроля', 'Оценки', 'Итог']]
        rows += [[r['discipline'], r['group'], r['semester'], r['teacher'], r['control_form'],
                  '; '.join(a['title'] + ': ' + str(grade_label(a['value'])) for a in r['assignments']), grade_label(r['final_grade'])] for r in data['results']]
    elif kind == 'group-rating':
        rows = [['Группа', data['group_name']], ['Место', 'Студент', 'Средний балл', 'Долгов']]
        rows += [[s['place'], s['full_name'], s['avg_grade'], s['bad_count']] for s in data['students']]
    elif kind == 'debtors':
        rows = [['Студент', 'Группа', 'Дисциплина', 'Семестр', 'Итог']]
        rows += [[r['student'], r['group'], r['discipline'], r['semester'], grade_label(r['final_grade'])] for r in data]
    elif kind == 'statistics':
        rows = [['Раздел', 'Студентов', 'Средний балл', 'Долгов']]
        rows += [[r['name'], r['students'], r['avg_grade'], r['bad_count']] for r in data]
    else:
        rows = [['Группа', 'Студентов', 'С оценками 4 и 5', 'Качество знаний, %']]
        rows += [[r['group'], r['students'], r['good'], r['quality_percent']] for r in data]
    return excel_response(rows, kind)
