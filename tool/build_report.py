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
    add_body(doc, "Ứng dụng User Registry đã hoàn thành phần quản trị người dùng trên Web và Android. Hệ thống đăng nhập bằng Firebase Authentication, đồng bộ dữ liệu theo thời gian thực và thực hiện đủ thao tác thêm, hiển thị, sửa, xóa. Mỗi hồ sơ trong Realtime Database chỉ có bốn trường email, matkhau, hoten và hinhanh theo đúng yêu cầu đề bài.")

    heading(doc, "Liên kết bàn giao", 2)
    links = [
        ("Web demo", "https://midtern-users-2026-htt1325.web.app/"),
        ("GitHub công khai", "https://github.com/htt1325abc/MidTernProject-Nov2026"),
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

    heading(doc, "Nội dung báo cáo", 2)
    add_numbered(doc, [
        "Đối chiếu yêu cầu đề bài",
        "Công nghệ và kiến trúc hệ thống",
        "Thiết kế cơ sở dữ liệu",
        "Các bước cài đặt và thực hiện",
        "Minh chứng chức năng",
        "Kiểm thử, build và triển khai",
        "Kết luận và danh mục nộp bài",
    ])

    page_break(doc)
    heading(doc, "1 Đối chiếu yêu cầu đề bài", 1)
    add_body(doc, "Đề yêu cầu xây dựng ứng dụng quản trị người dùng bằng Flutter, React Native hoặc .NET MAUI; dùng Firebase hoặc MongoDB; chạy trên Web và hỗ trợ giao diện di động. Dữ liệu chỉ được gồm bốn trường quy định. Bảng sau đối chiếu trực tiếp từng tiêu chí với phần đã triển khai.")
    add_table(doc, ["Tiêu chí", "Cách đáp ứng", "Minh chứng"], [
        ["CSDL và Web 8,0 điểm", "Firebase Realtime Database; thêm và hiển thị email, matkhau, hoten, hinhanh; Web đã deploy.", "database.rules.json, firebase.json, link Hosting"],
        ["Đăng nhập, sửa, xóa, nâng cao 1,5 điểm", "Firebase Authentication; sửa/xóa có xác nhận; tìm kiếm, sắp xếp, ẩn hiện mật khẩu, kiểm tra email trùng.", "Màn hình đăng nhập và dashboard"],
        ["Ảnh và giao diện di động 0,5 điểm", "Chọn ảnh từ thiết bị, nén ảnh, lưu dạng data URI; layout chuyển từ bảng sang thẻ trên màn hình hẹp.", "image_picker, image, ảnh giao diện di động"],
        ["Đúng bốn trường", "Model chỉ serialize email, matkhau, hoten, hinhanh. Firebase rules từ chối trường khác.", "user_record.dart và database.rules.json"],
        ["Báo cáo và tệp CSDL", "Báo cáo có bước thực hiện, lệnh cài đặt, ảnh minh họa; kèm database.json.", "submission/"],
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
    add_body(doc, "Firebase node key được dùng nội bộ để xác định bản ghi khi sửa hoặc xóa. Key không được serialize thành một trường dữ liệu. Phần đăng nhập quản trị nằm trong Firebase Authentication, tách khỏi dữ liệu hồ sơ người dùng.")

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
    add_body(doc, "AuthGate lắng nghe trạng thái đăng nhập. Sau khi xác thực thành công, UserRepository đọc node users bằng stream onValue. Các lệnh create, update và delete ghi trực tiếp vào Realtime Database; giao diện tự cập nhật khi dữ liệu thay đổi.")

    heading(doc, "Tổ chức mã nguồn", 2)
    add_code_block(doc, "lib/\n  app/                      Khởi tạo Firebase và điều hướng\n  core/                     Theme, validator, xử lý ảnh\n  features/auth/            Dịch vụ và màn hình đăng nhập\n  features/users/domain/    Model UserRecord\n  features/users/data/      UserRepository\n  features/users/presentation/ Dashboard, form, avatar\n  firebase_options.dart     Cấu hình Firebase Web và Android")

    page_break(doc)
    heading(doc, "3 Thiết kế cơ sở dữ liệu", 1)
    add_body(doc, "Dữ liệu được lưu tại node /users. Mỗi child là một hồ sơ có key do Firebase tạo. Giá trị của child chỉ gồm bốn trường bắt buộc sau.")
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
    add_body(doc, "Database Rules yêu cầu người dùng đã đăng nhập mới được đọc hoặc ghi. Quy tắc validate kiểm tra đủ bốn trường và chỉ chấp nhận tên trường nằm trong danh sách của đề bài.")
    add_code_block(doc, '"users": {\n  ".read": "auth != null",\n  ".write": "auth != null",\n  ".indexOn": ["email"],\n  "$userId": {\n    ".validate": "newData.hasChildren([\'email\', \'matkhau\', \'hoten\', \'hinhanh\'])",\n    "$field": {\n      ".validate": "($field == \'email\' ...) || ($field == \'matkhau\' ...) ||\n                    ($field == \'hoten\' ...) || ($field == \'hinhanh\' ...)"\n    }\n  }\n}')
    add_body(doc, "Lưu ý bảo mật: trường matkhau tồn tại vì đề bài bắt buộc. Tài khoản quản trị thật vẫn do Firebase Authentication quản lý. Trong hệ thống sản xuất, mật khẩu người dùng không nên lưu dưới dạng văn bản rõ trong cơ sở dữ liệu ứng dụng.")

    heading(doc, "4 Các bước cài đặt và thực hiện", 1)
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
    add_body(doc, "Màn hình yêu cầu email và mật khẩu. Firebase Authentication xác thực tài khoản trước khi mở dashboard. Khi đăng nhập thất bại, ứng dụng chuyển mã lỗi Firebase thành thông báo tiếng Việt.")
    add_figure(doc, "01-dang-nhap.png", "Hình 2  Màn hình đăng nhập trên bản Web đã deploy", width=6.45)

    page_break(doc)
    heading(doc, "Danh sách và thao tác quản trị", 2)
    add_body(doc, "Dashboard hiển thị dữ liệu theo thời gian thực. Thanh công cụ cho phép tìm kiếm, sắp xếp, ẩn hiện mật khẩu và mở form thêm người dùng. Mỗi dòng có nút sửa và xóa.")
    add_figure(doc, "02-danh-sach.png", "Hình 3  Dashboard với ba hồ sơ đang đồng bộ từ Firebase", width=6.45)

    page_break(doc)
    heading(doc, "Thêm hồ sơ và chọn ảnh", 2)
    add_body(doc, "Form thêm mới yêu cầu đủ họ tên, email và mật khẩu. Nút Chọn ảnh mở bộ chọn tệp trên Web hoặc thư viện ảnh trên Android. Ảnh được giảm kích thước và nén trước khi chuyển thành data URI để ghi vào trường hinhanh.")
    add_figure(doc, "03-them-nguoi-dung.png", "Hình 4  Form thêm người dùng và chức năng chọn ảnh", width=5.95)

    page_break(doc)
    heading(doc, "Sửa hồ sơ", 2)
    add_body(doc, "Khi người quản trị chọn biểu tượng sửa, form tải dữ liệu hiện tại theo Firebase node key. Lệnh lưu ghi lại đúng bốn trường của model. Repository loại trừ key hiện tại khi kiểm tra email trùng.")
    add_figure(doc, "04-sua-nguoi-dung.png", "Hình 5  Form cập nhật hồ sơ đã nạp dữ liệu hiện tại", width=6.35)

    page_break(doc)
    heading(doc, "Xóa hồ sơ", 2)
    add_body(doc, "Ứng dụng hiển thị tên người dùng và cảnh báo thao tác không thể hoàn tác. Chỉ khi người quản trị bấm Xóa hồ sơ, repository mới gọi remove trên node tương ứng.")
    add_figure(doc, "05-xac-nhan-xoa.png", "Hình 6  Hộp thoại xác nhận trước khi xóa dữ liệu", width=5.95)

    page_break(doc)
    heading(doc, "Giao diện di động", 2)
    add_body(doc, "Trên màn hình hẹp, sidebar và bảng được thay bằng thanh tiêu đề gọn và các thẻ hồ sơ. Nút thêm người dùng được đặt cố định ở cạnh dưới để thao tác thuận tiện. APK Android sử dụng cùng layout responsive và cùng lớp repository.")
    add_figure(doc, "06-giao-dien-di-dong.png", "Hình 7  Danh sách dạng thẻ trên khung nhìn di động", width=3.05)

    page_break(doc)
    heading(doc, "6 Kiểm thử build và triển khai", 1)
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
        "Model đọc map Firebase và chỉ serialize bốn trường được phép.",
        "Validator từ chối họ tên quá ngắn, email sai định dạng và mật khẩu dưới sáu ký tự.",
        "Firebase Rules yêu cầu auth != null và kiểm tra kiểu dữ liệu từng trường.",
        "Repository đọc stream, sắp xếp theo họ tên và trả thông báo dễ hiểu khi mất quyền hoặc mất mạng.",
    ])

    heading(doc, "Thông tin bản phát hành", 2)
    add_table(doc, ["Thuộc tính", "Giá trị"], [
        ["Phiên bản", "1.0.0+1"],
        ["Gói Android", "user-registry.apk"],
        ["Dung lượng", "Khoảng 55,0 MB"],
        ["SHA256", "aea2f37cfff06cf4eedb1bdd2a179f58f6a89fa7d127528cd6b6dbd31351f9f5"],
        ["Hosting", "midtern-users-2026-htt1325.web.app"],
        ["Firebase region", "asia-southeast1"],
    ], [1.55, 4.8], font_size=9)

    page_break(doc)
    heading(doc, "7 Kết luận và danh mục nộp bài", 1)
    add_body(doc, "User Registry đáp ứng các tiêu chí chức năng của đề: chạy trên Web, có bản Android, đăng nhập quản trị, CRUD người dùng, chọn và hiển thị ảnh, giao diện responsive và các chức năng tìm kiếm, sắp xếp, ẩn hiện mật khẩu. Cấu trúc dữ liệu được khóa ở đúng bốn trường bằng cả model và Firebase Rules.")

    heading(doc, "Danh mục tệp quan trọng", 2)
    add_table(doc, ["Tệp hoặc thư mục", "Nội dung"], [
        ["lib/", "Toàn bộ mã nguồn Flutter"],
        ["database.rules.json", "Quyền đọc ghi và validate dữ liệu"],
        ["firebase.json", "Cấu hình Hosting, Database và Emulator"],
        ["submission/database.json", "Tệp cơ sở dữ liệu JSON nộp kèm"],
        ["submission/Bao_cao_User_Registry.docx", "Báo cáo chi tiết"],
        ["test/", "Kiểm thử model, validator và widget"],
    ], [2.6, 3.75], font_size=9.2)

    heading(doc, "Checklist trước khi nộp", 2)
    add_bullets(doc, [
        "Mở link Web và đăng nhập bằng tài khoản demo.",
        "Kiểm tra thao tác thêm, sửa, xóa và chọn ảnh.",
        "Tải thử APK từ GitHub Release.",
        "Đính kèm file database.json và báo cáo Word.",
        "Quay video demo, tải lên dịch vụ chia sẻ và bổ sung link khi nộp bài.",
    ])

    heading(doc, "Kịch bản video demo đề xuất", 2)
    add_numbered(doc, [
        "Giới thiệu repository, link Web và cấu trúc bốn trường trong Firebase.",
        "Đăng nhập quản trị và giải thích dashboard.",
        "Thêm một hồ sơ có ảnh; tìm kiếm hồ sơ vừa tạo.",
        "Sửa thông tin, bật hiển thị mật khẩu và sắp xếp danh sách.",
        "Xóa hồ sơ thử nghiệm, sau đó mở giao diện di động hoặc APK Android.",
    ])

    doc.core_properties.title = "Báo cáo xây dựng ứng dụng quản lý người dùng"
    doc.core_properties.subject = "Lập trình đa nền tảng với Flutter và Firebase"
    doc.core_properties.author = "Huỳnh Tuấn Tú"
    doc.core_properties.keywords = "Flutter, Firebase, CRUD, Android, Web, Realtime Database"
    doc.core_properties.comments = "Báo cáo giữa kỳ tháng 11 năm 2026"
    doc.save(OUTPUT)
    print(OUTPUT)


if __name__ == "__main__":
    build()
