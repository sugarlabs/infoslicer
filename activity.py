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

import gi
gi.require_version('Gtk','3.0')
from gi.repository import Gtk
from gi.repository import GLib
from gettext import gettext as _

GLib.threads_init()

from sugar3.graphics.toolbutton import ToolButton
from sugar3.graphics.toggletoolbutton import ToggleToolButton
from sugar3.graphics.toolbarbox import ToolbarBox, ToolbarButton
from sugar3.activity.widgets import StopButton
from sugar3.activity import activity
from sugar3.graphics.radiotoolbutton import RadioToolButton
from sugar3.activity.widgets import ActivityToolbarButton


import library
import edit
import book

class InfoslicerActivity(activity.Activity):
    def __init__(self, handle):
        self.notebook = Gtk.Notebook()
        self.notebook.show()
        self.notebook.props.show_border = False
        self.notebook.props.show_tabs = False

        activity.Activity.__init__(self, handle)

        self.max_participants = 1

        self.set_canvas(self.notebook)
        self.instance()

    def instance(self):
        book.WIKI = book.WikiBook()
        if not book.CUSTOM:
            book.CUSTOM = book.CustomBook()

        self.edit_page = 1
        self.edit = edit.View()
        self.library = library.View(self)

        toolbar_box = ToolbarBox()
        activity_button = ActivityToolbarButton(self)
        toolbar_box.toolbar.insert(activity_button, 0)
        self.set_toolbar_box(toolbar_box)
        self._toolbar = toolbar_box.toolbar

        tool_group = None
        search_button = RadioToolButton()
        search_button.props.group = tool_group
        tool_group = search_button
        search_button.props.icon_name = 'white-search'
        search_button.set_tooltip(_('Library'))
        search_button.mode = 'search'
        search_button.connect('clicked', self.__mode_button_clicked)
        self._toolbar.insert(search_button, -1)

        edit_button = RadioToolButton()
        edit_button.props.group = tool_group
        edit_button.props.icon_name = 'toolbar-edit'
        edit_button.set_tooltip(_('Edit'))
        edit_button.mode = 'edit'
        edit_button.connect('clicked', self.__mode_button_clicked)
        self._toolbar.insert(edit_button, -1)
        self._toolbar.insert(Gtk.SeparatorToolItem(), -1)
        self.edit_bar = edit.ToolbarBuilder(self.edit, self._toolbar)
        self.library_bar = library.ToolbarBuilder(self.library,
                                                  activity_button)
        self.library_bar.publish.show()

        edit_fake = Gtk.EventBox()

        self.notebook.append_page(self.library, None)
        self.notebook.append_page(self.edit, None)
        self.notebook.append_page(edit_fake, None)

        self.show_all()

        self.__mode_button_clicked(search_button)
        separator = Gtk.SeparatorToolItem()
        separator.props.draw = False
        separator.set_expand(True)
        separator.show()
        self._toolbar.insert(separator, -1)
        stop_button = StopButton(self)
        stop_button.show()
        self._toolbar.insert(stop_button, -1)

    def new_instance(self):
        self.instance()

    def resume_instance(self, filepath):
        book.CUSTOM = book.CustomBook(filepath)
        self.instance()

    def save_instance(self, filepath):
        book.WIKI.sync()
        book.CUSTOM.sync(filepath)

    def set_edit_sensitive(self, enable):
        pass

    def _toolbar_changed_cb(self, widget, index):
        if index > 0:
            if index == 1:
                index = 0
            else:
                self.library.sync()
                index = self.edit_page
            self.notebook.set_current_page(index)

    def __mode_button_clicked(self, button):
        if button.mode == 'search':
            self.edit_bar.unsensitize_all()
            self.notebook.set_current_page(0)
        else:
            self.edit_bar.sensitize_all()
            self.notebook.set_current_page(1)
