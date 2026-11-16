from pathlib import Path

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_ALIGN_VERTICAL, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt


ROOT = Path(__file__).resolve().parent
FIG = ROOT / "figures"
OUT = ROOT / "2387_4бригада_работа3.docx"
CODE_UTF8 = ROOT / "ES_COMPUTER_utf8.pro"

TNR = "Times New Roman"
MONO = "Courier New"


def set_run_font(run, name=TNR, size=14, bold=None):
    run.font.name = name
    run.font.size = Pt(size)
    if bold is not None:
        run.font.bold = bold
    rPr = run._element.get_or_add_rPr()
    rFonts = rPr.find(qn("w:rFonts"))
    if rFonts is None:
        rFonts = OxmlElement("w:rFonts")
        rPr.append(rFonts)
    rFonts.set(qn("w:ascii"), name)
    rFonts.set(qn("w:hAnsi"), name)
    rFonts.set(qn("w:cs"), name)
    rFonts.set(qn("w:eastAsia"), name)


def set_para_spacing(p, line=18, before=0, after=0):
    pf = p.paragraph_format
    pf.line_spacing = Pt(line)
    pf.line_spacing_rule = WD_LINE_SPACING.EXACTLY
    pf.space_before = Pt(before)
    pf.space_after = Pt(after)


def add_body(doc, text):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.first_line_indent = Cm(1.25)
    set_para_spacing(p, 18)
    r = p.add_run(text)
    set_run_font(r, TNR, 14)
    return p


def add_heading(doc, text, level=0):
    p = doc.add_paragraph()
    if level == 0:
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.first_line_indent = Cm(0)
    else:
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.first_line_indent = Cm(0)
    set_para_spacing(p, 18)
    p.paragraph_format.keep_with_next = True
    r = p.add_run(text)
    set_run_font(r, TNR, 14, bold=True)
    return p


def add_bullet(doc, text):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.first_line_indent = Cm(1.25)
    p.paragraph_format.left_indent = Cm(0)
    set_para_spacing(p, 18)
    r = p.add_run("– " + text)
    set_run_font(r, TNR, 14)
    return p


def add_caption(doc, text, center=False):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER if center else WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.first_line_indent = Cm(0)
    set_para_spacing(p, 18)
    p.paragraph_format.keep_with_next = True
    r = p.add_run(text)
    set_run_font(r, TNR, 14)
    return p


def add_picture(doc, filename, width_cm, caption):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.first_line_indent = Cm(0)
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.line_spacing = 1.0
    p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.SINGLE
    p.paragraph_format.keep_with_next = True
    run = p.add_run()
    run.add_picture(str(FIG / filename), width=Cm(width_cm))
    add_caption(doc, caption, center=True)


def set_cell_text(cell, text, bold=False, align=WD_ALIGN_PARAGRAPH.LEFT,
                  size=12, line=13.8):
    cell.text = ""
    p = cell.paragraphs[0]
    p.alignment = align
    p.paragraph_format.first_line_indent = Cm(0)
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.line_spacing = Pt(line)
    p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.EXACTLY
    r = p.add_run(text)
    set_run_font(r, TNR, size, bold=bold)
    cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER


def shade_cell(cell, fill):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), fill)
    tcPr.append(shd)


def keep_table_together(table):
    for row in table.rows[:-1]:
        for cell in row.cells:
            for p in cell.paragraphs:
                p.paragraph_format.keep_with_next = True
    for row in table.rows:
        trPr = row._tr.get_or_add_trPr()
        cant = OxmlElement("w:cantSplit")
        trPr.append(cant)


def repeat_header(table):
    trPr = table.rows[0]._tr.get_or_add_trPr()
    tblHeader = OxmlElement("w:tblHeader")
    tblHeader.set(qn("w:val"), "true")
    trPr.append(tblHeader)


def add_table(doc, headers, rows, widths, caption, size=11, header_size=11,
              align_center_cols=None):
    add_caption(doc, caption)
    table = doc.add_table(rows=1, cols=len(headers))
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    for i, w in enumerate(widths):
        table.columns[i].width = Cm(w)
    for i, h in enumerate(headers):
        cell = table.rows[0].cells[i]
        cell.width = Cm(widths[i])
        set_cell_text(cell, h, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER,
                      size=header_size)
        shade_cell(cell, "F2F2F2")
    for row in rows:
        cells = table.add_row().cells
        for i, val in enumerate(row):
            align = WD_ALIGN_PARAGRAPH.LEFT
            if i == 0 or (align_center_cols and i in align_center_cols):
                align = WD_ALIGN_PARAGRAPH.CENTER
            cells[i].width = Cm(widths[i])
            set_cell_text(cells[i], str(val), align=align, size=size)
    repeat_header(table)
    keep_table_together(table)
    doc.add_paragraph()
    return table


def add_code_block(doc, code, size=9, line=None):
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    table.columns[0].width = Cm(17)
    cell = table.cell(0, 0)
    cell.width = Cm(17)
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), "F7F7F7")
    tcPr.append(shd)
    tcMar = OxmlElement("w:tcMar")
    for side in ("top", "left", "bottom", "right"):
        el = OxmlElement(f"w:{side}")
        el.set(qn("w:w"), "80")
        el.set(qn("w:type"), "dxa")
        tcMar.append(el)
    tcPr.append(tcMar)
    tblBorders = OxmlElement("w:tblBorders")
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        el = OxmlElement(f"w:{edge}")
        el.set(qn("w:val"), "single")
        el.set(qn("w:sz"), "4")
        el.set(qn("w:space"), "0")
        el.set(qn("w:color"), "D0D0D0")
        tblBorders.append(el)
    table._tbl.tblPr.append(tblBorders)
    trPr = table.rows[0]._tr.get_or_add_trPr()
    trPr.append(OxmlElement("w:cantSplit"))

    lines = code.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    first = True
    for line_text in lines:
        if first:
            p = cell.paragraphs[0]
            first = False
        else:
            p = cell.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.first_line_indent = Cm(0)
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.line_spacing = Pt(line if line else size + 2.5)
        p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.EXACTLY
        r = p.add_run(line_text if line_text else " ")
        set_run_font(r, MONO, size)
    doc.add_paragraph()


def add_page_number_footer(section):
    section.different_first_page_header_footer = True
    footer = section.footer
    p = footer.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.first_line_indent = Cm(0)
    run = p.add_run()
    set_run_font(run, TNR, 12)
    fld1 = OxmlElement("w:fldChar")
    fld1.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = " PAGE "
    fld2 = OxmlElement("w:fldChar")
    fld2.set(qn("w:fldCharType"), "separate")
    t = OxmlElement("w:t")
    t.text = "1"
    fld3 = OxmlElement("w:fldChar")
    fld3.set(qn("w:fldCharType"), "end")
    run._r.append(fld1)
    run._r.append(instr)
    run._r.append(fld2)
    run._r.append(t)
    run._r.append(fld3)

    pgNumType = OxmlElement("w:pgNumType")
    pgNumType.set(qn("w:start"), "0")
    section._sectPr.append(pgNumType)


def title_page(doc):
    header = [
        "МИНОБРНАУКИ РОССИИ",
        "САНКТ-ПЕТЕРБУРГСКИЙ ГОСУДАРСТВЕННЫЙ",
        "ЭЛЕКТРОТЕХНИЧЕСКИЙ УНИВЕРСИТЕТ",
        "«ЛЭТИ» ИМ. В.И. УЛЬЯНОВА (ЛЕНИНА)",
        "Кафедра Вычислительной техники",
    ]
    for line in header:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.first_line_indent = Cm(0)
        set_para_spacing(p, 18)
        r = p.add_run(line)
        set_run_font(r, TNR, 14, bold=True)

    for _ in range(6):
        p = doc.add_paragraph()
        set_para_spacing(p, 18)

    for line in [
        "ОТЧЕТ",
        "по лабораторной работе №3",
        "по дисциплине «Интеллектуальные системы»",
        "Тема: Разработка экспертной системы с прямой цепочкой рассуждений",
    ]:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.first_line_indent = Cm(0)
        set_para_spacing(p, 18)
        r = p.add_run(line)
        set_run_font(r, TNR, 14, bold=True)

    for _ in range(2):
        p = doc.add_paragraph()
        set_para_spacing(p, 18)

    table = doc.add_table(rows=5, cols=3)
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    for i, w in enumerate((6.0, 5.0, 6.0)):
        table.columns[i].width = Cm(w)
    tblBorders = OxmlElement("w:tblBorders")
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        el = OxmlElement(f"w:{edge}")
        el.set(qn("w:val"), "nil")
        tblBorders.append(el)
    table._tbl.tblPr.append(tblBorders)

    data = [
        ("", "", "Недовизий А.И."),
        ("Студенты гр. 2387", "", "Писаренко А.А."),
        ("", "", "Смирнов М.А."),
        ("", "", ""),
        ("Преподаватель", "", "Подклетнов С.Г."),
    ]
    for r, row in enumerate(data):
        for c, val in enumerate(row):
            cell = table.cell(r, c)
            cell.width = Cm((6.0, 5.0, 6.0)[c])
            set_cell_text(cell, val, size=14, line=14,
                          align=WD_ALIGN_PARAGRAPH.CENTER if c in (1, 2) else WD_ALIGN_PARAGRAPH.LEFT)

    for _ in range(2):
        p = doc.add_paragraph()
        set_para_spacing(p, 18)

    for line in ("Санкт-Петербург", "2026"):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.first_line_indent = Cm(0)
        set_para_spacing(p, 18)
        r = p.add_run(line)
        set_run_font(r, TNR, 14)

    doc.add_page_break()


def main():
    doc = Document()
    section = doc.sections[0]
    section.page_width = Cm(21)
    section.page_height = Cm(29.7)
    section.left_margin = Cm(3)
    section.right_margin = Cm(1)
    section.top_margin = Cm(2)
    section.bottom_margin = Cm(2)
    add_page_number_footer(section)

    style = doc.styles["Normal"]
    style.font.name = TNR
    style.font.size = Pt(14)
    style.paragraph_format.line_spacing = Pt(18)
    style.paragraph_format.line_spacing_rule = WD_LINE_SPACING.EXACTLY
    style.paragraph_format.space_before = Pt(0)
    style.paragraph_format.space_after = Pt(0)
    style.paragraph_format.first_line_indent = Cm(1.25)

    title_page(doc)

    add_heading(doc, "1 Цель работы", 0)
    add_body(doc,
             "Изучение технологии построения экспертных систем с прямой цепочкой рассуждений. "
             "Приобретение навыков разработки базы знаний, механизма вывода и пользовательского "
             "интерфейса на языке Visual Prolog 5.2 на примере задачи определения причины "
             "неработоспособности компьютера.")

    add_heading(doc, "2 Ход работы", 0)
    add_heading(doc, "2.1 Постановка задачи", 1)
    add_body(doc,
             "В соответствии с вариантом 4 (рисунок 1) требуется разработать экспертную систему "
             "с прямой цепочкой рассуждений для определения причины неработоспособности компьютера. "
             "Система должна оперировать 12 возможными причинами и 6 признаками, а максимальная "
             "глубина дерева вывода не должна превышать 4.")
    add_picture(doc, "task_variant4.png", 16.5, "Рисунок 1 – Вариант 4 задания")

    add_body(doc,
             "Перечень признаков, которые запрашиваются у пользователя, приведён в таблице 1. "
             "Каждый признак имеет два возможных значения: y (да) и n (нет). Ответы пользователя "
             "образуют исходные факты рабочей памяти.")
    add_table(
        doc,
        ("№", "Обозначение", "Вопрос"),
        [
            ("1", "power", "Компьютер включается (есть реакция на кнопку питания)?"),
            ("2", "fan", "Вращается вентилятор блока питания или процессора?"),
            ("3", "display", "Есть изображение на мониторе?"),
            ("4", "beep", "Слышны звуковые сигналы BIOS?"),
            ("5", "os", "Начинается загрузка операционной системы?"),
            ("6", "overheat", "Компьютер перегревается или выключается через некоторое время?"),
        ],
        (1.0, 4.0, 12.0),
        "Таблица 1 – Признаки неработоспособности компьютера",
        size=11,
        align_center_cols=(0, 1),
    )

    add_body(doc,
             "Возможные причины неработоспособности приведены в таблице 2. Для каждого допустимого "
             "набора ответов система должна выводить не более одной причины, а для противоречивых "
             "или нормальных наборов — не выдавать ложную причину. Кроме того, система должна "
             "показывать глубину, на которой была получена причина.")
    add_table(
        doc,
        ("№", "Обозначение", "Причина"),
        [
            ("1", "bad_outlet", "Нет напряжения в сети (неисправна розетка или кабель питания)"),
            ("2", "bad_psu", "Неисправен блок питания"),
            ("3", "bad_power_button", "Неисправна кнопка питания"),
            ("4", "bad_motherboard", "Неисправна материнская плата"),
            ("5", "bad_cpu", "Неисправен процессор"),
            ("6", "bad_ram", "Неисправна оперативная память"),
            ("7", "bad_gpu", "Неисправна видеокарта"),
            ("8", "bad_monitor", "Неисправен монитор или кабель"),
            ("9", "bad_hdd", "Неисправен жёсткий диск"),
            ("10", "bad_os", "Повреждена операционная система"),
            ("11", "bad_bios", "Неисправен BIOS"),
            ("12", "bad_cooler", "Неисправна система охлаждения (кулер)"),
        ],
        (1.0, 5.0, 11.0),
        "Таблица 2 – Возможные причины неработоспособности",
        size=10.5,
        align_center_cols=(0, 1),
    )

    add_heading(doc, "2.2 Проектирование базы знаний", 1)
    add_body(doc,
             "Экспертная система построена по схеме, показанной на рисунке 2. Основу составляют "
             "рабочая память и база правил. Механизм вывода на каждом проходе просматривает все "
             "правила и добавляет в рабочую память те заключения, условия которых уже известны.")
    add_picture(doc, "es_architecture.png", 16.5,
                "Рисунок 2 – Схема работы экспертной системы")

    add_body(doc,
             "Рабочая память реализована как динамическая база фактов known(Ответ, Факт, Глубина). "
             "Для исходных признаков поле «Ответ» принимает значение yes или no, а глубина равна 0. "
             "Для выведенных фактов используется ответ yes; глубина вычисляется как максимум глубин "
             "условий плюс единица.")
    add_body(doc,
             "База правил хранится в виде фактов rule(Заключение, ПоложительныеУсловия, "
             "ОтрицательныеУсловия). Положительные условия должны быть известны со значением yes, "
             "отрицательные — со значением no. Например, правило rule(no_video, [], [display]) "
             "означает: если на вопрос display получен ответ no, то факт no_video истинен.")
    add_body(doc,
             "Все правила разделены на четыре уровня (таблица 3). На первом уровне 12 правил "
             "преобразуют ответы пользователя в элементарные заключения. На втором уровне 11 правил "
             "объединяют пары элементарных заключений. На третьем уровне 4 правила уточняют "
             "гипотезы с учётом загрузки операционной системы и перегрева. На четвёртом уровне "
             "12 правил соответствуют причинам неработоспособности. Общее количество правил — 39.")
    add_table(
        doc,
        ("Уровень", "Назначение", "Кол-во", "Примеры"),
        [
            ("0", "Исходные признаки (ответы пользователя)", "6",
             "power, fan, display, beep, os, overheat"),
            ("1", "Элементарные заключения", "12",
             "power_ok, no_power, post_ok, boot_error, hot, cool"),
            ("2", "Составные гипотезы", "11",
             "power_fan, no_video_post_error, boot_error_cool"),
            ("3", "Уточняющие гипотезы", "4",
             "no_video_post_ok_no_os, video_ok_post_ok_os_hot"),
            ("4", "Причины", "12",
             "bad_gpu, bad_ram, bad_cooler"),
        ],
        (2.0, 6.0, 2.0, 7.0),
        "Таблица 3 – Уровни базы знаний",
        size=10.5,
        align_center_cols=(0, 2),
    )

    add_body(doc,
             "Для сценария bad_gpu путь вывода показан на рисунке 3. Ответы power=yes и fan=yes "
             "дают power_ok и fan_ok, после чего на втором проходе появляется power_fan. Ответы "
             "display=no и beep=no дают no_video и post_ok, а на втором проходе — no_video_post_ok. "
             "Ответ os=no даёт boot_error; вместе с no_video_post_ok он образует "
             "no_video_post_ok_no_os на третьем проходе. Наконец, power_fan и "
             "no_video_post_ok_no_os дают bad_gpu на четвёртом проходе. Ответ overheat=no порождает "
             "cool и побочный факт boot_error_cool, который в выводе bad_gpu не участвует.")
    add_picture(doc, "rule_path_bad_gpu.png", 16.5,
                "Рисунок 3 – Путь прямого вывода для сценария bad_gpu")

    add_body(doc,
             "Максимальная глубина достигается для причин bad_gpu, bad_monitor, bad_hdd, bad_os "
             "и bad_cooler и равна 4, что соответствует варианту задания.")

    add_heading(doc, "2.3 Разработка программы", 1)
    add_body(doc,
             "Программа реализована на Visual Prolog 5.2. Исходный файл ES_COMPUTER.pro сохранён "
             "в кодировке Windows-1251, поскольку компилятор 5.2 не поддерживает UTF-8 в исходных "
             "текстах. Для запуска в VDE создаётся проект Text mode или EasyWin, в проект "
             "добавляется файл ES_COMPUTER.pro, цель проекта — run.")
    add_body(doc,
             "Основные предикаты механизма вывода приведены в листинге 1. Предикат forward "
             "организует проходы, а all_known проверяет условия правила и вычисляет глубину.")
    add_caption(doc, "Листинг 1 – Основные предикаты прямого вывода")
    add_code_block(doc, """forward :-
    clear_fired,
    pass_no(N),
    write("--- Проход ", N, " ---"), nl,
    rule(C, Pos, Neg),
    not(known(yes, C, _)),
    all_known(Pos, Neg, 0, D0),
    D = D0 + 1,
    D <= 4,
    fact_name(C, Name),
    assertz(known(yes, C, D)),
    assertz(fired(yes)),
    write("  Сработало правило: ", Name, " (глубина ", D, ")"), nl,
    fail.
forward :-
    fired(_),
    !,
    pass_no(N),
    N1 = N + 1,
    retract(pass_no(N)),
    assertz(pass_no(N1)),
    forward.
forward.

all_known([], [], D, D) :- !.
all_known([P|Ps], Neg, D0, D) :-
    known(yes, P, DP),
    max2(D0, DP, D1),
    all_known(Ps, Neg, D1, D).
all_known([], [N|Ns], D0, D) :-
    known(no, N, _),
    all_known([], Ns, D0, D).""", size=8.5)

    add_body(doc,
             "Фрагмент базы правил приведён в листинге 2. Правила причин перечислены первыми, "
             "затем идут правила третьего, второго и первого уровней. Такой порядок не влияет "
             "на результат, но делает трассировку наглядной: на каждом проходе сначала проверяются "
             "более «дальние» заключения, а затем происходит накопление фактов по уровням.")
    add_caption(doc, "Листинг 2 – Фрагмент базы правил")
    add_code_block(doc, """rule(bad_gpu, [power_fan, no_video_post_ok_no_os], []).
rule(bad_ram, [power_fan, no_video_post_error], []).
rule(bad_bios, [power_fan, video_ok_post_error], []).
rule(no_video_post_ok_no_os, [no_video_post_ok, boot_error], []).
rule(power_fan, [power_ok, fan_ok], []).
rule(no_video, [], [display]).
rule(post_ok, [], [beep]).
rule(boot_error, [], [os]).""", size=8.5)

    doc.add_page_break()
    add_body(doc,
             "Опрос пользователя реализован в листинге 3. Ответ y или Y считается положительным, "
             "любой другой ответ — отрицательным.")
    add_caption(doc, "Листинг 3 – Опрос пользователя")
    add_code_block(doc, """ask(S) :-
    question_text(S, Q),
    write(Q, " (y/n): "),
    readln(Reply),
    frontchar(Reply, C, _),
    yes_char(C), !,
    assertz(known(yes, S, 0)).
ask(S) :-
    assertz(known(no, S, 0)).

yes_char('y').
yes_char('Y').""", size=8.5)
    add_body(doc,
             "Для сборки использовались компилятор PRO.EXE и компоновщик pdclink.exe из состава "
             "Visual Prolog 5.2. Для консольной версии применялась опция -SCUI, для отладочной "
             "сборки включалась генерация отладочной информации. Полный текст программы "
             "с комментариями приведён в приложении А.")

    add_heading(doc, "2.4 Результаты работы", 1)
    add_body(doc,
             "Для проверки разработано 12 сценариев — по одному на каждую причину. В каждом "
             "сценарии система задаёт шесть вопросов и выполняет от двух до пяти проходов. "
             "Результаты приведены в таблице 4.")
    add_table(
        doc,
        ("№", "Причина", "Ответы (power, fan, display, beep, os, overheat)", "Глубина"),
        [
            ("1", "bad_outlet", "n  n  n  n  n  n", "3"),
            ("2", "bad_psu", "n  n  n  y  n  n", "3"),
            ("3", "bad_power_button", "n  y  n  n  n  n", "2"),
            ("4", "bad_motherboard", "y  n  n  n  n  n", "3"),
            ("5", "bad_cpu", "y  n  n  y  n  n", "3"),
            ("6", "bad_ram", "y  y  n  y  n  n", "3"),
            ("7", "bad_gpu", "y  y  n  n  n  n", "4"),
            ("8", "bad_monitor", "y  y  n  n  y  n", "4"),
            ("9", "bad_hdd", "y  y  y  n  n  n", "4"),
            ("10", "bad_os", "y  y  y  n  n  y", "4"),
            ("11", "bad_bios", "y  y  y  y  n  n", "3"),
            ("12", "bad_cooler", "y  y  y  n  y  y", "4"),
        ],
        (1.0, 5.0, 9.0, 2.0),
        "Таблица 4 – Результаты проверки по 12 сценариям",
        size=9.5,
        header_size=9.5,
        align_center_cols=(0, 3),
    )
    add_body(doc,
             "Во всех 12 сценариях система вывела ровно одну причину, совпадающую с ожидаемой. "
             "Пересечений и ложных срабатываний нет. Для причин bad_gpu, bad_monitor, bad_hdd, "
             "bad_os и bad_cooler глубина равна 4, для bad_outlet, bad_psu, bad_motherboard, "
             "bad_cpu, bad_ram и bad_bios — 3, для bad_power_button — 2.")
    add_body(doc,
             "На рисунках 4–7 приведены примеры работы программы для сценариев bad_gpu, "
             "bad_outlet, bad_power_button и для случая, когда причина не выявлена.")
    add_picture(doc, "result_bad_gpu.png", 15.0,
                "Рисунок 4 – Результат для сценария bad_gpu")
    add_picture(doc, "result_bad_outlet.png", 15.0,
                "Рисунок 5 – Результат для сценария bad_outlet")
    add_picture(doc, "result_bad_power_button.png", 15.0,
                "Рисунок 6 – Результат для сценария bad_power_button")
    add_picture(doc, "result_no_cause.png", 15.0,
                "Рисунок 7 – Пример работы без выявленной причины")
    add_body(doc,
             "Дополнительно проверены все 64 возможные комбинации ответов. В 59 комбинациях "
             "система выводит одну из 12 причин. Остальные 5 комбинаций (таблица 5) являются "
             "противоречивыми или соответствуют исправному компьютеру; для них выводится сообщение "
             "«Причина не определена». Например, комбинация power=yes, fan=no, display=yes "
             "означает, что вентилятор не вращается, но изображение на мониторе есть, что "
             "физически противоречиво. Комбинация y, y, y, n, y, n соответствует полностью "
             "работающему компьютеру.")
    add_table(
        doc,
        ("power", "fan", "display", "beep", "os", "overheat", "Интерпретация"),
        [
            ("y", "n", "y", "n", "n", "n", "Противоречие: вентилятор не вращается, но изображение есть"),
            ("y", "n", "y", "n", "n", "y", "То же, плюс перегрев"),
            ("y", "n", "y", "n", "y", "n", "То же, ОС загружается"),
            ("y", "n", "y", "n", "y", "y", "То же, ОС загружается и перегрев"),
            ("y", "y", "y", "n", "y", "n", "Все основные подсистемы работают, причина не выявлена"),
        ],
        (1.6, 1.2, 1.5, 1.3, 1.2, 1.8, 8.4),
        "Таблица 5 – Комбинации ответов, для которых причина не определена",
        size=9,
        header_size=9,
        align_center_cols=(0, 1, 2, 3, 4, 5),
    )
    add_body(doc,
             "Таким образом, на допустимых наборах ответов система работает корректно, а на "
             "противоречивых данных не выдаёт ложную причину.")

    add_heading(doc, "2.5 Трассировка прямого вывода", 1)
    add_body(doc,
             "Трассировка выполнена для сценария bad_gpu с ответами power=yes, fan=yes, display=no, "
             "beep=no, os=no, overheat=no. В VDE включена генерация отладочной информации, точка "
             "останова установлена на предикате forward. На каждом проходе фиксировались новые "
             "факты рабочей памяти, содержимое окна Call Stack и окна Variables For Current Clause.")
    add_body(doc, "Последовательность проходов приведена в таблице 6.")
    add_table(
        doc,
        ("Проход", "Новые факты", "Глубина", "Комментарий"),
        [
            ("1", "power_ok, fan_ok, no_video, post_ok, boot_error, cool", "1",
             "Симптомы преобразованы в факты"),
            ("2", "power_fan, no_video_post_ok, boot_error_cool", "2",
             "Составные гипотезы; boot_error_cool — побочный факт"),
            ("3", "no_video_post_ok_no_os", "3",
             "Объединены отсутствие изображения и ошибка загрузки ОС"),
            ("4", "bad_gpu", "4", "Причина найдена"),
            ("5", "—", "—", "Новых фактов нет, вывод остановлен"),
        ],
        (1.8, 7.0, 1.8, 6.4),
        "Таблица 6 – Проходы прямого вывода для сценария bad_gpu",
        size=9.5,
        header_size=9.0,
        align_center_cols=(0, 2),
    )
    add_body(doc,
             "На первом проходе срабатывают 12 правил первого уровня, но в рабочую память "
             "добавляются только те факты, которые соответствуют ответам. Для данного сценария "
             "это power_ok, fan_ok, no_video, post_ok, boot_error и cool. На втором проходе "
             "появляются power_fan, no_video_post_ok и побочный boot_error_cool. На третьем "
             "проходе — no_video_post_ok_no_os. На четвёртом — bad_gpu. Пятый проход не добавляет "
             "новых фактов, после чего вывод останавливается.")
    add_body(doc, "Связывания переменных на ключевых шагах приведены в таблице 7.")
    add_table(
        doc,
        ("Шаг", "Правило", "Связывания", "Результат"),
        [
            ("1", "power_ok", "C=power_ok, Pos=[power], Neg=[], D0=0", "D=1"),
            ("2", "power_fan", "C=power_fan, Pos=[power_ok, fan_ok], D0=max(1,1)=1", "D=2"),
            ("3", "no_video_post_ok", "C=no_video_post_ok, Pos=[no_video, post_ok], D0=max(1,1)=1", "D=2"),
            ("4", "no_video_post_ok_no_os", "C=no_video_post_ok_no_os, Pos=[no_video_post_ok, boot_error], D0=max(2,1)=2", "D=3"),
            ("5", "bad_gpu", "C=bad_gpu, Pos=[power_fan, no_video_post_ok_no_os], D0=max(2,3)=3", "D=4"),
        ],
        (1.5, 4.5, 9.0, 2.0),
        "Таблица 7 – Связывания переменных при выводе bad_gpu",
        size=8.5,
        header_size=9,
        align_center_cols=(0, 3),
    )
    add_body(doc,
             "На рисунках 8–10 приведены окна отладчика для проходов 1, 3 и 4. В окне Call Stack "
             "видна цепочка вызовов forward → run → _PROLOG_Goal. На рисунках 8 и 9 в окне "
             "Variables For Current Clause отображается номер прохода N (N = 1 и N = 3 "
             "соответственно); на рисунке 10 — переменные C, Pos, Neg, D0, D и Name. На проходе 4 "
             "переменная C связана с bad_gpu, Pos — со списком [power_fan, no_video_post_ok_no_os], "
             "Neg = [], D0 = 3, D = 4, Name = «Неисправна видеокарта».")
    add_body(doc,
             "Для получения трассировки необходимо: 1) включить в VDE генерацию отладочной "
             "информации; 2) установить точку останова внутри второго предложения forward "
             "(строка 116) для проходов 1 и 3, а для прохода 4 — на строке 110 после "
             "assertz(fired(yes)); 3) запустить проект и ввести ответы y, y, n, n, n, n; 4) открыть "
             "окна View → Call Stack и View → Variables For Current Clause; 5) выполнять шаги "
             "Trace Into и фиксировать состояние после каждого прохода.")
    doc.add_page_break()
    add_picture(doc, "trace_pass1.png", 13.0,
                "Рисунок 8 – Трассировка, проход 1")
    add_picture(doc, "trace_pass3.png", 13.0,
                "Рисунок 9 – Трассировка, проход 3")
    add_picture(doc, "trace_pass4.png", 13.0,
                "Рисунок 10 – Трассировка, проход 4")

    doc.add_page_break()
    add_heading(doc, "3 Выводы", 0)
    add_body(doc,
             "В ходе лабораторной работы была изучена технология построения экспертных систем "
             "с прямой цепочкой рассуждений. Разработана база знаний из 39 правил: 27 промежуточных "
             "гипотез и 12 причин. Реализован механизм прямого вывода, который на каждом проходе "
             "просматривает правила, добавляет новые факты в рабочую память и вычисляет глубину "
             "вывода. Максимальная глубина ограничена 4, что соответствует варианту задания.")
    add_body(doc,
             "Программа проверена на 12 сценариях. Во всех сценариях причина определена "
             "однозначно и совпала с ожидаемой. Дополнительная проверка 64 комбинаций ответов "
             "показала, что 59 комбинаций дают одну из 12 причин, а 5 противоречивых или нормальных "
             "комбинаций не приводят к ложной причине.")
    add_body(doc, "Обязанности между участниками команды были распределены следующим образом.")
    add_body(doc,
             "Писаренко А.А. занималась программной реализацией и отладкой: написала исходный "
             "текст программы, настроила сборку в Visual Prolog 5.2, провела трассировку "
             "с использованием окон Call Stack и Variables For Current Clause.")
    add_body(doc,
             "Недовизий А.И. отвечал за аналитическую часть: проанализировал предметную область, "
             "выделил 12 причин и 6 признаков, построил уровни базы знаний и проверил отсутствие "
             "пересечений между причинами.")
    add_body(doc,
             "Смирнов М.А. выполнял сведение данных и оформление отчёта: подготовил таблицы, "
             "рисунки и описания трассировки, проверил соответствие отчёта варианту задания.")
    add_body(doc,
             "Все поставленные задачи выполнены. Полученные навыки могут быть применены при "
             "разработке экспертных систем с продукционной моделью знаний.")

    doc.add_page_break()
    add_heading(doc, "Приложение А – Полный текст программы", 0)
    add_body(doc,
             "Ниже приведён полный текст файла ES_COMPUTER.pro (кодировка Windows-1251). "
             "Комментарии сохранены в исходном виде.")
    code_lines = CODE_UTF8.read_text(encoding="utf-8").splitlines()
    for line in code_lines:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.first_line_indent = Cm(0)
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.line_spacing = Pt(10.5)
        p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.EXACTLY
        r = p.add_run(line if line else " ")
        set_run_font(r, MONO, 7.5)

    doc.core_properties.title = "Лабораторная работа №3. Вариант 4"
    doc.core_properties.author = "Недовизий А.И., Писаренко А.А., Смирнов М.А."
    doc.core_properties.subject = "Экспертная система с прямой цепочкой рассуждений"
    doc.save(OUT)
    print("saved", OUT)


if __name__ == "__main__":
    main()
