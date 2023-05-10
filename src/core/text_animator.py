import cairo
import os
import math
from xml.dom.minidom import parse, Document, Element
from . import tools
import typing


class TextAnimator:
    def __init__(self, file_name: str = '', **kwargs):
        self.kwargs_input: dict = kwargs
        self.kwargs_output: typing.Union[dict, str] = ''
        self.doc: typing.Union[Document, str] = ''
        self.doc_main: typing.Union[Document, None] = None
        self.file_name: str = file_name
        self.from_file: bool = bool(file_name)
        if not self.from_file:
            self.file_name = tools.getTempFileName(prefix='ba-TextAnimator_', suffix='.svg')
        if not self.from_file:
            self.kwargs_output = self.text_to_svg(file_name=self.file_name, **self.kwargs_input)#, by_char=False)
            if isinstance(self.kwargs_output, dict):
                self.doc = self.animate_text(file_name=self.file_name, **self.kwargs_output)#, dur='1s')
        else:
            self.load_file(self.file_name)
        if isinstance(self.doc, Document):
            self.doc_main = parse(self.file_name)

    def load_file(self, file_name: str):
        if os.path.exists(file_name):
            try:
                self.doc = parse(file_name)
                elems: list[Element] = self.doc.getElementsByTagName('desc')
                elem: typing.Union[Element, None] = None
                for each in elems:
                    if each.getAttribute('id') == 'desc_ba-TA':
                        elem = each
                        break
                if elem is None:
                    raise 'Could not find an XML <desc> tag with id=desc_ba-TA'
            except Exception as e:
                self.doc = 'Cannot load the file at %s; more info: %s' % (str(file_name), str(e))
                return
            try:
                self.kwargs_output = {'text': elem.childNodes[0].data[1:-1],
                                      'background': elem.getAttribute('background'),
                                      'font_name': elem.getAttribute('font_name'),
                                      'font_size': int(elem.getAttribute('font_size')),
                                      'font_color': elem.getAttribute('font_color'),
                                      'width': int(elem.getAttribute('width')),
                                      'height': int(elem.getAttribute('height')),
                                      'vertical_spacing': float(elem.getAttribute('vertical_spacing'))}
                background = tools.svgColorToTuple(self.kwargs_output['background'], 'background')
                font_color = tools.svgColorToTuple(self.kwargs_output['font_color'], 'font')
                errs = [background if isinstance(background, str) else tools.checkRGB(background, 'background'),
                        tools.checkFontName(self.kwargs_output['font_name']),
                        tools.checkFontSize(self.kwargs_output['font_size']),
                        font_color if isinstance(font_color, str) else tools.checkRGB(font_color, 'font')]
                error = ''
                for err in errs:
                    if err:
                        if error:
                            error += ', ' + err
                        else:
                            error = err
                if error:
                    raise error
            except Exception as e:
                self.kwargs_output = 'Loaded file at %s does not have a correct structure; more info: %s' \
                                     % (str(file_name), str(e))
        else:
            self.kwargs_output = 'The provided file name "%s" does not exist to be animated' % file_name
            return

    def __del__(self):
        if self.file_name and not self.from_file:
            try:
                os.remove(self.file_name)
            except:
                pass
        self.doc = ''
        self.kwargs_input = {}
        self.kwargs_output = ''
        self.doc_main = None

    def get_error(self) -> str:
        if isinstance(self.kwargs_output, str):
            return self.kwargs_output
        elif isinstance(self.doc, str):
            return self.doc
        else:
            return ''

    @staticmethod
    def animate_text(file_name: str = '', **kwargs) -> typing.Union[Document, str]:
        if not file_name:
            return 'Cannot animate the SVG file since no file is provided'
        file_handle = None
        try:
            doc: Document = parse(file_name)
            svg = doc.getElementsByTagName('svg')[0]
            svg.setAttribute('class', 'bornalgo-TextAnimator')
            paths = [path for path in doc.getElementsByTagName('path')]
            n = len(paths)
            i = 0
            for path in paths:
                path.setAttribute('id', ('path_%d' % i))
                path.setAttribute('fill', kwargs.get('background', 'white'))
                elem = doc.createElement('animate')
                elem.setAttribute('id', ('animate_%d_show' % i))
                elem.setAttribute('fill', 'freeze')
                elem.setAttribute('dur', kwargs.get('dur', '0.1s'))
                elem.setAttribute('begin', ('animate_%d_show.end' % (i - 1)) if i > 0 else '0s;animate_0_hide.end + 1s')
                elem.setAttribute('to', kwargs.get('font_color', 'black'))
                elem.setAttribute('from', kwargs.get('background', 'white'))
                elem.setAttribute('attributeName', 'fill')
                path.appendChild(elem)
                elem = doc.createElement('animate')
                elem.setAttribute('id', ('animate_%d_hide' % i))
                elem.setAttribute('fill', 'freeze')
                elem.setAttribute('dur', kwargs.get('dur', '0.1s'))
                elem.setAttribute('begin', ('animate_%d_show.end + %s' % ((n - 1), kwargs.get('delay', '5s'))))
                elem.setAttribute('to', kwargs.get('background', 'white'))
                elem.setAttribute('from', kwargs.get('font_color', 'black'))
                elem.setAttribute('attributeName', 'fill')
                path.appendChild(elem)
                i += 1

            desc = doc.createElement('desc')
            desc.setAttribute('id', 'desc_ba-TA')
            for key in kwargs:
                if key != 'text':
                    desc.setAttribute(key, str(kwargs[key]))

            if 'text' in kwargs:
                descText = doc.createTextNode('\n' + kwargs['text'] + '\n')
                desc.appendChild(descText)

            doc.childNodes[0].insertBefore(desc, doc.childNodes[0].firstChild)
            file_handle = open(file_name, 'w')
            doc.writexml(file_handle)
            file_handle.close()
        except Exception as e:
            if file_handle is not None:
                try:
                    file_handle.close()
                except:
                    pass
            return 'Cannot animate the SVG file at %s; more info: %s' % (str(file_name), str(e))

        return doc

    @staticmethod
    def text_to_svg(file_name: str = '', text: str = '', background: tuple = (255, 255, 255),
                    font_name: str = 'Consolas', font_size: int = 0, font_color: tuple = None, width: int = 0,
                    height: int = 0, vertical_spacing: float = 1.2,
                    default_font_size: int = 14, by_char: bool = True) -> typing.Union[dict, str]:
        if not file_name:
            return 'Cannot create the SVG file since no file is provided'
        default_size: int = 100
        background = tuple([min(max(z, 0), 255) for z in background])
        background_01 = tuple([min(max(z / 255, 0), 1) for z in background])
        if font_color is None:
            font_color = tuple([255 - z for z in background])
        else:
            font_color = tuple([min(max(z, 0), 255) for z in font_color])
        font_color_01 = tuple([min(max(z / 255, 0), 1) for z in font_color])
        try:
            surface = cairo.SVGSurface(file_name, width if width > 0 else default_size,
                                       height if height > 0 else default_size)
            context = cairo.Context(surface)
            context.set_source_rgb(*background_01)
            context.rectangle(0, 0, width if width > 0 else default_size,
                              height if height > 0 else default_size)
            context.fill()
            context.set_source_rgb(*font_color_01)
            context.set_font_size(font_size if font_size > 0 else default_font_size)
            context.select_font_face(font_name)
            lines: list = text.split('\n')
            text_extents_lines = [context.text_extents(line) for line in lines]
            w: float = max([each.x_advance for each in text_extents_lines])
            hmax = max([each.height for each in text_extents_lines])
            vspace = vertical_spacing * hmax - hmax
            h: float = sum([each.height for each in text_extents_lines]) + vspace * (len(text_extents_lines) - 1)
            proposed_font_size = default_font_size
            reevaluate = False
            if (font_size > 0 and (width <= 0 or w > width or height <= 0 or h > height)) or \
                    (font_size <= 0 and width <= 0 and height <= 0):
                if width <= w:
                    width = math.ceil(w)
                if height <= h:
                    height = math.ceil(h)
                reevaluate = True

            elif font_size <= 0:
                if width <= 0 or height <= 0:
                    proposed_font_size = math.floor(default_font_size * ((height / h) if height <= 0 else (width / w)))
                else:
                    proposed_font_size = math.floor(default_font_size * min((height / h), (width / w)))
                if proposed_font_size != default_font_size:
                    reevaluate = True

            if reevaluate:
                surface.finish()
                surface.flush()
                os.remove(file_name)
                return TextAnimator.text_to_svg(file_name=file_name, text=text, background=background,
                                                font_name=font_name, font_size=font_size, font_color=font_color,
                                                width=width, height=height, vertical_spacing=vertical_spacing,
                                                default_font_size=proposed_font_size)

            font_size = default_font_size if font_size <= 0 else font_size
            x = 0
            y = 0
            dic = {}
            text_extents_A: typing.Union[cairo.TextExtents, None] = None
            i = 0
            for line in lines:
                dx = x
                y -= text_extents_lines[i].y_bearing
                if by_char:
                    for char in line:
                        val = dic.get(chr)
                        if val is None:
                            text_extents: cairo.TextExtents = context.text_extents(char)
                            if text_extents.width == 0:
                                if text_extents_A is None:
                                    text_extents_A = context.text_extents('A')
                                text_extents = context.text_extents('A' + char + 'A')
                                val = text_extents.x_advance - 2 * text_extents_A.x_advance
                                dx += val
                                dic[chr] = val
                                continue
                            val = text_extents.x_advance
                            dic[chr] = val
                        context.new_path()
                        context.move_to(dx, y)
                        context.text_path(char)
                        context.fill()
                        context.close_path()
                        dx += val
                else:
                    # This will create animations based on characters
                    context.new_path()
                    context.move_to(dx, y)
                    context.show_text(line)
                    context.fill()
                    context.close_path()
                y += text_extents_lines[i].y_bearing + text_extents_lines[i].height + vspace
                i += 1

            surface.finish()
            surface.flush()
        except Exception as e:
            return 'Cannot create the SVG file at %s; more info: %s' % (str(file_name), str(e))

        return {'width': width, 'height': height, 'background': 'rgb(%d, %d, %d)' % background,
                'text': text, 'font_color': 'rgb(%d, %d, %d)' % font_color, 'font_name': font_name,
                'font_size': font_size, 'vertical_spacing': vertical_spacing}
