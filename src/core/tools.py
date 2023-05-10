import re
import tempfile
import typing
from datetime import datetime
from xml.etree import ElementTree
from PyQt5.QtGui import QColor, QFont

def getTempFileName(**kwargs):
    file = tempfile.NamedTemporaryFile(**kwargs)
    file.close()
    return file.name

def strftime(frmt: str = '%Y-%m-%d_%H-%M-%S'):
    return datetime.now().strftime(frmt)


def colorComplement(color: QColor) -> QColor:
    r = 255 - color.red()
    g = 255 - color.green()
    b = 255 - color.blue()
    return QColor(r, g, b)


def svgColorToTuple(svgColor: str, txt: str) -> typing.Union[tuple, str]:
    result = re.search('rgb\\([^,0-9]*([0-9]+)[^,0-9]*,[^,0-9]*([0-9]+)[^,0-9]*,[^,0-9]*([0-9]+)[^,0-9]*\\)', svgColor)
    if result is None:
        return '%s is not a valid rgb %s color' % (svgColor, txt)
    else:
        return int(result.group(1)), int(result.group(2)), int(result.group(3))


def checkFontName(font_name: str) -> str:
    try:
        font = QFont(font_name)
    except:
        return '"%s" is not a recognized font name' % font_name
    return ''


def checkFontSize(font_size: int, minimum: int = 1, maximum: int = 99) -> str:
    if font_size < minimum or font_size > maximum:
        return '%d font size is not between %d and %d' % (font_size, minimum, maximum)
    return ''


def checkRGB(rgb: tuple, txt: str) -> str:
    try:
        color = QColor(*rgb)
    except:
        return '"rgb(%s)" is not a recognized %s color' % (str(rgb), txt)
    return ''


def getTags(text: str, tag: str = 'AsciiArt') -> typing.Union[dict, str]:
    pattern = '(?:<{0}.*?>)(.*?)(?:<\\/{0}>)'.format(tag)
    results = []
    for result in re.finditer(pattern, text):
        results.append(result)

    if len(results) > 0:
        xml = ''.join([result.group(0) for result in results])
        root = 'root'
        i = 0
        while xml.count('<' + root + '' if i == 0 else str(i)) > 0:
            i += 1
        root += '' if i == 0 else str(i)
        xml = '<{0}>{1}</{0}>'.format(root, xml)
        try:
            tree = ElementTree.fromstring(xml)
            elems = list(tree.iter())[1:]
            i = 0
            dic = {}
            for elem in elems:
                key = results[i].group(0)
                if key not in dic:
                    dic[key] = elem.attrib
                    dic[key]['text'] = elem.text
                i += 1
            return dic
        except Exception as e:
            return 'Cannot get the <%s> tags; more info: %s' % (tag, str(e))
    else:
        return 'No valid <%s> tag could be found' % tag
