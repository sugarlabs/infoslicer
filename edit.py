# Copyright (C) IBM Corporation 2008
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GObject
from gi.repository import GLib
from gettext import gettext as _

from sugar3.graphics.toolbutton import ToolButton
from sugar3.graphics.toggletoolbutton import ToggleToolButton

from sugar3 import mime
from sugar3.graphics.objectchooser import ObjectChooser

from infoslicer.widgets.Edit_Pane import Edit_Pane
from infoslicer.widgets.Format_Pane import Format_Pane
from infoslicer.widgets.Image_Pane import Image_Pane
from infoslicer.widgets.Journal_Image_Pane import Journal_Image_Pane
from infoslicer.processing.HTML_strip import dehtml
from infoslicer.processing.Article import Article

import book

import logging


TABS = (Edit_Pane(),
        Image_Pane(),
        Journal_Image_Pane(),
        Format_Pane())


class View(Gtk.Notebook):
    def __init__(self):
        GObject.GObject.__init__(self)
        self.props.show_border = False
        self.props.show_tabs = False

        for i in TABS:
            self.append_page(i, None)
            i.show()

        self.connect('map', self._map_cb)

    def _map_cb(self, widget):
        index = self.get_current_page()

        if book.wiki.article:
            TABS[index].set_source_article(book.wiki.article)
        if book.custom.article:
            TABS[index].set_working_article(book.custom.article)

class ToolbarBuilder():
    def __init__(self, edit, toolbar):
        self.edit = edit
        logging.debug('init edit toolbar')
        logging.debug(self.edit)

        self.txt_toggle = ToggleToolButton('ascii')
        self.img_toggle = ToggleToolButton('image')
        self.jimg_toggle = ToggleToolButton('journal-image')
        self.jimg_chooser_toggle = ToolButton('load-image-from-journal')
        self.jtext_chooser_toggle = ToolButton('load-text-from-journal')

        self.txt_toggle.set_tooltip(_('Text'))
        self.txt_toggle.connect('toggled', self._toggle_cb,
            [self.txt_toggle, self.img_toggle, self.jimg_toggle])
        toolbar.insert(self.txt_toggle, -1)

        self.img_toggle.set_tooltip(_('Images'))
        self.img_toggle.connect('toggled', self._toggle_cb,
            [self.txt_toggle, self.img_toggle, self.jimg_toggle])
        toolbar.insert(self.img_toggle, -1)

        self.jimg_toggle.set_tooltip(_('Journal Images'))
        self.jimg_toggle.connect('toggled', self._toggle_cb,
            [self.txt_toggle, self.img_toggle, self.jimg_toggle])
        toolbar.insert(self.jimg_toggle, -1)

        self.jimg_chooser_toggle.set_tooltip(_('Choose Journal Images'))
        self.jimg_chooser_toggle.connect('clicked', self._toggle_image_chooser)
        toolbar.insert(self.jimg_chooser_toggle, -1)

        self.jtext_chooser_toggle.set_tooltip(_('Choose Journal Text'))
        self.jtext_chooser_toggle.connect('clicked', self._toggle_text_chooser)
        toolbar.insert(self.jtext_chooser_toggle, -1)

        for tab in TABS:
            for i in tab.toolitems:
                toolbar.insert(i, -1)

        self.txt_toggle.set_active(True)

    def sensitize_all(self):
        self.txt_toggle.set_sensitive(True)
        self.img_toggle.set_sensitive(True)
        self.jimg_toggle.set_sensitive(True)

    def unsensitize_all(self):
        self.txt_toggle.set_sensitive(False)
        self.img_toggle.set_sensitive(False)
        self.jimg_toggle.set_sensitive(False)

    def _toggle_image_chooser(self, widget):
        # self._old_cursor = self.edit.get_window().get_cursor()
        # self.edit.get_window().set_cursor(Gdk.Cursor.new(Gdk.CursorType.WATCH))
        GLib.idle_add(self.__image_chooser)

    def __image_chooser(self):
        chooser = ObjectChooser(what_filter=mime.GENERIC_TYPE_IMAGE)
        result = chooser.run()
        if result == Gtk.ResponseType.ACCEPT:
            jobject = chooser.get_selected_object()
            if jobject and jobject.file_path:
                title = str(jobject.metadata['title'])
                path = str(jobject.file_path)
                TABS[2].gallery.add_image(path, title)
        # self.edit.get_window().set_cursor(self._old_cursor)

    def _toggle_text_chooser(self, widget):
        # self._old_cursor = self.edit.get_window().get_cursor()
        # self.edit.get_window().set_cursor(Gdk.Cursor.new(Gdk.CursorType.WATCH))
        GLib.idle_add(self.__text_chooser)

    def __text_chooser(self):
        chooser = ObjectChooser(what_filter=mime.GENERIC_TYPE_TEXT)
        result = chooser.run()
        if result == Gtk.ResponseType.ACCEPT:
            jobject = chooser.get_selected_object()
            if jobject and jobject.file_path:
                title = str(jobject.metadata['title'])
                path = str(jobject.file_path)
                fp = open(path, 'r')
                text = fp.read()
                fp.close()
                article_data = dehtml(text, title)
                TABS[0].set_source_article(Article(article_data))
        # self.edit.get_window().set_cursor(self._old_cursor)

    def _toggle_cb(self, widget, toggles):
        for tab in TABS:
            for i in tab.toolitems:
                i.hide()

        if not widget.get_active():
            index = 3
        else:
            for t in range(0, len(toggles)):
                if toggles[t] != widget:
                    toggles[t].set_active(False)
                else:
                    index = t

        for i in TABS[index].toolitems:
            i.show()

        # We don't require any article data to display jounal images
        if book.wiki.article and index != 2:
            TABS[index].set_source_article(book.wiki.article)
        if book.custom.article:
            TABS[index].set_working_article(book.custom.article)

        self.edit.set_current_page(index)
