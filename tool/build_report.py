from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_ALIGN_VERTICAL, WD_CELL_VERTICAL_ALIGNMENT, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK, WD_LINE_SPACING
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "submission" / "report_assets"
OUTPUT = ROOT / "submission" / "Bao_cao_User_Registry.docx"

NAVY = "0B2034"
BLUE = "2463EB"
TEAL = "35CFC1"
PALE = "F1F6F5"
PALE_BLUE = "EEF4FF"
MID = "5B6B7D"
LIGHT_BORDER = "D9D9D9"
WHITE = "FFFFFF"
BLACK = "000000"
RED = "C73E3E"


def set_cell_shading(cell, fill: str) -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = tc_pr.find(qn("w:shd"))
    if shd is None:
        shd = OxmlElement("w:shd")
        tc_pr.append(shd)
    shd.set(qn("w:fill"), fill)


def set_cell_margins(cell, top=120, start=140, bottom=120, end=140) -> None:
    tc = cell._tc
    tc_pr = tc.get_or_add_tcPr()
    tc_mar = tc_pr.first_child_found_in("w:tcMar")
    if tc_mar is None:
        tc_mar = OxmlElement("w:tcMar")
        tc_pr.append(tc_mar)
    for side, value in (("top", top), ("start", start), ("bottom", bottom), ("end", end)):
        node = tc_mar.find(qn(f"w:{side}"))
        if node is None:
            node = OxmlElement(f"w:{side}")
            tc_mar.append(node)
        node.set(qn("w:w"), str(value))
        node.set(qn("w:type"), "dxa")


def set_table_borders(table, color=LIGHT_BORDER, size="6") -> None:
    tbl_pr = table._tbl.tblPr
    borders = tbl_pr.first_child_found_in("w:tblBorders")
    if borders is None:
        borders = OxmlElement("w:tblBorders")
        tbl_pr.append(borders)
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        tag = f"w:{edge}"
        node = borders.find(qn(tag))
        if node is None:
            node = OxmlElement(tag)
            borders.append(node)
        node.set(qn("w:val"), "single")
        node.set(qn("w:sz"), size)
        node.set(qn("w:space"), "0")
        node.set(qn("w:color"), color)


def set_repeat_table_header(row) -> None:
    tr_pr = row._tr.get_or_add_trPr()
    tbl_header = OxmlElement("w:tblHeader")
    tbl_header.set(qn("w:val"), "true")
    tr_pr.append(tbl_header)


def set_row_cant_split(row) -> None:
    tr_pr = row._tr.get_or_add_trPr()
    cant_split = OxmlElement("w:cantSplit")
    cant_split.set(qn("w:val"), "true")
    tr_pr.append(cant_split)


def set_column_widths(table, widths: list[float]) -> None:
    for row in table.rows:
        for idx, width in enumerate(widths):
            row.cells[idx].width = Inches(width)
            tc_pr = row.cells[idx]._tc.get_or_add_tcPr()
            tc_w = tc_pr.find(qn("w:tcW"))
            if tc_w is None:
                tc_w = OxmlElement("w:tcW")
                tc_pr.append(tc_w)
            tc_w.set(qn("w:w"), str(int(width * 1440)))
            tc_w.set(qn("w:type"), "dxa")


def set_run_font(run, name="Aptos", size=None, bold=None, color=None, italic=None) -> None:
    run.font.name = name
    run._element.get_or_add_rPr().get_or_add_rFonts().set(qn("w:ascii"), name)
    run._element.get_or_add_rPr().get_or_add_rFonts().set(qn("w:hAnsi"), name)
    run._element.get_or_add_rPr().get_or_add_rFonts().set(qn("w:eastAsia"), name)
    if size is not None:
        run.font.size = Pt(size)
    if bold is not None:
        run.bold = bold
    if color:
        run.font.color.rgb = RGBColor.from_string(color)
    if italic is not None:
        run.italic = italic


def add_page_number(paragraph) -> None:
    run = paragraph.add_run()
    begin = OxmlElement("w:fldChar")
    begin.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = "PAGE"
    separate = OxmlElement("w:fldChar")
    separate.set(qn("w:fldCharType"), "separate")
    text = OxmlElement("w:t")
    text.text = "1"
    end = OxmlElement("w:fldChar")
    end.set(qn("w:fldCharType"), "end")
    for node in (begin, instr, separate, text, end):
        run._r.append(node)
    set_run_font(run, size=9, color=MID)


def add_hyperlink(paragraph, text: str, url: str, color=BLUE) -> None:
    part = paragraph.part
    rel_id = part.relate_to(url, "http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink", is_external=True)
    hyperlink = OxmlElement("w:hyperlink")
    hyperlink.set(qn("r:id"), rel_id)
    run = OxmlElement("w:r")
    r_pr = OxmlElement("w:rPr")
    r_fonts = OxmlElement("w:rFonts")
    r_fonts.set(qn("w:ascii"), "Aptos")
    r_fonts.set(qn("w:hAnsi"), "Aptos")
    color_node = OxmlElement("w:color")
    color_node.set(qn("w:val"), color)
    underline = OxmlElement("w:u")
    underline.set(qn("w:val"), "single")
    r_pr.extend([r_fonts, color_node, underline])
    run.append(r_pr)
    t = OxmlElement("w:t")
    t.text = text
    run.append(t)
    hyperlink.append(run)
    paragraph._p.append(hyperlink)


def add_body(doc: Document, text: str, bold_lead: str | None = None, space_after=6) -> None:
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = 1.12
    if bold_lead and text.startswith(bold_lead):
        r1 = p.add_run(bold_lead)
        set_run_font(r1, bold=True)
        r2 = p.add_run(text[len(bold_lead):])
        set_run_font(r2)
    else:
        run = p.add_run(text)
        set_run_font(run)


def add_bullets(doc: Document, items: list[str], level=0) -> None:
    for item in items:
        p = doc.add_paragraph(style="List Bullet" if level == 0 else "List Bullet 2")
        p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.left_indent = Inches(0.25 + 0.25 * level)
        p.paragraph_format.first_line_indent = Inches(-0.17)
        run = p.add_run(item)
        set_run_font(run)


def add_numbered(doc: Document, items: list[str]) -> None:
    for idx, item in enumerate(items, start=1):
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.left_indent = Inches(0.26)
        p.paragraph_format.first_line_indent = Inches(-0.26)
        run = p.add_run(f"{idx}.  {item}")
        set_run_font(run)


def add_table(doc: Document, headers: list[str], rows: list[list[str]], widths: list[float], font_size=9.5):
    table = doc.add_table(rows=1, cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    set_table_borders(table)
    set_column_widths(table, widths)
    header = table.rows[0]
    set_repeat_table_header(header)
    for idx, text in enumerate(headers):
        cell = header.cells[idx]
        set_cell_shading(cell, NAVY)
        set_cell_margins(cell)
        cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_after = Pt(0)
        r = p.add_run(text)
        set_run_font(r, size=font_size, bold=True, color=WHITE)
    for row_idx, values in enumerate(rows):
        cells = table.add_row().cells
        if row_idx % 2:
            for cell in cells:
                set_cell_shading(cell, PALE_BLUE)
        for idx, value in enumerate(values):
            set_cell_margins(cells[idx])
            cells[idx].vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            p = cells[idx].paragraphs[0]
            p.paragraph_format.space_after = Pt(0)
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if idx == 0 else WD_ALIGN_PARAGRAPH.LEFT
            r = p.add_run(value)
            set_run_font(r, size=font_size)
    doc.add_paragraph().paragraph_format.space_after = Pt(0)
    return table


def add_code_block(doc: Document, code: str, font_size=8.5) -> None:
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    set_row_cant_split(table.rows[0])
    set_table_borders(table, color="C8D2DC", size="4")
    cell = table.cell(0, 0)
    set_cell_shading(cell, "F5F7F9")
    set_cell_margins(cell, top=150, start=170, bottom=150, end=170)
    p = cell.paragraphs[0]
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.line_spacing = 1.0
    r = p.add_run(code)
    set_run_font(r, name="DejaVu Sans Mono", size=font_size, color="182433")
    doc.add_paragraph().paragraph_format.space_after = Pt(0)


def add_figure(doc: Document, filename: str, caption: str, width=6.65, alt=None) -> None:
    path = ASSETS / filename
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.keep_with_next = True
    run = p.add_run()
    shape = run.add_picture(str(path), width=Inches(width))
    shape._inline.docPr.set("descr", alt or caption)
    cp = doc.add_paragraph()
    cp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cp.paragraph_format.space_after = Pt(7)
    cp.paragraph_format.keep_with_next = False
    r = cp.add_run(caption)
    set_run_font(r, size=9, italic=True, color=MID)


def heading(doc: Document, text: str, level=1) -> None:
    p = doc.add_paragraph(style=f"Heading {level}")
    if getattr(doc, "_pending_page_break", False):
        p.paragraph_format.page_break_before = True
        doc._pending_page_break = False
    p.paragraph_format.keep_with_next = True
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(6)
    r = p.add_run(text)
    set_run_font(r, size=18 if level == 1 else 13, bold=True, color=BLACK)


def page_break(doc: Document) -> None:
    doc._pending_page_break = True


def make_database_snapshot() -> None:
    source = json.loads((ROOT / "submission" / "database.json").read_text(encoding="utf-8"))
    width, height = 1500, 860
    img = Image.new("RGB", (width, height), "#111417")
    draw = ImageDraw.Draw(img)
    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    bold_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    regular = ImageFont.truetype(font_path, 28)
    small = ImageFont.truetype(font_path, 23)
    bold = ImageFont.truetype(bold_path, 30)
    title = ImageFont.truetype(bold_path, 36)
    draw.rounded_rectangle((28, 25, width - 28, height - 25), radius=26, fill="#171B20", outline="#38434F", width=2)
    draw.text((74, 62), "Realtime Database", font=title, fill="#FFFFFF")
    draw.text((74, 116), "midtern-users-2026-htt1325-default-rtdb  /  data", font=small, fill="#AEB9C5")
    draw.line((74, 166, width - 74, 166), fill="#38434F", width=2)
    y = 206
    draw.text((80, y), "▾ users", font=bold, fill="#F4C95D")
    y += 52
    for node, record in source["users"].items():
        draw.text((130, y), f"▾ {node}", font=regular, fill="#7CC7FF")
        y += 42
        for field in ("email", "matkhau", "hoten", "hinhanh"):
            value = record[field]
            if field == "matkhau":
                value = "••••••••••"
            if field == "hinhanh" and not value:
                value = '""'
            draw.text((185, y), field, font=small, fill="#69D8C8")
            draw.text((390, y), f":  {value}", font=small, fill="#E8EDF2")
            y += 36
        y += 22
    draw.text((80, height - 88), "Cấu trúc hợp lệ gồm đúng 4 trường trong mỗi hồ sơ", font=small, fill="#AEB9C5")
    img.save(ASSETS / "07-firebase-database.png")


def configure_document(doc: Document) -> None:
    section = doc.sections[0]
    section.page_width = Inches(8.5)
    section.page_height = Inches(11)
    section.top_margin = Inches(0.7)
    section.bottom_margin = Inches(0.68)
    section.left_margin = Inches(0.78)
    section.right_margin = Inches(0.78)
    section.header_distance = Inches(0.28)
    section.footer_distance = Inches(0.28)

    styles = doc.styles
    normal = styles["Normal"]
    normal.font.name = "Aptos"
    normal.font.size = Pt(11)
    normal.font.color.rgb = RGBColor.from_string(BLACK)
    normal._element.rPr.rFonts.set(qn("w:ascii"), "Aptos")
    normal._element.rPr.rFonts.set(qn("w:hAnsi"), "Aptos")
    normal._element.rPr.rFonts.set(qn("w:eastAsia"), "Aptos")
    normal.paragraph_format.space_after = Pt(6)
    normal.paragraph_format.line_spacing = 1.12

    for style_name, size in (("Title", 28), ("Heading 1", 18), ("Heading 2", 13)):
        style = styles[style_name]
        style.font.name = "Aptos Display" if style_name != "Normal" else "Aptos"
        style.font.size = Pt(size)
        style.font.color.rgb = RGBColor.from_string(BLACK)
        style.font.bold = True
        style._element.rPr.rFonts.set(qn("w:ascii"), "Aptos Display")
        style._element.rPr.rFonts.set(qn("w:hAnsi"), "Aptos Display")
        style._element.rPr.rFonts.set(qn("w:eastAsia"), "Aptos Display")
        p_pr = style._element.get_or_add_pPr()
        p_bdr = p_pr.find(qn("w:pBdr"))
        if p_bdr is not None:
            p_pr.remove(p_bdr)

    header = section.header
    hp = header.paragraphs[0]
    hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    hr = hp.add_run("LẬP TRÌNH ĐA NỀN TẢNG  ·  USER REGISTRY")
    set_run_font(hr, size=8, bold=True, color=MID)
    footer = section.footer
    fp = footer.paragraphs[0]
    fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    add_page_number(fp)
    section.different_first_page_header_footer = True
    section.first_page_header.paragraphs[0].clear()
    section.first_page_footer.paragraphs[0].clear()


def build() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    make_database_snapshot()
    doc = Document()
    configure_document(doc)

    # Cover
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(28)
    r = p.add_run("LẬP TRÌNH ĐA NỀN TẢNG")
    set_run_font(r, size=12, bold=True, color=MID)

    p = doc.add_paragraph(style="Title")
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(54)
    p.paragraph_format.space_after = Pt(12)
    r = p.add_run("Báo cáo xây dựng ứng dụng quản lý người dùng")
    set_run_font(r, name="Aptos Display", size=28, bold=True, color=BLACK)
    direct_borders = p._p.get_or_add_pPr().find(qn("w:pBdr"))
    if direct_borders is not None:
        p._p.get_or_add_pPr().remove(direct_borders)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(58)
    r = p.add_run("Flutter Web và Android với Firebase")
    set_run_font(r, size=15, color=MID)

    mark = doc.add_table(rows=1, cols=1)
    mark.alignment = WD_TABLE_ALIGNMENT.CENTER
    mark.autofit = False
    mark.cell(0, 0).width = Inches(2.1)
    set_cell_shading(mark.cell(0, 0), NAVY)
    set_cell_margins(mark.cell(0, 0), top=230, start=250, bottom=230, end=250)
    set_table_borders(mark, color=NAVY)
    mp = mark.cell(0, 0).paragraphs[0]
    mp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    mr = mp.add_run("U/\nUSER REGISTRY")
    set_run_font(mr, size=14, bold=True, color=WHITE)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(64)
    p.paragraph_format.space_after = Pt(5)
    r = p.add_run("Sinh viên thực hiện")
    set_run_font(r, size=10, color=MID)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("Huỳnh Tuấn Tú")
    set_run_font(r, size=13, bold=True)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("Ngày 10 tháng 11 năm 2026")
    set_run_font(r, size=10.5, color=MID)

    page_break(doc)

    heading(doc, "Tóm tắt kết quả", 1)
    add_body(doc, "User Registry là ứng dụng quản lý người dùng xây dựng bằng Flutter cho Web và Android. Ứng dụng dùng Firebase Authentication để đăng nhập, Realtime Database để đồng bộ dữ liệu và hỗ trợ đầy đủ thao tác thêm, hiển thị, sửa, xóa. Mỗi hồ sơ chỉ gồm bốn trường email, matkhau, hoten và hinhanh.")

    heading(doc, "Liên kết nộp bài", 2)
    links = [
        ("Web demo", "https://midtern-users-2026-htt1325.web.app/"),
        ("GitHub công khai", "https://github.com/htt1325abc/MidTernProject-Nov2026"),
        ("Video demo", "https://github.com/htt1325abc/MidTernProject-Nov2026/releases/latest/download/user-registry-demo.mp4"),
        ("Android APK", "https://github.com/htt1325abc/MidTernProject-Nov2026/releases/latest/download/user-registry.apk"),
    ]
    for label, url in links:
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(4)
        r = p.add_run(f"{label}: ")
        set_run_font(r, bold=True)
        add_hyperlink(p, url, url)
    add_body(doc, "Tài khoản quản trị demo: admin@userhub.local", bold_lead="Tài khoản quản trị demo:")
    add_body(doc, "Mật khẩu demo: Admin@123", bold_lead="Mật khẩu demo:")

    heading(doc, "Mục lục", 2)
    add_numbered(doc, [
        "Đối chiếu yêu cầu đề bài",
        "Công nghệ và kiến trúc hệ thống",
        "Thiết kế cơ sở dữ liệu",
        "Cài đặt và triển khai",
        "Minh chứng chức năng",
        "Kiểm thử và kết quả build",
        "Kết luận và tệp nộp",
    ])

    page_break(doc)
    heading(doc, "1 Đối chiếu yêu cầu đề bài", 1)
    add_body(doc, "Ứng dụng được xây dựng bằng Flutter, dùng Firebase Realtime Database, chạy trên Web và Android, đồng thời giới hạn dữ liệu ở đúng bốn trường quy định.")
    add_table(doc, ["Tiêu chí", "Cách đáp ứng", "Minh chứng"], [
        ["CSDL và Web 8,0 điểm", "Realtime Database; thêm và hiển thị đúng bốn trường; Web đã triển khai.", "Rules, cấu hình Firebase và Hosting"],
        ["Đăng nhập và CRUD 1,5 điểm", "Đăng nhập quản trị; sửa, xóa có xác nhận; tìm kiếm, sắp xếp và ẩn hiện mật khẩu.", "Màn hình đăng nhập và dashboard"],
        ["Ảnh và di động 0,5 điểm", "Chọn và nén ảnh; bố cục chuyển từ bảng sang thẻ trên màn hình hẹp.", "Ảnh form và giao diện di động"],
        ["Đúng bốn trường", "Model chỉ ghi email, matkhau, hoten, hinhanh; Rules từ chối trường khác.", "user_record.dart và database.rules.json"],
        ["Báo cáo và CSDL", "Có hướng dẫn, ảnh minh họa và tệp database.json.", "Thư mục submission"],
    ], [1.55, 3.0, 1.8], font_size=8.8)

    heading(doc, "Phạm vi chức năng", 2)
    add_bullets(doc, [
        "Đăng nhập và đăng xuất tài khoản quản trị.",
        "Theo dõi danh sách người dùng theo thời gian thực.",
        "Thêm, sửa và xóa hồ sơ với kiểm tra dữ liệu đầu vào.",
        "Chọn ảnh trên Web hoặc Android, nén ảnh trước khi lưu.",
        "Tìm kiếm theo họ tên hoặc email; sắp xếp dữ liệu; ẩn hoặc hiện mật khẩu.",
        "Hiển thị bảng trên màn hình rộng và thẻ hồ sơ trên màn hình di động.",
    ])

    heading(doc, "Ràng buộc dữ liệu", 2)
    add_body(doc, "Firebase node key chỉ dùng để xác định bản ghi khi sửa hoặc xóa, không được lưu thành trường dữ liệu. Tài khoản quản trị do Firebase Authentication quản lý riêng.")

    page_break(doc)
    heading(doc, "2 Công nghệ và kiến trúc hệ thống", 1)
    add_table(doc, ["Thành phần", "Công nghệ", "Vai trò"], [
        ["Ứng dụng", "Flutter 3.47.6 và Dart", "Một codebase chạy trên Web và Android"],
        ["Xác thực", "firebase_auth 7.0.1", "Đăng nhập quản trị bằng Email và Password"],
        ["Dữ liệu", "firebase_database 13.0.1", "CRUD và stream dữ liệu thời gian thực"],
        ["Khởi tạo", "firebase_core 5.1.0", "Kết nối project Firebase theo từng nền tảng"],
        ["Hình ảnh", "image_picker 1.2.4 và image 4.12.0", "Chọn, thu nhỏ và mã hóa ảnh"],
        ["Triển khai", "Firebase Hosting và GitHub Releases", "Phát hành Web và APK công khai"],
    ], [1.2, 2.25, 2.9], font_size=9)

    heading(doc, "Luồng xử lý", 2)
    flow = doc.add_table(rows=1, cols=5)
    flow.alignment = WD_TABLE_ALIGNMENT.CENTER
    flow.autofit = False
    labels = ["Màn hình Flutter", "Xác thực", "Repository", "Realtime Database", "Web hoặc Android"]
    colors = [PALE_BLUE, PALE, PALE_BLUE, PALE, PALE_BLUE]
    for idx, label in enumerate(labels):
        cell = flow.cell(0, idx)
        set_cell_shading(cell, colors[idx])
        set_cell_margins(cell, top=190, start=80, bottom=190, end=80)
        cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(label)
        set_run_font(r, size=8.5, bold=True)
    set_table_borders(flow)
    set_column_widths(flow, [1.22, 1.0, 1.05, 1.45, 1.2])
    doc.add_paragraph()
    add_body(doc, "AuthGate theo dõi trạng thái đăng nhập. Sau khi xác thực, UserRepository đọc node users bằng stream onValue. Các thao tác CRUD ghi trực tiếp vào Realtime Database và giao diện tự cập nhật khi dữ liệu thay đổi.")

    heading(doc, "Tổ chức mã nguồn", 2)
    add_code_block(doc, "lib/\n  app/                      Khởi tạo Firebase và điều hướng\n  core/                     Theme, validator, xử lý ảnh\n  features/auth/            Dịch vụ và màn hình đăng nhập\n  features/users/domain/    Model UserRecord\n  features/users/data/      UserRepository\n  features/users/presentation/ Dashboard, form, avatar\n  firebase_options.dart     Cấu hình Firebase Web và Android")

    page_break(doc)
    heading(doc, "3 Thiết kế cơ sở dữ liệu", 1)
    add_body(doc, "Dữ liệu nằm tại node /users. Mỗi hồ sơ có một key do Firebase tạo và chỉ chứa bốn trường sau.")
    add_table(doc, ["Trường", "Kiểu", "Ý nghĩa", "Kiểm tra"], [
        ["email", "String", "Email người dùng", "Định dạng email, không trùng"],
        ["matkhau", "String", "Mật khẩu theo yêu cầu đề", "Tối thiểu 6 ký tự"],
        ["hoten", "String", "Họ và tên", "Tối thiểu 2 ký tự"],
        ["hinhanh", "String", "Data URI ảnh đại diện", "Chuỗi, có thể rỗng trong tệp mẫu"],
    ], [1.05, 0.85, 2.0, 2.45], font_size=9.2)

    heading(doc, "Dữ liệu JSON mẫu", 2)
    add_code_block(doc, '{\n  "users": {\n    "sample-nguyen-thi-lan": {\n      "email": "lan.nguyen@example.com",\n      "matkhau": "Lan@12345",\n      "hoten": "Nguyễn Thị Lan",\n      "hinhanh": ""\n    }\n  }\n}', font_size=8.2)

    add_figure(doc, "07-firebase-database.png", "Hình 1  Ảnh dữ liệu xuất từ cấu trúc Firebase Realtime Database", width=4.8)

    page_break(doc)
    heading(doc, "Quy tắc bảo vệ dữ liệu", 2)
    add_body(doc, "Database Rules chỉ cho phép tài khoản đã đăng nhập đọc hoặc ghi, đồng thời kiểm tra đủ bốn trường và từ chối trường ngoài quy định.")
    add_code_block(doc, '"users": {\n  ".read": "auth != null",\n  ".write": "auth != null",\n  ".indexOn": ["email"],\n  "$userId": {\n    ".validate": "newData.hasChildren([\'email\', \'matkhau\', \'hoten\', \'hinhanh\'])",\n    "$field": {\n      ".validate": "($field == \'email\' ...) || ($field == \'matkhau\' ...) ||\n                    ($field == \'hoten\' ...) || ($field == \'hinhanh\' ...)"\n    }\n  }\n}')
    add_body(doc, "Trường matkhau được giữ theo yêu cầu đề bài. Trong hệ thống thực tế, mật khẩu không nên lưu dưới dạng văn bản rõ; tài khoản quản trị của ứng dụng này vẫn do Firebase Authentication quản lý.")

    heading(doc, "4 Cài đặt và triển khai", 1)
    heading(doc, "Chuẩn bị môi trường", 2)
    add_numbered(doc, [
        "Cài Flutter SDK 3.47 trở lên, Android SDK và Chrome.",
        "Clone repository công khai về máy.",
        "Khôi phục thư viện bằng flutter pub get.",
        "Chạy ứng dụng trên Chrome hoặc thiết bị Android.",
    ])
    add_code_block(doc, "git clone https://github.com/htt1325abc/MidTernProject-Nov2026.git\ncd MidTernProject-Nov2026\nflutter pub get\nflutter run -d chrome")

    heading(doc, "Cấu hình Firebase", 2)
    add_numbered(doc, [
        "Tạo project Firebase midtern-users-2026-htt1325.",
        "Khai báo ứng dụng Web và Android; thêm cấu hình vào firebase_options.dart và google-services.json.",
        "Bật Authentication với phương thức Email và Password.",
        "Tạo Realtime Database tại khu vực asia-southeast1 và deploy database.rules.json.",
        "Tạo tài khoản quản trị demo và nhập dữ liệu mẫu.",
    ])
    add_code_block(doc, "firebase login\nfirebase use midtern-users-2026-htt1325\nfirebase deploy --only database,hosting")

    heading(doc, "5 Minh chứng chức năng", 1)
    heading(doc, "Đăng nhập quản trị", 2)
    add_body(doc, "Firebase Authentication xác thực email và mật khẩu trước khi mở trang quản trị. Lỗi đăng nhập được hiển thị bằng tiếng Việt.")
    add_figure(doc, "01-dang-nhap.png", "Hình 2  Màn hình đăng nhập trên bản Web đã deploy", width=6.45)

    page_break(doc)
    heading(doc, "Danh sách và thao tác quản trị", 2)
    add_body(doc, "Danh sách cập nhật theo thời gian thực và hỗ trợ tìm kiếm, sắp xếp, ẩn hiện mật khẩu, thêm, sửa và xóa hồ sơ.")
    add_figure(doc, "02-danh-sach.png", "Hình 3  Danh sách người dùng đồng bộ từ Firebase", width=5.9)

    heading(doc, "Thêm hồ sơ và chọn ảnh", 2)
    add_body(doc, "Người quản trị nhập họ tên, email, mật khẩu và chọn ảnh từ thiết bị. Ảnh được sửa chiều, thu nhỏ, nén JPEG, hiển thị xem trước và mã hóa thành data URI trước khi lưu vào trường hinhanh.")
    add_figure(doc, "08-chon-anh-nguoi-dung.png", "Hình 4  Ảnh đại diện hiển thị xem trước trong form thêm người dùng", width=4.6)

    page_break(doc)
    heading(doc, "Sửa hồ sơ", 2)
    add_body(doc, "Form sửa tải dữ liệu theo Firebase node key, kiểm tra email trùng và ghi lại đúng bốn trường của hồ sơ.")
    add_figure(doc, "04-sua-nguoi-dung.png", "Hình 5  Form cập nhật hồ sơ", width=4.9)

    heading(doc, "Xóa hồ sơ", 2)
    add_body(doc, "Ứng dụng yêu cầu xác nhận trước khi xóa node tương ứng khỏi Realtime Database.")
    add_figure(doc, "05-xac-nhan-xoa.png", "Hình 6  Xác nhận trước khi xóa dữ liệu", width=4.9)

    page_break(doc)
    heading(doc, "Giao diện di động", 2)
    add_body(doc, "Trên màn hình hẹp, danh sách dạng bảng chuyển thành các thẻ hồ sơ. APK Android dùng cùng bố cục thích ứng và lớp dữ liệu với bản Web.")
    add_figure(doc, "06-giao-dien-di-dong.png", "Hình 7  Danh sách dạng thẻ trên khung nhìn di động", width=3.05)

    page_break(doc)
    heading(doc, "6 Kiểm thử và kết quả build", 1)
    heading(doc, "Kết quả kiểm tra mã nguồn", 2)
    add_table(doc, ["Lệnh", "Kết quả", "Phạm vi"], [
        ["flutter analyze", "Không có lỗi", "Lint và phân tích tĩnh toàn project"],
        ["flutter test", "5 kiểm thử đạt", "Validator, model và widget cơ bản"],
        ["flutter build web --release", "Thành công", "Bản Web tối ưu để deploy"],
        ["flutter build apk --release", "Thành công", "APK Android phiên bản 1.0.0"],
        ["firebase deploy --only database,hosting", "Thành công", "Rules và Hosting công khai"],
    ], [2.25, 1.25, 2.85], font_size=9)

    heading(doc, "Kiểm thử dữ liệu", 2)
    add_bullets(doc, [
        "Model đọc dữ liệu Firebase và chỉ ghi bốn trường được phép.",
        "Validator từ chối họ tên quá ngắn, email sai định dạng và mật khẩu dưới sáu ký tự.",
        "Firebase Rules yêu cầu auth != null và kiểm tra kiểu dữ liệu từng trường.",
        "Repository đồng bộ dữ liệu, sắp xếp theo họ tên và báo lỗi khi mất quyền hoặc mất mạng.",
    ])

    heading(doc, "Thông tin bản phát hành", 2)
    add_table(doc, ["Thuộc tính", "Giá trị"], [
        ["Phiên bản", "1.0.0+1"],
        ["Gói Android", "user-registry.apk"],
        ["Dung lượng", "Khoảng 55,0 MB"],
        ["SHA256", "aea2f37cfff06cf4eedb1bdd2a179f58f6a89fa7d127528cd6b6dbd31351f9f5"],
        ["Hosting", "midtern-users-2026-htt1325.web.app"],
        ["Khu vực Firebase", "asia-southeast1"],
    ], [1.55, 4.8], font_size=9)

    page_break(doc)
    heading(doc, "7 Kết luận và tệp nộp", 1)
    add_body(doc, "Ứng dụng đáp ứng yêu cầu về nền tảng, cơ sở dữ liệu, đăng nhập, CRUD, hình ảnh và giao diện di động. Model và Firebase Rules cùng giới hạn mỗi hồ sơ ở đúng bốn trường quy định.")

    heading(doc, "Danh mục nộp bài", 2)
    add_table(doc, ["Hạng mục", "Tệp hoặc liên kết"], [
        ["Mã nguồn", "GitHub công khai MidTernProject-Nov2026"],
        ["Cơ sở dữ liệu", "submission/database.json"],
        ["Báo cáo", "submission/Bao_cao_User_Registry.docx"],
        ["Video demo", "submission/user-registry-demo.mp4 và GitHub Release"],
        ["Ứng dụng Android", "user-registry.apk trên GitHub Release"],
    ], [2.0, 4.35], font_size=9.5)

    doc.core_properties.title = "Báo cáo xây dựng ứng dụng quản lý người dùng"
    doc.core_properties.subject = "Lập trình đa nền tảng với Flutter và Firebase"
    doc.core_properties.author = "Huỳnh Tuấn Tú"
    doc.core_properties.keywords = "Flutter, Firebase, CRUD, Android, Web, Realtime Database"
    doc.core_properties.comments = "Báo cáo giữa kỳ tháng 11 năm 2026"
    doc.save(OUTPUT)
    print(OUTPUT)


if __name__ == "__main__":
    build()
