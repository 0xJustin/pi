"""Build the dark slide template from the figure palette and the geometry in layouts.py.
usage: python -m slidestyle.build_template   (from the skill directory) -> template/dark.pptx and template/dark.potx

The template is generated, not hand-edited: change a color in ../figures/figstyle/palette.py or a frame in
layouts.py and rebuild, and slides and figures stay in one visual language."""
import shutil, sys, zipfile
from pathlib import Path
from lxml import etree
from pptx import Presentation
from pptx.opc.constants import RELATIONSHIP_TYPE as RT
from pptx.util import Inches

SKILL = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SKILL.parent / "figures"))
from figstyle.palette import BG, INK, INK2, INK3, FAMILIES   # noqa: E402
from . import layouts as L                                    # noqa: E402

NS = {"a": "http://schemas.openxmlformats.org/drawingml/2006/main",
      "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
      "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships"}
XMLNS = " ".join(f'xmlns:{k}="{v}"' for k, v in NS.items())
BG2 = "#1C1C1C"
HEAD_FONT, BODY_FONT = "Source Sans 3 Semibold", "Source Sans 3"


def emu(inches):
    return int(round(inches * 914400))


def hx(c):
    return c.lstrip("#").upper()


def xfrm(box):
    x, y, w, h = box
    return f'<a:xfrm><a:off x="{emu(x)}" y="{emu(y)}"/><a:ext cx="{emu(w)}" cy="{emu(h)}"/></a:xfrm>'


def run_style(pt, color, font=None):
    face = f'<a:latin typeface="{font}"/>' if font else ""
    return f'<a:defRPr sz="{pt * 100}"><a:solidFill><a:schemeClr val="{color}"/></a:solidFill>{face}</a:defRPr>'


def placeholder(sid, name, ph, box, prompt, anchor="t", lst=""):
    """One placeholder shape. `ph` is the <p:ph> attributes; text insets are zero so text sits on the margin."""
    return f"""<p:sp><p:nvSpPr><p:cNvPr id="{sid}" name="{name}"/><p:cNvSpPr><a:spLocks noGrp="1"/></p:cNvSpPr>
      <p:nvPr><p:ph {ph}/></p:nvPr></p:nvSpPr><p:spPr>{xfrm(box)}</p:spPr>
      <p:txBody><a:bodyPr lIns="0" tIns="0" rIns="0" bIns="0" anchor="{anchor}"><a:noAutofit/></a:bodyPr>
      <a:lstStyle>{lst}</a:lstStyle><a:p><a:r><a:rPr lang="en-US"/><a:t>{prompt}</a:t></a:r></a:p></p:txBody></p:sp>"""


def slide_number(sid, idx):
    lst = f'<a:lvl1pPr algn="r">{run_style(L.NUMBER_PT, "tx2")}</a:lvl1pPr>'
    return f"""<p:sp><p:nvSpPr><p:cNvPr id="{sid}" name="Slide Number"/><p:cNvSpPr><a:spLocks noGrp="1"/></p:cNvSpPr>
      <p:nvPr><p:ph type="sldNum" sz="quarter" idx="{idx}"/></p:nvPr></p:nvSpPr><p:spPr>{xfrm(L.SLIDE_NUMBER)}</p:spPr>
      <p:txBody><a:bodyPr lIns="0" tIns="0" rIns="0" bIns="0" anchor="b"/><a:lstStyle>{lst}</a:lstStyle>
      <a:p><a:fld id="{{B6F15528-21DE-4FAA-801E-634DDDAF4B2B}}" type="slidenum"><a:rPr lang="en-US"/><a:t>‹#›</a:t></a:fld></a:p>
      </p:txBody></p:sp>"""


def figure_frame(sid, name, idx, box, layout, frame):
    w, h = L.figure_size(layout, frame)
    lst = f'<a:lvl1pPr marL="0" indent="0" algn="ctr"><a:buNone/>{run_style(14, "tx2")}</a:lvl1pPr>'
    return placeholder(sid, name, f'type="pic" idx="{idx}"', L.LAYOUTS[layout][frame],
                       f"Figure: fs.slide_figure({w}, {h})", anchor="ctr", lst=lst)


def body(sid, name, idx, box, prompt):
    return placeholder(sid, name, f'type="body" idx="{idx}"', box, prompt)


def layout_shapes(name):
    g = L.LAYOUTS[name]
    claim = lambda: placeholder(2, "Claim", 'type="title"', g["title"], "Claim, as one sentence")
    shapes = {
        "Title": lambda: [
            placeholder(2, "Title", 'type="ctrTitle"', g["title"], "Talk title", anchor="b",
                        lst=f'<a:lvl1pPr>{run_style(L.SECTION_PT, "tx1")}</a:lvl1pPr>'),
            placeholder(3, "Subtitle", 'type="subTitle" idx="1"', g["subtitle"], "Name · lab · date",
                        lst=f'<a:lvl1pPr marL="0" indent="0"><a:buNone/>{run_style(L.BODY_PT, "tx2")}</a:lvl1pPr>')],
        "Claim + figure": lambda: [claim(), figure_frame(3, "Figure", 13, g["figure"], name, "figure")],
        "Two figures": lambda: [claim(), figure_frame(3, "Left figure", 13, g["left"], name, "left"),
                                figure_frame(4, "Right figure", 14, g["right"], name, "right")],
        "Figure only": lambda: [figure_frame(3, "Figure", 13, g["figure"], name, "figure")],
        "Claim only": lambda: [claim()],
        "Section": lambda: [placeholder(2, "Section", 'type="title"', g["title"], "Section", anchor="b",
                                        lst=f'<a:lvl1pPr>{run_style(L.SECTION_PT, "tx1")}</a:lvl1pPr>')],
        "Recap / asks": lambda: [claim(), body(3, "Recap", 1, g["recap"], "Since last time"),
                                 body(4, "Asks", 2, g["asks"], "Asks")],
    }[name]()
    if name in L.NUMBERED:
        shapes.append(slide_number(9, 12))
    return shapes


LAYOUT_TYPES = {"Title": "title", "Claim + figure": "cust", "Two figures": "cust", "Figure only": "cust",
                "Claim only": "titleOnly", "Section": "secHead", "Recap / asks": "twoColTx"}


def write_layout(layout, name):
    root = layout._element
    for child in list(root):
        root.remove(child)
    root.set("type", LAYOUT_TYPES[name])
    root.set("preserve", "1")
    tree = f"""<p:cSld {XMLNS} name="{name}"><p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/>
      </p:nvGrpSpPr><p:grpSpPr/>{"".join(layout_shapes(name))}</p:spTree></p:cSld>"""
    root.append(etree.fromstring(tree))
    root.append(etree.fromstring(f'<p:clrMapOvr {XMLNS}><a:masterClrMapping/></p:clrMapOvr>'))


def text_styles():
    lvl = lambda n, mar, ind, bullet, pt, color, before: (
        f'<a:lvl{n}pPr marL="{mar}" indent="{ind}" algn="l"><a:spcBef><a:spcPts val="{before}"/></a:spcBef>{bullet}'
        f'{run_style(pt, color, "+mn-lt")}</a:lvl{n}pPr>')
    dash = '<a:buFont typeface="Arial"/><a:buChar char="–"/>'
    body = lvl(1, 0, 0, "<a:buNone/>", L.BODY_PT, "tx1", 1200) + "".join(
        lvl(n, 342900 * (n - 1), -228600, dash, L.SUB_PT, "tx2", 400) for n in range(2, 10))
    title = f'<a:lvl1pPr algn="l"><a:spcBef><a:spcPts val="0"/></a:spcBef><a:buNone/>{run_style(L.TITLE_PT, "tx1", "+mj-lt")}</a:lvl1pPr>'
    other = f'<a:lvl1pPr>{run_style(18, "tx1", "+mn-lt")}</a:lvl1pPr>'
    return (f'<p:txStyles {XMLNS}><p:titleStyle>{title}</p:titleStyle><p:bodyStyle>{body}</p:bodyStyle>'
            f'<p:otherStyle>{other}</p:otherStyle></p:txStyles>')


def write_master(master):
    root = master._element
    cmap = root.find("p:clrMap", NS)   # dark: the background is the theme's dark 1, text its light 1
    for k, v in dict(bg1="dk1", tx1="lt1", bg2="dk2", tx2="lt2").items():
        cmap.set(k, v)
    csld = root.find("p:cSld", NS)
    csld.replace(csld.find("p:bg", NS),
                 etree.fromstring(f'<p:bg {XMLNS}><p:bgPr><a:solidFill><a:schemeClr val="bg1"/></a:solidFill>'
                                  '<a:effectLst/></p:bgPr></p:bg>'))
    tree = csld.find("p:spTree", NS)
    for sp in tree.findall("p:sp", NS):
        tree.remove(sp)
    g = L.LAYOUTS["Claim + figure"]
    for xml in [placeholder(2, "Title", 'type="title"', g["title"], "Claim, as one sentence"),
                body(3, "Text", 1, (L.M, L.FIG_TOP, L.W - 2 * L.M, L.H - L.FIG_TOP - 0.6), "Text"),
                slide_number(4, 4)]:
        tree.append(etree.fromstring(xml.replace("<p:sp>", f"<p:sp {XMLNS}>", 1)))
    root.replace(root.find("p:txStyles", NS), etree.fromstring(text_styles()))


def write_theme(master):
    part = master.part.part_related_by(RT.THEME)
    root = etree.fromstring(part.blob)
    root.set("name", "Dark")
    scheme = root.find(".//a:clrScheme", NS)
    scheme.set("name", "Dark")
    hues = [h for h, _ in FAMILIES.values()]
    colors = dict(dk1=BG, lt1=INK, dk2=BG2, lt2=INK2, **{f"accent{k + 1}": h for k, h in enumerate(hues)},
                  accent6=INK3, hlink=hues[0], folHlink=INK2)
    for child in list(scheme):
        scheme.remove(child)
    for k, v in colors.items():
        scheme.append(etree.fromstring(f'<a:{k} {XMLNS}><a:srgbClr val="{hx(v)}"/></a:{k}>'))
    fonts = root.find(".//a:fontScheme", NS)
    fonts.set("name", "Source Sans 3")
    fonts.find("a:majorFont/a:latin", NS).set("typeface", HEAD_FONT)
    fonts.find("a:minorFont/a:latin", NS).set("typeface", BODY_FONT)
    part._blob = etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True)


def as_template(pptx, potx):
    """Same package, with the main part typed as a template so PowerPoint opens it as a new untitled deck."""
    pres = "application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml"
    tmpl = "application/vnd.openxmlformats-officedocument.presentationml.template.main+xml"
    with zipfile.ZipFile(pptx) as src, zipfile.ZipFile(potx, "w", zipfile.ZIP_DEFLATED) as dst:
        for item in src.infolist():
            data = src.read(item.filename)
            if item.filename == "[Content_Types].xml":
                data = data.replace(pres.encode(), tmpl.encode())
            dst.writestr(item, data)


def build(out_dir=SKILL / "template"):
    prs = Presentation()
    prs.slide_width, prs.slide_height = Inches(L.W), Inches(L.H)
    master = prs.slide_master
    write_theme(master)
    write_master(master)
    names = list(L.LAYOUTS)
    layouts = list(prs.slide_layouts)
    for layout in layouts[len(names):]:
        prs.slide_layouts.remove(layout)
    for layout, name in zip(layouts, names):
        write_layout(layout, name)
    cp = prs.core_properties
    cp.title, cp.author, cp.last_modified_by, cp.revision = "Dark slides", "", "", 1
    out_dir.mkdir(exist_ok=True)
    pptx = out_dir / "dark.pptx"
    prs.save(pptx)
    as_template(pptx, out_dir / "dark.potx")
    print(pptx, out_dir / "dark.potx")


if __name__ == "__main__":
    build()
