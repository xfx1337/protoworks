DEFAULT_BORDER_STYLESHEET = "background-color: rgb(32,33,36); margin:5px; border:1px solid rgb(255, 129, 2); "
SELECTED_BORDER_STYLESHEET = "background-color: rgb(111,113,118); margin:5px; border:1px solid rgb(255, 129, 2); "
DISABLE_BORDER = "border: none;"

SELECTED_STYLESHEET = "background-color: rgb(111,113,118)"
UNSELECTED_STYLESHEET = "background-color: rgb(32,33,36)"

GREEN_BACKGROUND_STYLESHEET = "background-color: rgb(0, 128, 0)"
YELLOW_BACKGROUND_STYLESHEET = "background-color: rgb(216, 235, 9)"

OVERALL_STYLESHEET = """
QSplitter::handle
{
    background-color: rgb(63, 64, 66);
}
QPushButton::border {
    margin: 15px;
}
"""

COLORS_TO_HTML_RGB = {
    "red": "rgb(210, 20, 4)",
    "yellow": "rgb(216, 235, 9)"
}

YELLOW_HIGHLIGHT = "QLabel {color: rgb(216, 235, 9); }"
BLACK_HIGHLIGHT = "QLabel {color: rgb(128,128,128)}"
GREEN_HIGHLIGHT = "QLabel {color: rgb(0, 128, 0)}"
RED_HIGHLIGHT = "QLabel {color: rgb(210, 20, 4)}"
CYAN_HIGHLIGHT = "QLabel {color: rgb(0, 255, 255)}"
PURPLE_HIGHLIGHT = "QLabel {color: rgb(204, 136, 153)}"
NO_HIGHLIGHT = "QLabel {color: rgb(255,255,255)}"
DEFAULT_BUTTON = "QPushButton {color: rgb(255, 129, 2)}"

TOOLTIP = """QToolTip {
    border: 2px rgb(32,33,36);
    padding: 5px;
    opacity: 200;
}""" # for some reason in dark theme, tooltips are broken..

def combine(l):
    sheet = l[0][:-1]
    for i in range(1, len(l)):
        sheet += (l[i][:-1])
    sheet += "}"
    return sheet

def adapt(l, fr, to):
    if fr != None:
        if fr != "" and fr in l:
            return l.replace(fr, to)
        else:
            return to + " {" + l + "}"
    else:
        return to + " {" + l + "}"