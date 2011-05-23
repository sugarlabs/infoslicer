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

import gtk
from gettext import gettext as _

from sugar.graphics.toolbutton import ToolButton
from sugar.graphics.toggletoolbutton import ToggleToolButton
from sugar.activity.activity import ActivityToolbox
OLD_TOOLBAR = False
try:
    from sugar.graphics.toolbarbox import ToolbarBox, ToolbarButton
    from sugar.activity.widgets import StopButton
    from sugar.graphics.radiotoolbutton import RadioToolButton
    from sugar.activity.widgets import ActivityToolbarButton
except ImportError:
    OLD_TOOLBAR = True
from port.activity import SharedActivity

import library
import edit
import book

gtk.gdk.threads_init()
gtk.gdk.threads_enter()

class InfoslicerActivity(SharedActivity):
    def __init__(self, handle):
        self.notebook = gtk.Notebook()
        self.notebook.show()
        self.notebook.props.show_border = False
        self.notebook.props.show_tabs = False

        SharedActivity.__init__(self, self.notebook, 'SERVICE', handle)

    def instance(self):
        book.wiki = book.WikiBook()
        if not book.custom:
            book.custom = book.CustomBook()

        self.edit_page = 1
        self.edit = edit.View()
        self.library = library.View(self)

        if OLD_TOOLBAR:
            self.edit_toolbar = gtk.Toolbar()
            self.edit_bar = edit.ToolbarBuilder(self.edit, self.edit_toolbar)
            self.edit_toolbar.show_all()

            self.library_toolbar = gtk.Toolbar()
            self.library_bar = library.ToolbarBuilder(self.library,
                    self.library_toolbar)
            self.library_toolbar.show_all()

            toolbox = ActivityToolbox(self)
            toolbox.connect('current-toolbar-changed',
                    self._toolbar_changed_cb)
            self.set_toolbox(toolbox)
            toolbox.add_toolbar(_('Library'), self.library_toolbar)
            toolbox.add_toolbar(_('Edit'), self.edit_toolbar)
            toolbox.set_current_toolbar(1)
        else:
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
            self._toolbar.insert(gtk.SeparatorToolItem(), -1)
            self.edit_bar = edit.ToolbarBuilder(self.edit, self._toolbar)
            self.library_bar = library.ToolbarBuilder(self.library, self._toolbar)

        edit_fake = gtk.EventBox()

        self.notebook.append_page(self.library)
        self.notebook.append_page(self.edit)
        self.notebook.append_page(edit_fake)

        self.show_all()

        if not OLD_TOOLBAR:
            self.__mode_button_clicked(search_button)
            separator = gtk.SeparatorToolItem()
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
        book.custom = book.CustomBook(filepath)
        self.instance()

    def save_instance(self, filepath):
        book.wiki.sync()
        book.custom.sync(filepath)

    def set_edit_sensitive(self, enable):
        if OLD_TOOLBAR:
            #self.edit_toolbar.props.sensitive = enable
            self.edit_page = (enable and 1 or 2)

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
