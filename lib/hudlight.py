#!/usr/bin/env python
# -*- coding: utf-8 -*-

# A HUD that is easy to use.
# Copyright Gummbum, 4/18/2017. Free software, no warranty express or implied.

"""hudlight.py - a basic HUD with a lot of conveniences

hud = HUD()

hud.add('fps', '{} fps', 0)
hud.update_item('fps', int(clock.get_fps()))

hud.add('date', '{} {}', time, date)
hud.update_item('date', time, date)

hud.add('mouse', '{0[0]}, {0[1]}', (0, 0))
hud.update_item('mouse', pygame.mouse.get_pos())

hud.draw(pygame.display.get_surface())

See demo1-so-easy.py for an introductory usage; demo2-casting-a-shadow.py for slightly more complex.

Despite the seeming simplicity of the above examples, one can do quite a lot with this HUD. See demo3-all-features.py
for a very elaborate example. But keep in mind that demo3 is not typical of HUD implementations. It is very elaborate
because the HUD is the interactive GUI which displays the real-time values for all the HUD features. This demo3 is
primarily an interactive runtime tester, so it lets you play with all the features.
"""

import collections

import pygame

import pygametext

__version__ = '3.0.0'
__vernum__ = tuple(int(s) for s in __version__.split('.'))
__all__ = ['HUDNameExists', 'HUDNameNotFound', 'HUDBadArgs', 'HUD', 'set_font_template']


class HUDNameExists(BaseException):
    """HUD non-unique name in items list"""
    pass


class HUDNameNotFound(BaseException):
    """HUD name not found in items list"""
    pass


class HUDBadArgs(BaseException):
    """HUD update_item() arg count does not match args given to add()"""
    pass


def set_font_template(s="%s"):
    """set template using old style string formatting

    For example, set_font_template("fonts/%s.ttf"). The module default is "%s".

    :param s: str
    :return:
    """
    pygametext.FONT_NAME_TEMPLATE = s


class HUD(object):
    """HUD class for a basic Heads Up Display

    Not supported:
        - Per-item details (font, size, style, antialias, color).

    Tips and tricks:
        Color arguments may be string names, color sequences, or pygame.Color.

        Note the difference between set_color(None) and set_background(None). The former is ignored. The latter
        has the side effect of making the background transparent.

        set_bold() and set_italic() are software rendering effects. If bold and italic fonts exist they give
        more pleasing results.

        If you want per-item details (font, size, style, antialias, color) or want to use HUD in a more robust
        dashboard-like way, you can make multiple HUDs with custom x, y positions. If you want to calculate
        their size for positioning, use the hud_size() method, keeping in mind that changing SysFont styles,
        font file, etc. will change the rendered size. One can use the same trick with the HUD that is often
        done with words: render the longest strings with the widest character (usually "W") and then remember
        the size for layout calculations.

        The font items are rendered in the order they are added. Order can be rearranged at any time by
        modifying the hud.order list, which is simply a list of the item names. When modifying hud.order and/or
        hud.items take care to keep the contents one-to-one.
    """

    def __init__(self, fontname=None, fontsize=24, sysfontname='sans', bold=False, italic=False, underline=False,
                 color='gold', background=None, gcolor=None, ocolor=None, scolor=None,
                 owidth=1, shadow=(1, 1), antialias=True, alpha=1.0):
        """create a basic HUD

        The defaults are simply sysfont_name='sans', fontsize=16, antialias=True.

        Positioning is anchored at topleft. Modify via x and y attribute. The default is 10, 10.

        Vertical spacing for items is 3 pixels by default. Modify via space attribute.

        :param fontname: the name of a font file
        :param fontsize: point size of the font
        :param sysfontname: the name of a system font
        :param bold: boolean
        :param italic: boolean
        :param underline: boolean
        :param color: text foreground color
        :param background: text background color
        :param gcolor: text gradient color
        :param ocolor: text outline color
        :param scolor: text shadow color
        :param owidth: int (float?), width in pixels of outline
        :param shadow: tuple of int, (x, y) offset for drop shadow
        :param antialias: boolean
        :param alpha: float, valid values are 0.0 - 1.0
        :return: HUD
        """
        # Info needed to position and draw HUD items on a surface.
        self.x = 10
        self.y = 10
        self.space = 1

        self.order = []  # list to order rendering
        self.items = {}  # HUD data
        self.dirty = True

        # Info needed to create a font object.
        self._fontname = fontname
        self._fontsize = fontsize
        self._sysfontname = sysfontname
        self._bold = bold
        self._italic = italic
        self._underline = underline
        self._font_info = self._fontname, self._fontsize, self._sysfontname, self._bold, self._italic, self._underline

        # Info needed for pygametext effects.
        self._fgcolor = None
        self._background = None
        self._gcolor = None
        self._scolor = None
        self._ocolor = None
        self._antialias = None
        self._alpha = None
        self._owidth = owidth
        self._shadow = shadow

        self.set_color(color)
        self.set_background(background)
        self.set_gcolor(gcolor)
        self.set_ocolor(ocolor)
        self.set_scolor(scolor)
        self.set_shadow(shadow)
        self.set_antialias(antialias)
        self.set_alpha(alpha)
        self.set_font(fontname, fontsize, sysfontname, bold, italic, underline)

        self.perf = collections.deque()
        self.perf_history_secs = 1

    def fps(self):
        return len(self.perf) / self.perf_history_secs

    def hud_size(self):
        """get the total rendered size of the HUD (may change depending on style, etc.)
        :return: w, h
        """
        total_w = 0
        total_h = 0
        for item in self.items.values():
            w, h = item[0].get_size()
            # inline is much faster than max()
            total_w = w if w > total_w else total_w
            total_h = h if h > total_h else total_h
            total_h += self.space
        total_h -= self.space
        return total_w, total_h

    def add(self, name, text, *args, **kwargs):
        """add a HUD item

        HUD items are rendered in the order they are added. Order can be rearranged at any time by modifying
        hud.order, which is simply a list of the item names.

        An item can use varargs or kwargs, not both. The choice is enforced when the item is updated.

        :param name: unique ID
        :param text: format text compatible with str.format()
        :param args: arguments for str.format()
        :param kwargs: optional, callback=func
        :return: None
        """
        if name in self.items:
            raise HUDNameExists('HUD non-unique name {}'.format(name))
        callback = kwargs.get('callback', None)
        if args:
            item = [None, text, args, callback]
        else:
            item = [None, text, kwargs, callback]
        self._render(item)
        self.order.append(name)
        self.items[name] = item

    def update_item(self, name, *args, **kwargs):
        """update the value of an item (does not invoke the callback)

        If the item was created with varargs, then the item must be updated with varargs.

        If item was created with kwargs, it must be updated with kwargs.

        If item was created with callback, callback will be invoked. The presence of args or kwargs will
        override the callback; this is by design, though it may not be practical to use a callback item
        this way.

        :param name: item's name
        :param args: item's new value
        :return: None
        """
        try:
            item = self.items[name]
        except KeyError:
            raise HUDNameNotFound('HUD name not found {}'.format(name))
        if args:
            # if len(args) != len(item[2]):
            #     raise HUDBadArgs('{}: arg count {} != {}'.format(name, len(args), len(item[2])))
            # if args != item[2]:     # <<< NO, does not compare deeper items
            if [a for a, b in zip(args, item[2]) if a != b]:
                item[2] = args
                self._render(item)
        elif kwargs:
            changed = False
            for k in kwargs:
                if item[2][k] != kwargs[k]:
                    changed = True
                    break
            if changed:
                item[2] = kwargs
                self._render(item)
        elif item[3]:
            callback = item[3]
            if callback:
                val = callback()
                if isinstance(item[2], dict):
                    self.update_item(name, **val)
                elif isinstance(val, str):
                    self.update_item(name, val)
                else:
                    try:
                        self.update_item(name, *val)
                    except:
                        self.update_item(name, val)

    def update(self, *args):
        """update all items, using the callbacks provided with add()

        Logic uses the type of the value passed in add() to determine how to update the value.
        The order of evaluation is dict, str, sequence, then discrete value.

        :param args: not used; for compatibility with timers, etc. that supply args by default
        :return: None
        """
        for name in self.items:
            self.update_item(name)

    def draw(self, surf):
        """draw all the items

        :param surf: target surface
        :return: None
        """
        if self.dirty:
            for item in self.items.values():
                self._render(item)
            self.dirty = False

        items = self.items
        x = self.x
        y = self.y
        for key in self.order:
            img = items[key][0]
            surf.blit(img, (x, y))
            y += img.get_height() + self.space

    def _render(self, item):
        if isinstance(item[2], dict):
            text = item[1].format(**item[2])
        else:
            text = item[1].format(*item[2])
        item[0] = pygametext.getsurf(text, self._fontname, self._fontsize, self._sysfontname,
                                     self._bold, self._italic, self._underline,
                                     color=self._fgcolor, background=self._background, antialias=self._antialias,
                                     ocolor=self._ocolor, scolor=self._scolor, gcolor=self._gcolor,
                                     shadow=None if self._scolor is None else self._shadow,
                                     owidth=None if self._ocolor is None else self._owidth,
                                     alpha=self._alpha)
        t0 = pygame.time.get_ticks()
        t1 = t0 - self.perf_history_secs * 1000
        perf = self.perf
        popleft = perf.popleft
        perf.append(t0)
        while perf[0] < t1:
            popleft()

    def get_font(self):
        """get the current font object
        :return: pygame.font.Font
        """
        return pygametext.getfont(*self._font_info)

    def set_font(self, fontname=None, fontsize=None, sysfontname=None, bold=None, italic=None, underline=None):
        """change font

        If any of the args are not specified the instance variables are used. The instance variables are
        updated to reflect the supplied values.

        Font creation and re-rendering of items is triggered.

        :param fontname: the name of a font file
        :param fontsize: point size of the font
        :param sysfontname: the name of a sysfont
        :param bold: boolean
        :param italic: boolean
        :param underline: boolean
        :return: self
        """
        if fontname is not None:
            sysfontname = None
        elif sysfontname is not None:
            fontname = None
        else:
            fontname = self._fontname
            sysfontname = self._sysfontname
        fontsize = fontsize if fontsize is not None else self._fontsize
        bold = bold if bold is not None else self._bold
        italic = italic if italic is not None else self._italic
        underline = underline if underline is not None else self._underline
        new_info = fontname, fontsize, sysfontname, bold, italic, underline

        if self._font_info != new_info or self.dirty:
            self._font_info = new_info
            self._fontname, self._fontsize, self._sysfontname, self._bold, self._italic, self._underline = new_info
            self.dirty = True
        return self

    def set_fontname(self, name):
        """change the font source to a file font

        :param name: the name of a font file or system font
        :return: self
        """
        self.set_font(fontname=name)
        return self

    def get_fontname(self):
        return self._fontname

    def set_sysfontname(self, name):
        """change the font source to a sysfont

        :param name: the name of a font file or system font
        :return: self
        """
        self.set_font(sysfontname=name)
        return self

    def get_sysfontname(self):
        return self._sysfontname

    def set_fontsize(self, fontsize):
        """change the font size
        :param fontsize: int
        :return: self
        """
        self.set_font(fontsize=fontsize)
        return self

    def get_fontsize(self):
        return self._fontsize

    def set_bold(self, boolean):
        """change the bold style
        :param boolean
        :return: self
        """
        self.set_font(bold=boolean)
        return self

    def get_bold(self):
        return self._bold

    def set_italic(self, boolean):
        """change the italic style
        :param boolean
        :return: self
        """
        self.set_font(italic=boolean)
        return self

    def get_italic(self):
        return self._italic

    def set_underline(self, boolean):
        """change the underline style
        :param boolean
        :return: None
        """
        self.set_font(underline=boolean)
        return self

    def get_underline(self):
        return self._underline

    def set_color(self, color):
        """change foreground color
        :param color: a pygame.Color, color sequence, or name string
        :return: self
        """
        if color is None:
            return

        self._fgcolor = color
        self.dirty = True
        return self

    def get_color(self):
        return self._fgcolor

    def set_background(self, color):
        """change background color

        If color is None, the background will be transparent.

        :param color: a pygame.Color, color sequence, or name string
        :return: self
        """
        self._background = color
        self.dirty = True
        return self

    def get_background(self):
        return self._background

    def set_gcolor(self, color=None):
        """change gradient color

        If color is None, the gradient effect will be removed.

        :param color: a pygame.Color, color sequence, or name string
        :return: self
        """
        self._gcolor = color
        self.dirty = True
        return self

    def get_gcolor(self):
        return self._gcolor

    def set_scolor(self, color=None):
        """render a drop shadow color

        If color is None, the shadow effect will be removed.

        :param color: a pygame.Color, color sequence, name string, or None
        :return: self
        """
        self._scolor = color
        self.dirty = True
        return self

    def get_scolor(self):
        return self._scolor

    def set_shadow(self, shadow):
        """set the x, y distance in pixels to project the shadow
        :param shadow: tuple of two ints; the offset of the shadow; e.g. (1, 1), (0, 1), (-2, -2)
        :return: self
        """
        self._shadow = shadow
        self.dirty = True
        return self

    def get_shadow(self):
        return self._shadow

    def set_ocolor(self, color=None):
        """render an outline color

        If color is None, the outline effect will be removed.

        :param color: a pygame.Color, color sequence, name string, or None
        :return: self
        """
        self._ocolor = color
        self.dirty = True
        return self

    def get_ocolor(self):
        return self._ocolor

    def set_owidth(self, width):
        """set outline width
        :param width: int >= 0
        :return: self
        """
        if width >= 0:
            self._owidth = width
            self.dirty = True
        return self

    def get_owidth(self):
        return self._owidth

    def set_alpha(self, alpha):
        """change the surface alpha value

        Valid values are 0.0 to 1.0.

        :param alpha: int, 0 to 255; if None it is disabled
        :return: self
        """
        self._alpha = alpha
        for item in self.items.values():
            item[0].set_alpha(alpha)
        return self

    def get_alpha(self):
        return self._alpha

    def set_antialias(self, boolean):
        """render antialiased font
        :param boolean
        :return: self
        """
        if boolean in (True, False, 1, 0):
            self._antialias = boolean
            self.dirty = True
        return self

    def get_antialias(self):
        return self._antialias
