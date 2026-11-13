import json
from pathlib import Path

import nbformat
from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent
TEMPLATE = ROOT / "1lab" / "ml1_Nedoviziy.docx"
NOTEBOOK = BASE / "lab2.ipynb"
RESULTS_PATH = BASE / "artifacts" / "results.json"
FIG_DIR = BASE / "artifacts" / "figures"
OUTPUT = BASE / "ml2_Nedoviziy.docx"

R = json.loads(RESULTS_PATH.read_text(encoding="utf-8"))
K = {row["k"]: row for row in R["kmeans"]}
INIT = {row["init"]: row for row in R["init_summary"]}
DBSCAN_EPS = {row["eps"]: row for row in R["dbscan_eps"]}
DBSCAN_NOISE = {row["contamination"]: row for row in R["dbscan_noise"]}
HIER = {(row["linkage"], row["metric"]): row for row in R["hierarchical"]}
COMPARISON = {row["method"]: row for row in R["comparison"]}
PROFILES = R["profiles"]
FEATURE_SUBSET = {row["features"]: row for row in R["feature_subset"]}
STABILITY = R["stability"]
SCALABILITY = R["scalability"]
ENSEMBLE = R["ensemble"]
DBSCAN_FINAL = R["dbscan_final"]
DATASET = R["dataset"]


def number(value, digits=3):
    return f"{value:.{digits}f}".replace(".", ",")


def percent(value, digits=1):
    return f"{value * 100:.{digits}f}".replace(".", ",") + " %"


doc = Document(TEMPLATE)
body = doc.element.body
for child in list(body):
    if child.tag != qn("w:sectPr"):
        body.remove(child)

section = doc.sections[0]
section.page_width = Cm(21)
section.page_height = Cm(29.7)
section.left_margin = Cm(3)
section.right_margin = Cm(1.5)
section.top_margin = Cm(2)
section.bottom_margin = Cm(2)
section.header_distance = Cm(1.25)
section.footer_distance = Cm(1.25)
section.different_first_page_header_footer = True

styles = doc.styles

normal = styles["Normal"]
normal.font.name = "Times New Roman"
normal.font.size = Pt(14)
normal._element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
normal.paragraph_format.line_spacing = 1.5
normal.paragraph_format.space_after = Pt(0)
normal.paragraph_format.first_line_indent = Cm(1.25)
normal.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY


for style_name, size in [("Heading 1", 14), ("Heading 2", 14), ("Heading 3", 14)]:
    style = styles[style_name]
    style.font.name = "Times New Roman"
    style.font.size = Pt(size)
    style.font.bold = True
    style.font.color.rgb = RGBColor(0, 0, 0)
    style.paragraph_format.first_line_indent = Cm(0)
    style.paragraph_format.line_spacing = 1.5
    style.paragraph_format.space_before = Pt(12)
    style.paragraph_format.space_after = Pt(6)
    style.paragraph_format.keep_with_next = True
    style.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT

caption_style = styles.add_style("FigureCaption", 1)
caption_style.font.name = "Times New Roman"
caption_style.font.size = Pt(12)
caption_style.paragraph_format.first_line_indent = Cm(0)
caption_style.paragraph_format.line_spacing = 1.0
caption_style.paragraph_format.space_before = Pt(6)
caption_style.paragraph_format.space_after = Pt(6)
caption_style.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER

table_caption_style = styles.add_style("TableCaption", 1)
table_caption_style.font.name = "Times New Roman"
table_caption_style.font.size = Pt(12)
table_caption_style.paragraph_format.first_line_indent = Cm(0)
table_caption_style.paragraph_format.line_spacing = 1.0
table_caption_style.paragraph_format.space_before = Pt(6)
table_caption_style.paragraph_format.space_after = Pt(2)
table_caption_style.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT

code_style = styles.add_style("CodeBlock", 1)
code_style.font.name = "Courier New"
code_style.font.size = Pt(8.5)
code_style.paragraph_format.first_line_indent = Cm(0)
code_style.paragraph_format.line_spacing = 1.0
code_style.paragraph_format.space_after = Pt(0)
code_style.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT

list_style = styles.add_style("ListItem", 1)
list_style.font.name = "Times New Roman"
list_style.font.size = Pt(14)
list_style.paragraph_format.line_spacing = 1.5
list_style.paragraph_format.space_after = Pt(0)
list_style.paragraph_format.left_indent = Cm(1.25)
list_style.paragraph_format.first_line_indent = Cm(-0.6)
list_style.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY


def set_run_font(run, name="Times New Roman", size=14, bold=None, italic=None):
    run.font.name = name
    run.font.size = Pt(size)
    if bold is not None:
        run.bold = bold
    if italic is not None:
        run.italic = italic
    run._element.rPr.rFonts.set(qn("w:eastAsia"), name)


def centered(text, size=14, bold=False, space_after=0):
    paragraph = doc.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    paragraph.paragraph_format.first_line_indent = Cm(0)
    paragraph.paragraph_format.line_spacing = 1.5
    paragraph.paragraph_format.space_after = Pt(space_after)
    run = paragraph.add_run(text)
    set_run_font(run, size=size, bold=bold)
    return paragraph


def add_heading(text, level):
    paragraph = doc.add_heading(text, level=level)
    paragraph.paragraph_format.first_line_indent = Cm(0)
    return paragraph


def add_body(text):
    paragraph = doc.add_paragraph(text)
    paragraph.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    paragraph.paragraph_format.first_line_indent = Cm(1.25)
    paragraph.paragraph_format.line_spacing = 1.5
    paragraph.paragraph_format.space_after = Pt(0)
    return paragraph


def add_list_item(text):
    paragraph = doc.add_paragraph(text, style="ListItem")
    return paragraph


def add_theory_subheading(text):
    paragraph = doc.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    paragraph.paragraph_format.first_line_indent = Cm(1.25)
    paragraph.paragraph_format.line_spacing = 1.5
    run = paragraph.add_run(text)
    set_run_font(run, size=14, italic=True)
    return paragraph


def add_figure(filename, caption, width_cm=16):
    paragraph = doc.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    paragraph.paragraph_format.first_line_indent = Cm(0)
    paragraph.paragraph_format.space_before = Pt(6)
    paragraph.paragraph_format.space_after = Pt(0)
    run = paragraph.add_run()
    run.add_picture(str(FIG_DIR / filename), width=Cm(width_cm))
    caption_paragraph = doc.add_paragraph(f"Рисунок {caption}", style="FigureCaption")
    return caption_paragraph


def set_table_borders(table):
    tbl_pr = table._tbl.tblPr
    borders = OxmlElement("w:tblBorders")
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        element = OxmlElement(f"w:{edge}")
        element.set(qn("w:val"), "single")
        element.set(qn("w:sz"), "4")
        element.set(qn("w:space"), "0")
        element.set(qn("w:color"), "000000")
        borders.append(element)
    tbl_pr.append(borders)


def add_table(caption, headers, rows, font_size=9, column_widths=None):
    caption_paragraph = doc.add_paragraph(f"Таблица {caption}", style="TableCaption")
    caption_paragraph.paragraph_format.keep_with_next = True
    table = doc.add_table(rows=1, cols=len(headers))
    set_table_borders(table)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    header_cells = table.rows[0].cells
    for index, header in enumerate(headers):
        cell = header_cells[index]
        cell.text = ""
        paragraph = cell.paragraphs[0]
        paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
        paragraph.paragraph_format.first_line_indent = Cm(0)
        paragraph.paragraph_format.line_spacing = 1.0
        run = paragraph.add_run(str(header))
        set_run_font(run, size=font_size, bold=True)
    for row in rows:
        cells = table.add_row().cells
        for index, value in enumerate(row):
            cell = cells[index]
            cell.text = ""
            paragraph = cell.paragraphs[0]
            paragraph.alignment = (
                WD_ALIGN_PARAGRAPH.LEFT if index == 0 else WD_ALIGN_PARAGRAPH.CENTER
            )
            paragraph.paragraph_format.first_line_indent = Cm(0)
            paragraph.paragraph_format.line_spacing = 1.0
            run = paragraph.add_run(str(value))
            set_run_font(run, size=font_size)
    if column_widths:
        for row in table.rows:
            for index, width in enumerate(column_widths):
                row.cells[index].width = Cm(width)
    all_rows = list(table.rows)
    for row in all_rows:
        tr_pr = row._tr.get_or_add_trPr()
        tr_pr.append(OxmlElement("w:cantSplit"))
    header_tr_pr = all_rows[0]._tr.get_or_add_trPr()
    header_tr_pr.append(OxmlElement("w:tblHeader"))
    for row in all_rows[:-1]:
        for cell in row.cells:
            for paragraph in cell.paragraphs:
                paragraph.paragraph_format.keep_with_next = True
    doc.add_paragraph()
    return table


def add_toc():
    paragraph = doc.add_paragraph()
    paragraph.paragraph_format.first_line_indent = Cm(0)
    run = paragraph.add_run()
    fldChar = OxmlElement("w:fldChar")
    fldChar.set(qn("w:fldCharType"), "begin")
    fldChar.set(qn("w:dirty"), "true")
    instrText = OxmlElement("w:instrText")
    instrText.set(qn("xml:space"), "preserve")
    instrText.text = 'TOC \\o "1-3" \\h \\z \\u'
    fldChar2 = OxmlElement("w:fldChar")
    fldChar2.set(qn("w:fldCharType"), "separate")
    text = OxmlElement("w:t")
    text.text = "Обновите поле оглавления (F9)."
    fldChar3 = OxmlElement("w:fldChar")
    fldChar3.set(qn("w:fldCharType"), "end")
    run._r.append(fldChar)
    run._r.append(instrText)
    run._r.append(fldChar2)
    run._r.append(text)
    run._r.append(fldChar3)
    settings = doc.settings.element
    update_fields = OxmlElement("w:updateFields")
    update_fields.set(qn("w:val"), "true")
    settings.append(update_fields)


add_heading("", 1)
doc.paragraphs[-1]._element.getparent().remove(doc.paragraphs[-1]._element)

for _ in range(1):
    centered("")
centered("МИНОБРНАУКИ РОССИИ", bold=True)
centered("САНКТ–ПЕТЕРБУРГСКИЙ ГОСУДАРСТВЕННЫЙ", bold=True)
centered("ЭЛЕКТРОТЕХНИЧЕСКИЙ УНИВЕРСИТЕТ", bold=True)
centered("«ЛЭТИ» ИМ. В.И. УЛЬЯНОВА (ЛЕНИНА)", bold=True)
centered("Кафедра вычислительной техники", bold=True)
for _ in range(5):
    centered("")
centered("ОТЧЕТ", size=16, bold=True)
centered("по лабораторной работе №2", bold=True)
centered("по дисциплине «Машинное обучение»", bold=True)
centered("Тема: «Кластеризация»", bold=True)
for _ in range(6):
    centered("")

signature_table = doc.add_table(rows=2, cols=3)
signature_table.alignment = WD_TABLE_ALIGNMENT.CENTER
signature_table.autofit = True
signature_rows = [
    ("Студент гр. 2387", "________________", "Недовизий А.И."),
    ("Преподаватель", "________________", "Турсуков Н.О."),
]
for row_index, row_values in enumerate(signature_rows):
    for column_index, value in enumerate(row_values):
        cell = signature_table.cell(row_index, column_index)
        cell.text = ""
        paragraph = cell.paragraphs[0]
        paragraph.paragraph_format.first_line_indent = Cm(0)
        paragraph.paragraph_format.line_spacing = 1.0
        if column_index == 0:
            paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT
        elif column_index == 1:
            paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
        else:
            paragraph.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        run = paragraph.add_run(value)
        set_run_font(run, size=14)
for row in signature_table.rows:
    row.cells[0].width = Cm(6)
    row.cells[1].width = Cm(5)
    row.cells[2].width = Cm(5)

for _ in range(4):
    centered("")
centered("Санкт–Петербург")
centered("2026")
doc.add_page_break()

paragraph = doc.add_paragraph()
paragraph.paragraph_format.first_line_indent = Cm(0)
run = paragraph.add_run("Оглавление")
set_run_font(run, size=14, bold=True)
add_toc()
doc.add_page_break()

add_heading("Цель работы", 1)
add_body(
    "Закрепить навыки предобработки данных и применения методов машинного обучения "
    "для решения задач кластеризации."
)

add_heading("Задачи", 1)
tasks = [
    "1. Провести цикл предварительной обработки данных: визуализировать значимые признаки, выполнить очистку данных, построить матрицу корреляций и подготовить признаки к кластеризации.",
    "2. Провести обучение моделей методами кластеризации:",
    "a. метод К-средних: подобрать оптимальное число кластеров k с использованием метода локтя и силуэтного анализа, протестировать разные инициализации (k-means++ и random), реализовать ансамблевую кластеризацию на основе нескольких запусков K-Means;",
    "b. DBSCAN: подобрать гиперпараметры при помощи анализа k-расстояний, исследовать чувствительность алгоритма к шуму и выбросам;",
    "c. иерархическая кластеризация: провести кластеризацию с разными метриками расстояния, определить оптимальное число кластеров с помощью дендрограммы, сравнить время выполнения при увеличении объёма данных;",
    "3. Провести оценку моделей:",
    "a. экспертная оценка;",
    "b. сравнение разбиения на классы с помощью кластеризации с реальными классами;",
    "c. визуализация предсказанных значений;",
    "d. кросс-валидация устойчивости кластеров через многократную подвыборку данных.",
]
for task in tasks:
    add_list_item(task)

add_heading("Теория", 1)
add_body(
    "Кластеризация относится к методам обучения без учителя. Её цель — разделить "
    "объекты на группы (кластеры) так, чтобы объекты внутри одной группы были похожи "
    "друг на друга, а объекты из разных групп различались. В отличие от классификации, "
    "заранее известные метки классов отсутствуют, поэтому качество кластеризации "
    "оценивают как внутренними метриками, так и сопоставлением с реальными классами."
)
add_theory_subheading("Метод K-Means")
add_body(
    "K-Means (метод K-средних) заранее получает число кластеров k и ищет такие "
    "центроиды, чтобы сумма квадратов расстояний от объектов до своих центроидов "
    "была минимальной. Алгоритм состоит из следующих шагов: задать k, инициализировать "
    "центроиды, отнести каждый объект к ближайшему центроиду, пересчитать центроиды как "
    "среднее объектов кластера и повторять два последних шага до сходимости. "
    "Используются инициализации random, k-means++ и farthest-first. Основные "
    "гиперпараметры: n_clusters, init, n_init, max_iter, tol."
)
add_body(
    "Для выбора числа кластеров применяют метод локтя (по инерции) и силуэтный анализ. "
    "Силуэт объекта i равен s(i) = (b(i) − a(i)) / max(a(i), b(i)), где a(i) — среднее "
    "расстояние до объектов своего кластера, b(i) — среднее расстояние до объектов "
    "ближайшего чужого кластера. Средний силуэт лежит в диапазоне от −1 до 1; чем он "
    "выше, тем лучше разбиение. Ансамблевая кластеризация объединяет несколько запусков "
    "K-Means: для каждой пары объектов считается доля запусков, в которых они попали в "
    "один кластер, после чего по матрице совместной встречаемости выполняется итоговая "
    "иерархическая кластеризация."
)
add_theory_subheading("Алгоритм DBSCAN")
add_body(
    "DBSCAN (Density-Based Spatial Clustering of Applications with Noise) ищет кластеры "
    "как области высокой плотности и отдельно выделяет шум. Основные параметры: eps — "
    "радиус окрестности и min_samples — минимальное число точек в окрестности для "
    "ядровой точки. Точка является ядровой, если в её eps-окрестности не меньше "
    "min_samples точек. Граничная точка не является ядровой, но попадает в окрестность "
    "ядровой точки. Остальные точки получают метку шума −1. Кластеры строятся как "
    "максимальные множества точек, связанных по плотности. Для выбора eps строят график "
    "k-расстояний: для каждого объекта вычисляют расстояние до k-го ближайшего соседа, "
    "сортируют значения и ищут колено, после которого расстояние резко растёт."
)
add_theory_subheading("Иерархическая кластеризация")
add_body(
    "Агломеративная иерархическая кластеризация начинает с того, что каждый объект "
    "считается отдельным кластером, и последовательно объединяет два ближайших кластера. "
    "Результат изображается дендрограммой. Расстояние между объектами может задаваться "
    "евклидовой, манхэттенской или косинусной метрикой, а расстояние между кластерами — "
    "методами single, complete, average или Ward linkage. Число кластеров выбирают, "
    "разрезая дендрограмму на нужной высоте. Основной недостаток метода — квадратичная "
    "сложность по времени и памяти, поэтому на больших данных его применяют к "
    "подвыборкам."
)
add_theory_subheading("Метрики качества")
add_body(
    "Silhouette оценивает компактность и отделённость кластеров. ARI (Adjusted Rand "
    "Index) измеряет согласие разбиения с реальными классами с поправкой на случайность. "
    "NMI (Normalized Mutual Information) оценивает взаимную информацию между разбиением "
    "и классами. Purity показывает долю объектов, для которых кластер содержит "
    "наибольшее число объектов одного класса; она может быть завышена при сильном "
    "дисбалансе классов, поэтому используется вместе с ARI и NMI."
)

add_heading("Выполнение работы", 1)
add_heading("1. Предварительная обработка данных", 2)
add_body(
    f"В качестве набора данных выбран датасет Perfume Type Classification, содержащий "
    f"{DATASET['n_rows_raw']} записей и 11 столбцов: 10 признаков и целевую переменную "
    f"perfume_category. Целевая переменная принимает четыре значения: Eau de Cologne, "
    f"Eau de Toilette, Eau de Parfum и Perfume Extract. Признаки описывают стойкость "
    f"аромата, интенсивность шлейфа, число верхних нот, цену, концентрацию эфирных "
    f"масел, семейство аромата, ценовой сегмент бренда, целевую аудиторию, наличие "
    f"спирта и признак лимитированного выпуска."
)
add_body(
    f"В исходных данных обнаружено {DATASET['n_duplicates']} дубликатов и пропуски: "
    f"price_usd — {DATASET['missing_raw']['price_usd']}, brand_tier — "
    f"{DATASET['missing_raw']['brand_tier']}, contains_alcohol — "
    f"{DATASET['missing_raw']['contains_alcohol']}. После удаления дубликатов осталось "
    f"{DATASET['n_rows']} записей; пропуски в числовых признаках заполнены медианой, "
    f"в категориальных — строкой Unknown. На рисунке 1 показано распределение классов "
    f"после удаления дубликатов."
)
add_figure("fig01_target.png", "1 – Распределение классов perfume_category", 13)
add_body(
    "Набор несбалансирован: после очистки Eau de Toilette содержит 22 014 объектов, "
    "Eau de Parfum — 19 254, Eau de Cologne — 8 258, Perfume Extract — 5 474. "
    "Поскольку кластеризация является обучением без учителя, балансировка классов "
    "не применялась: она изменила бы естественную структуру данных. Целевая переменная "
    "используется только для оценки согласия кластеров с реальными классами."
)
add_body(
    "На рисунке 2 приведена матрица корреляций числовых признаков. Наиболее заметные "
    "связи: concentration_percent — longevity_hours (0,60), concentration_percent — "
    "price_usd (0,59), concentration_percent — sillage_score (0,51), longevity_hours — "
    "price_usd (0,48), top_note_count — concentration_percent (−0,38). Это согласуется "
    "с предметной областью: более концентрированные ароматы держатся дольше, стоят "
    "дороже и имеют меньше верхних нот. Сильных мультиколлинеарных связей (|r| > 0,8) "
    "нет."
)
add_figure("fig02_corr.png", "2 – Матрица корреляций числовых признаков", 14)
add_body(
    "На рисунках 3–7 показаны распределения значимых признаков. Классы упорядочены "
    "по концентрации, стойкости и цене: Eau de Cologne имеет наименьшие значения, "
    "Perfume Extract — наибольшие, а Eau de Toilette и Eau de Parfum занимают "
    "промежуточное положение. При этом распределения заметно перекрываются, поэтому "
    "идеального разделения на четыре класса в признаковом пространстве нет."
)
add_figure("fig03_features.png", "3 – Распределения признаков contains_alcohol, price_usd и brand_tier", 16)
add_figure("fig04_concentration.png", "4 – Распределения признака concentration_percent по классам", 15)
add_figure("fig05_longevity.png", "5 – Распределения признака longevity_hours по классам", 15)
add_figure("fig06_price.png", "6 – Распределения признака price_usd", 17)
add_figure("fig07_sillage.png", "7 – Распределения признака sillage_score по классам", 15)
add_body(
    f"На рисунке 8 показана проекция данных на первые две главные компоненты. Две "
    f"компоненты объясняют {number((DATASET['pca_evr'][0] + DATASET['pca_evr'][1]) * 100, 1)} % "
    f"дисперсии; классы образуют общую область с частичным перекрытием. Это объясняет, "
    f"почему кластеризация не сможет идеально восстановить perfume_category."
)
add_figure("fig08_pca_true.png", "8 – Проекция данных на первые две главные компоненты", 14)
add_body(
    f"Для кластеризации категориальные признаки закодированы OneHotEncoder, числовые — "
    f"масштабированы StandardScaler; пропуски заполняются внутри pipeline. Итоговая "
    f"матрица имеет размерность {DATASET['n_rows']} × {DATASET['n_features_encoded']}. "
    f"PCA используется только для визуализации, кластеризация выполняется в полном "
    f"масштабированном пространстве признаков."
)

add_heading("2. Обучение моделей кластеризации", 2)
add_heading("a. Метод К-средних", 3)
add_body(
    f"Для выбора числа кластеров построены графики инерции и среднего силуэта "
    f"(рисунок 9). Инерция монотонно убывает, явного излома нет. Силуэт максимален "
    f"при k = 3 ({number(K[3]['silhouette'])}), при k = 2 он равен "
    f"{number(K[2]['silhouette'])}, при k = 4 — {number(K[4]['silhouette'])}, при "
    f"k = 5 — {number(K[5]['silhouette'])}. Внутренние метрики указывают на k = 2–3, "
    f"тогда как в данных четыре истинных класса. Для содержательного сравнения с "
    f"реальными классами в качестве рабочего выбрано k = 4; вариант k = 2 также "
    f"рассмотрен при оценке."
)
add_figure("fig09_elbow.png", "9 – Зависимость инерции и среднего силуэта от числа кластеров", 16)
add_body(
    "Числовые результаты подбора числа кластеров приведены в таблице 1. Помимо "
    "внутренних метрик, в таблице показаны ARI и NMI относительно истинных классов; "
    "они используются только для анализа и не участвуют в выборе k."
)
add_table(
    "1 – Результаты K-Means для разного числа кластеров",
    ["k", "Инерция", "Silhouette", "ARI", "NMI"],
    [
        [
            row["k"],
            f"{row['inertia']:.0f}",
            number(row["silhouette"]),
            number(row["ari"]),
            number(row["nmi"]),
        ]
        for row in R["kmeans"]
    ],
    font_size=9,
    column_widths=[1.2, 3.2, 2.6, 2.2, 2.2],
)
add_body(
    f"Сравнение инициализаций k-means++ и random по пяти запускам (n_init = 1) "
    f"приведено на рисунке 10 и в таблице 2. Random-инициализация оказалась более "
    f"стабильной: средняя инерция {INIT['random']['inertia_mean']:.0f} ± "
    f"{INIT['random']['inertia_std']:.0f}, средний силуэт "
    f"{number(INIT['random']['silhouette_mean'])} ± "
    f"{number(INIT['random']['silhouette_std'])}. У k-means++ средняя инерция "
    f"{INIT['k-means++']['inertia_mean']:.0f} ± "
    f"{INIT['k-means++']['inertia_std']:.0f}, средний силуэт "
    f"{number(INIT['k-means++']['silhouette_mean'])} ± "
    f"{number(INIT['k-means++']['silhouette_std'])}. При этом один из запусков "
    f"k-means++ нашёл лучшее решение с инерцией 325 260 и силуэтом 0,205, но в "
    f"остальных случаях решения не лучше random. Это показывает, что целевая функция "
    f"K-Means имеет несколько локальных оптимумов."
)
add_figure("fig10_init.png", "10 – Сравнение инициализаций k-means++ и random", 15)
add_table(
    "2 – Сравнение инициализаций K-Means",
    ["Инициализация", "Инерция, среднее ± std", "Silhouette, среднее ± std", "ARI, среднее ± std"],
    [
        [
            "k-means++",
            f"{INIT['k-means++']['inertia_mean']:.0f} ± {INIT['k-means++']['inertia_std']:.0f}",
            f"{number(INIT['k-means++']['silhouette_mean'])} ± {number(INIT['k-means++']['silhouette_std'])}",
            f"{number(INIT['k-means++']['ari_mean'])} ± {number(INIT['k-means++']['ari_std'])}",
        ],
        [
            "random",
            f"{INIT['random']['inertia_mean']:.0f} ± {INIT['random']['inertia_std']:.0f}",
            f"{number(INIT['random']['silhouette_mean'])} ± {number(INIT['random']['silhouette_std'])}",
            f"{number(INIT['random']['ari_mean'])} ± {number(INIT['random']['ari_std'])}",
        ],
    ],
    font_size=8,
    column_widths=[3.0, 4.5, 4.5, 4.0],
)
add_body(
    f"Ансамблевая кластеризация реализована через матрицу совместной встречаемости по "
    f"20 запускам K-Means с random-инициализацией на подвыборке 5 000 объектов; "
    f"итоговое разбиение получено иерархической кластеризацией по матрице "
    f"1 − coassociation (average linkage). Результаты приведены на рисунке 11 и в "
    f"таблице 3. Ансамбль практически совпал с одиночным K-Means на той же подвыборке: "
    f"ARI {number(ENSEMBLE['metrics'][1]['ari'])} против "
    f"{number(ENSEMBLE['metrics'][0]['ari'])}, NMI "
    f"{number(ENSEMBLE['metrics'][1]['nmi'])} против "
    f"{number(ENSEMBLE['metrics'][0]['nmi'])}, purity "
    f"{number(ENSEMBLE['metrics'][1]['purity'])} против "
    f"{number(ENSEMBLE['metrics'][0]['purity'])}. Среднее попарное ARI между запусками "
    f"равно {number(ENSEMBLE['pairwise_ari_mean'])} ± "
    f"{number(ENSEMBLE['pairwise_ari_std'])}. Ансамбль не улучшил согласие с классами, "
    f"но подтвердил, что большинство запусков сходится к одному и тому же локальному "
    f"оптимуму."
)
add_figure("fig11_ensemble.png", "11 – Сравнение одиночного K-Means и ансамблевой кластеризации", 14)
add_table(
    "3 – Одиночный K-Means и ансамбль на подвыборке 5 000 объектов",
    ["Метод", "Кластеров", "Silhouette", "ARI", "NMI", "Purity"],
    [
        [
            row["method"],
            row["n_clusters"],
            number(row["silhouette"]),
            number(row["ari"]),
            number(row["nmi"]),
            number(row["purity"]),
        ]
        for row in ENSEMBLE["metrics"]
    ],
    font_size=8,
    column_widths=[4.2, 2.2, 2.5, 2.2, 2.2, 2.2],
)

add_heading("b. DBSCAN", 3)
add_body(
    f"Для выбора eps построен график k-расстояний при min_samples = 11 (рисунок 12). "
    f"Медиана расстояния до 11-го соседа равна "
    f"{number(R['kdist']['quantiles']['0.5'])}, 90-й процентиль — "
    f"{number(R['kdist']['quantiles']['0.9'])}, максимум — "
    f"{number(R['kdist']['max'])}. По точке перегиба и 90-му процентилю с запасом "
    f"выбрано eps = 1,9."
)
add_figure("fig12_kdist.png", "12 – График k-расстояний для выбора eps", 15)
add_body(
    f"Чувствительность DBSCAN к eps при min_samples = 11 показана на рисунке 13 и в "
    f"таблице 4. При eps = 1,0 алгоритм дробит данные на "
    f"{DBSCAN_EPS[1.0]['n_clusters']} кластеров, а "
    f"{percent(DBSCAN_EPS[1.0]['noise_fraction'])} объектов объявляет шумом. При "
    f"eps = 1,5 получается {DBSCAN_EPS[1.5]['n_clusters']} кластеров и "
    f"{percent(DBSCAN_EPS[1.5]['noise_fraction'])} шума, при eps = 1,7 — "
    f"{DBSCAN_EPS[1.7]['n_clusters']} кластера и "
    f"{percent(DBSCAN_EPS[1.7]['noise_fraction'])} шума, при eps = 1,9 — "
    f"{DBSCAN_EPS[1.9]['n_clusters']} кластера и "
    f"{percent(DBSCAN_EPS[1.9]['noise_fraction'])} шума, при eps = 2,0 — "
    f"{DBSCAN_EPS[2.0]['n_clusters']} кластера и "
    f"{percent(DBSCAN_EPS[2.0]['noise_fraction'])} шума. Согласие с истинными классами "
    f"во всех случаях близко к нулю."
)
add_figure("fig13_dbscan_sens.png", "13 – Чувствительность DBSCAN к eps", 16)
add_table(
    "4 – Зависимость результата DBSCAN от eps при min_samples = 11",
    ["eps", "Кластеров", "Доля шума", "Silhouette", "ARI", "NMI"],
    [
        [
            number(row["eps"], 1),
            row["n_clusters"],
            percent(row["noise_fraction"]),
            number(row["silhouette"]) if row["silhouette"] == row["silhouette"] else "—",
            number(row["ari"]),
            number(row["nmi"]),
        ]
        for row in R["dbscan_eps"]
    ],
    font_size=8,
    column_widths=[1.6, 2.3, 2.6, 2.6, 2.2, 2.2],
)
add_body(
    "Дополнительно выполнен перебор min_samples (5, 10, 20, 40) и eps; результаты "
    "показаны на рисунке 14 и в таблице 5. Наибольший силуэт среди невырожденных "
    "конфигураций достигается при min_samples = 5 и eps = 2,2, однако при этом почти "
    "все объекты сливаются в несколько крупных кластеров, а ARI остаётся около нуля. "
    "Это показывает, что выбирать параметры DBSCAN только по силуэту нельзя: можно "
    "получить геометрически хорошее, но содержательно бесполезное разбиение. Рабочей "
    "конфигурацией выбрана eps = 1,9, min_samples = 11, согласованная с графиком "
    "k-расстояний."
)
add_figure("fig13b_dbscan_grid.png", "14 – Подбор гиперпараметров DBSCAN по сетке eps и min_samples", 17)
add_table(
    "5 – Фрагмент сетки гиперпараметров DBSCAN",
    ["min_samples", "eps", "Кластеров", "Доля шума", "Silhouette", "ARI"],
    [
        [
            row["min_samples"],
            number(row["eps"], 1),
            row["n_clusters"],
            percent(row["noise_fraction"]),
            number(row["silhouette"]) if row["silhouette"] == row["silhouette"] else "—",
            number(row["ari"]),
        ]
        for row in R["dbscan_grid"]
        if row["eps"] in (1.5, 1.7, 2.0, 2.2)
    ],
    font_size=7,
    column_widths=[2.0, 1.6, 2.2, 2.5, 2.5, 2.2],
)
add_body(
    f"Для проверки устойчивости к выбросам в данные добавлялись искусственные объекты "
    f"(1 %, 5 %, 10 %), равномерно распределённые в расширенном диапазоне "
    f"стандартизированных признаков. Результаты приведены на рисунке 15 и в таблице 6. "
    f"Все добавленные выбросы (100 %) отнесены к шуму; доля шума среди исходных "
    f"объектов не изменилась ({percent(DBSCAN_NOISE[0.0]['original_noise_fraction'], 2)}), "
    f"число кластеров осталось равным {DBSCAN_NOISE[0.0]['n_clusters']}, ARI практически "
    f"не изменился. Таким образом, DBSCAN устойчив к явным выбросам, но не "
    f"восстанавливает целевые классы."
)
add_figure("fig14_dbscan_noise.png", "15 – Устойчивость DBSCAN к искусственным выбросам", 16)
add_table(
    "6 – Чувствительность DBSCAN к искусственным выбросам",
    ["Доля выбросов", "Выбросов", "Отнесено к шуму", "Шум среди исходных", "Кластеров", "ARI"],
    [
        [
            percent(row["contamination"], 0) if row["contamination"] else "0 %",
            row["n_outliers"],
            "100 %" if row["contamination"] else "—",
            percent(row["original_noise_fraction"], 2),
            row["n_clusters"],
            number(row["ari_original"]),
        ]
        for row in R["dbscan_noise"]
    ],
    font_size=8,
    column_widths=[2.5, 2.0, 2.8, 3.2, 2.0, 2.0],
)
add_body(
    f"Итоговое разбиение DBSCAN (eps = 1,9, min_samples = 11): "
    f"{DBSCAN_FINAL['n_clusters']} кластера, "
    f"{percent(DBSCAN_FINAL['noise_fraction'], 2)} шума, silhouette "
    f"{number(DBSCAN_FINAL['silhouette'])}, ARI {number(DBSCAN_FINAL['ari'])}, NMI "
    f"{number(DBSCAN_FINAL['nmi'])}, purity {number(DBSCAN_FINAL['purity'])}. Purity "
    f"заметно ниже, чем у K-Means и иерархической кластеризации, и при ARI около нуля "
    f"подтверждает, что плотностные кластеры не совпадают с категориями ароматов. "
    f"Визуализация разбиения в проекции PCA приведена на рисунке 16."
)
add_figure("fig15_dbscan_pca.png", "16 – Кластеры DBSCAN в проекции PCA", 14)

add_heading("c. Иерархическая кластеризация", 3)
add_body(
    "Дендрограмма построена по выборке 1 000 объектов (average linkage, евклидово "
    "расстояние) и приведена на рисунке 17. Порог для четырёх кластеров выбран между "
    "четвёртым и третьим с конца слияниями."
)
add_figure("fig16_dendrogram.png", "17 – Дендрограмма иерархической кластеризации", 16)
add_body(
    "Сравнение различных методов связи и метрик расстояния приведено в таблице 7. "
    "Лучший ARI показывает complete linkage с евклидовым расстоянием "
    f"({number(HIER[('complete', 'euclidean')]['ari'])}), близкий результат даёт "
    f"average linkage с косинусным расстоянием "
    f"({number(HIER[('average', 'cosine')]['ari'])}) и Ward "
    f"({number(HIER[('ward', 'euclidean')]['ari'])}). Single linkage показывает ARI "
    f"{number(HIER[('single', 'euclidean')]['ari'])} из-за эффекта цепочки: в его "
    f"разбиении появляются кластеры размера 1. Average linkage с манхэттенским "
    f"расстоянием также даёт ARI около нуля, хотя формально выделяет четыре кластера."
)
add_table(
    "7 – Сравнение методов связи и метрик расстояния",
    ["Linkage", "Метрика", "Время, с", "Кластеров", "Размеры кластеров", "ARI", "NMI", "Silhouette"],
    [
        [
            row["linkage"],
            row["metric"],
            number(row["time"], 4),
            row["n_clusters"],
            ", ".join(str(value) for value in row["sizes"]),
            number(row["ari"]),
            number(row["nmi"]),
            number(row["silhouette"]),
        ]
        for row in R["hierarchical"]
    ],
    font_size=7,
    column_widths=[2.0, 2.0, 1.6, 1.8, 3.8, 1.6, 1.6, 1.8],
)
add_body(
    f"Масштабируемость исследована на подвыборках от 1 000 до 16 000 объектов "
    f"(рисунок 18, таблица 8). Время растёт квадратично: "
    f"{number(SCALABILITY[0]['time'], 4)} с при 1 000, "
    f"{number(SCALABILITY[1]['time'], 4)} с при 2 000, "
    f"{number(SCALABILITY[2]['time'], 4)} с при 4 000, "
    f"{number(SCALABILITY[3]['time'], 4)} с при 8 000, "
    f"{number(SCALABILITY[4]['time'], 4)} с при 16 000. Экстраполяция на 55 000 "
    f"объектов даёт примерно 40–50 с и требует порядка 12 ГБ памяти для матрицы "
    f"расстояний, поэтому на полном наборе иерархическая кластеризация не "
    f"запускалась. Для итогового сравнения использовалась подвыборка 5 000 объектов."
)
add_figure("fig17_hier_scalability.png", "18 – Масштабируемость иерархической кластеризации", 14)
add_table(
    "8 – Время иерархической кластеризации при разном объёме данных",
    ["Число объектов", "Время, с", "Время / n², мкс"],
    [
        [
            row["n"],
            number(row["time"], 4),
            number(row["time"] / (row["n"] ** 2) * 1e6, 3),
        ]
        for row in SCALABILITY
    ],
    font_size=9,
    column_widths=[4.0, 3.5, 4.5],
)

add_heading("3. Провести оценку моделей", 2)
add_heading("a. Экспертная оценка", 3)
add_body(
    "Профили кластеров K-Means (k = 4) приведены в таблице 9. Кластер 0 объединяет "
    "20 844 объекта с низкой концентрацией (7,70 %), стойкостью (3,55 ч) и ценой "
    "(56,66 $); в нём преобладают Eau de Cologne и Eau de Toilette. Кластер 1 "
    "(20 603 объекта) имеет средние значения (15,55 %, 6,47 ч, 104,94 $), в нём "
    "преобладают Eau de Parfum и Eau de Toilette. Кластер 2 (7 419 объектов) — самый "
    "концентрированный и дорогой (25,10 %, 10,11 ч, 210,46 $), в нём преобладают "
    "Perfume Extract и Eau de Parfum. Кластер 3 (6 134 объекта) полностью состоит из "
    "limited_edition = 1 и смешивает классы."
)
add_table(
    "9 – Профили кластеров K-Means (k = 4)",
    [
        "Кластер",
        "Размер",
        "Стойкость, ч",
        "Шлейф",
        "Верхние ноты",
        "Цена, $",
        "Концентрация, %",
        "Преобладающий класс",
    ],
    [
        [
            cluster,
            PROFILES["sizes"][cluster],
            number(PROFILES["means"][cluster]["longevity_hours"]),
            number(PROFILES["means"][cluster]["sillage_score"]),
            number(PROFILES["means"][cluster]["top_note_count"]),
            number(PROFILES["means"][cluster]["price_usd"]),
            number(PROFILES["means"][cluster]["concentration_percent"]),
            PROFILES["dominant_class"][cluster],
        ]
        for cluster in ["0", "1", "2", "3"]
    ],
    font_size=7,
    column_widths=[1.6, 1.8, 2.0, 1.5, 1.9, 1.7, 2.3, 3.2],
)
add_body(
    "Три первых кластера упорядочены по концентрации, стойкости и цене и соответствуют "
    "предметной иерархии Eau de Cologne → Eau de Toilette → Eau de Parfum → Perfume "
    "Extract. Четвёртый кластер выделяет бинарный флаг лимитированного выпуска. "
    "Сопоставление кластеров с истинными классами приведено на рисунке 19."
)
add_figure("fig19_crosstab.png", "19 – Сопоставление кластеров K-Means и истинных классов", 14)
add_body(
    "Чтобы проверить влияние бинарных признаков, выполнена кластеризация без "
    "limited_edition и без обоих бинарных флагов (таблица 10). Без limited_edition "
    f"silhouette растёт с {number(FEATURE_SUBSET['Все признаки']['silhouette'])} до "
    f"{number(FEATURE_SUBSET['Без limited_edition']['silhouette'])}, а ARI немного "
    f"снижается ({number(FEATURE_SUBSET['Без limited_edition']['ari'])} против "
    f"{number(FEATURE_SUBSET['Все признаки']['ari'])}). Без обоих бинарных флагов "
    f"silhouette становится равным "
    f"{number(FEATURE_SUBSET['Без бинарных флагов']['silhouette'])}, а ARI падает до "
    f"{number(FEATURE_SUBSET['Без бинарных флагов']['ari'])}. Это показывает, что "
    f"бинарные признаки с малой встречаемостью доминируют в евклидовом расстоянии; "
    f"для смешанных данных разумно использовать Gower-расстояние или исключать такие "
    f"флаги."
)
add_table(
    "10 – Влияние бинарных признаков на результат K-Means",
    ["Набор признаков", "Silhouette", "ARI", "NMI", "Purity"],
    [
        [
            row["features"],
            number(row["silhouette"]),
            number(row["ari"]),
            number(row["nmi"]),
            number(row["purity"]),
        ]
        for row in R["feature_subset"]
    ],
    font_size=8,
    column_widths=[5.0, 2.6, 2.2, 2.2, 2.2],
)

add_heading("b. Сравнение разбиения на классы с помощью кластеризации с реальными", 3)
add_body(
    "Для сравнения разбиений с реальными классами использованы ARI, NMI и purity. "
    "ARI учитывает случайное совпадение и равен 1 при полном совпадении разбиений; "
    "NMI измеряет взаимную информацию; purity показывает долю объектов, для которых "
    "кластер содержит наибольшее число объектов одного класса. Результаты приведены "
    "в таблице 11."
)
add_table(
    "11 – Сравнение кластеризаций с реальными классами",
    ["Метод", "Кластеров", "Шум", "Silhouette", "ARI", "NMI", "Purity"],
    [
        [
            row["method"],
            row["n_clusters"],
            percent(row["noise_fraction"]),
            number(row["silhouette"]),
            number(row["ari"]),
            number(row["nmi"]),
            number(row["purity"]),
        ]
        for row in R["comparison"]
    ],
    font_size=7,
    column_widths=[5.4, 1.8, 1.8, 2.2, 1.8, 1.8, 1.8],
)
add_body(
    "Лучшее согласие среди четырёхкластерных решений показывает K-Means k = 4: "
    f"ARI {number(COMPARISON['K-Means, k=4']['ari'])}, NMI "
    f"{number(COMPARISON['K-Means, k=4']['nmi'])}, purity "
    f"{number(COMPARISON['K-Means, k=4']['purity'])}. K-Means k = 2 даёт более высокий "
    f"ARI {number(COMPARISON['K-Means, k=2']['ari'])} и purity "
    f"{number(COMPARISON['K-Means, k=2']['purity'])}, но выделяет лишь два кластера и "
    f"не соответствует числу истинных классов. Иерархическая кластеризация complete "
    f"linkage на 5 000 объектах даёт ARI "
    f"{number(COMPARISON['Иерархическая (complete, 5000)']['ari'])}, ансамбль — "
    f"{number(COMPARISON['Ансамбль K-Means (5000)']['ari'])}, DBSCAN — "
    f"{number(COMPARISON['DBSCAN']['ari'])}. Низкое ARI у DBSCAN объясняется тем, что "
    f"плотностные кластеры не совпадают с категориями ароматов; purity на невыбросовых "
    f"объектах равна {number(COMPARISON['DBSCAN']['purity'])} и заметно ниже, чем у "
    f"K-Means и иерархической кластеризации. Purity чувствительна к дисбалансу классов, "
    f"поэтому используется только вместе с ARI и NMI."
)

add_heading("c. Визуализация предсказанных значений", 3)
add_body(
    "На рисунке 20 показаны кластеры K-Means в проекции PCA, на рисунке 21 — в "
    "проекции t-SNE, построенной по подвыборке 3 000 объектов. Кластеры занимают "
    "крупные области, но их границы не совпадают с границами истинных классов. Это "
    "подтверждает частичное перекрытие признаковых распределений и объясняет, почему "
    "внешние метрики не достигают единицы. Визуализация DBSCAN ранее приведена на "
    "рисунке 16: основная масса объектов образует один крупный плотный кластер, "
    "несколько небольших кластеров соответствуют локальным сгущениям, а шум — "
    "разреженным областям."
)
add_figure("fig18_kmeans_pca.png", "20 – Кластеры K-Means (k = 4) в проекции PCA", 14)
add_figure("fig20_tsne.png", "21 – Кластеры K-Means (k = 4) в проекции t-SNE", 14)

add_heading("d. Провести кросс-валидацию устойчивости кластеров через многократную подвыборку данных", 3)
add_body(
    "Для оценки устойчивости зафиксирована контрольная подвыборка 20 % объектов. На "
    "оставшихся 80 % десять раз случайно выбиралось 80 % объектов, обучался K-Means "
    "(k = 4), после чего предсказания сравнивались на одной и той же контрольной "
    "подвыборке. Результаты приведены в таблице 12 и на рисунке 22."
)
add_table(
    "12 – Устойчивость K-Means при многократной подвыборке",
    ["Показатель", "Значение"],
    [
        ["Среднее попарное ARI между запусками", number(STABILITY["pairwise_ari_mean"])],
        ["Стандартное отклонение попарного ARI", number(STABILITY["pairwise_ari_std"])],
        ["Минимальное попарное ARI", number(STABILITY["pairwise_ari_min"])],
        ["Максимальное попарное ARI", number(STABILITY["pairwise_ari_max"])],
        ["Среднее ARI относительно истинных классов", number(STABILITY["ari_vs_true_mean"])],
        ["Стандартное отклонение ARI относительно классов", number(STABILITY["ari_vs_true_std"])],
    ],
    font_size=9,
    column_widths=[10.0, 4.0],
)
add_body(
    f"Среднее попарное ARI между запусками составило "
    f"{number(STABILITY['pairwise_ari_mean'])} при стандартном отклонении "
    f"{number(STABILITY['pairwise_ari_std'])} (минимум "
    f"{number(STABILITY['pairwise_ari_min'])}, максимум "
    f"{number(STABILITY['pairwise_ari_max'])}). Среднее ARI относительно истинных "
    f"классов равно {number(STABILITY['ari_vs_true_mean'])} ± "
    f"{number(STABILITY['ari_vs_true_std'])}. Разброс объясняется двумя устойчивыми "
    f"локальными оптимумами: часть запусков сходится к разбиению с ARI около 0,248, "
    f"часть — к ARI около 0,322–0,325. Это согласуется с результатами сравнения "
    f"инициализаций и говорит о том, что устойчивость кластеров умеренная. Ансамблевая "
    f"кластеризация и увеличение n_init снижают зависимость от одного запуска, но не "
    f"устраняют неоднозначность, связанную с перекрытием классов."
)
add_figure("fig20_stability.png", "22 – Устойчивость K-Means при многократной подвыборке", 15)

add_heading("Выводы", 1)
add_body(
    "В ходе лабораторной работы освоены методы кластеризации K-Means, DBSCAN и "
    "иерархическая кластеризация, а также способы подбора их параметров и оценки "
    "качества. Предварительная обработка включала удаление 15 000 дубликатов, "
    "заполнение пропусков, кодирование категориальных признаков и стандартизацию; "
    "итоговая матрица имеет размерность 55 000 × 20. PCA показал, что первые две "
    "компоненты объясняют 40,6 % дисперсии, а классы существенно перекрываются."
)
add_body(
    "K-Means: внутренние метрики (силуэт) предпочитают k = 3 (0,195), но для сравнения "
    "с четырьмя истинными классами выбрано k = 4. Кластеры k = 4 упорядочены по "
    "концентрации, стойкости и цене и хорошо интерпретируются экспертно; ARI = 0,322, "
    "NMI = 0,407. Ансамбль из 20 запусков не улучшил согласие с классами, но "
    "подтвердил устойчивость основного локального оптимума. Кросс-валидация показала "
    "умеренную устойчивость: среднее попарное ARI 0,785 при стандартном отклонении "
    "0,280."
)
add_body(
    f"DBSCAN с eps = 1,9 и min_samples = 11 выделил {DBSCAN_FINAL['n_clusters']} кластера "
    f"и {percent(DBSCAN_FINAL['noise_fraction'], 2)} шума; согласие с классами близко к "
    f"нулю (ARI {number(DBSCAN_FINAL['ari'])}). Алгоритм устойчив к искусственным "
    f"выбросам: все добавленные выбросы отнесены к шуму, а разбиение исходных объектов "
    f"не изменилось. Однако для восстановления категорий ароматов DBSCAN не подходит."
)
add_body(
    "Иерархическая кластеризация: лучший ARI показывает complete linkage с евклидовым "
    "расстоянием (0,265 на выборке 1 000 объектов; 0,212 на выборке 5 000 объектов). "
    "Single linkage страдает от эффекта цепочки, а average linkage с манхэттенским "
    "расстоянием даёт ARI около нуля. Время работы растёт квадратично, поэтому на "
    "полном наборе 55 000 объектов метод требует около 12 ГБ памяти и не "
    "использовался."
)
add_body(
    "В целом кластеризация позволила выявить содержательную структуру данных — "
    "уровень концентрации и стойкости, а также бинарные флаги, — но не позволила "
    "однозначно восстановить четыре целевых класса из-за их перекрытия. Результаты "
    "показывают, что внутренние метрики (silhouette, инерция) и внешние метрики "
    "(ARI, NMI, purity) оценивают разные свойства разбиения, поэтому выводы о качестве "
    "кластеризации должны опираться на совместный анализ метрик и содержательную "
    "интерпретацию."
)

doc.add_page_break()
add_heading("Приложение А", 1)
add_heading("Исходный код программы", 2)
notebook = nbformat.read(NOTEBOOK, as_version=4)
for cell in notebook.cells:
    if cell.cell_type != "code":
        continue
    source = cell.source.rstrip()
    if not source:
        continue
    for line in source.splitlines():
        paragraph = doc.add_paragraph(line if line else " ", style="CodeBlock")
        paragraph.paragraph_format.space_after = Pt(0)

doc.save(OUTPUT)
print("saved", OUTPUT)
