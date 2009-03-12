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

from shared import SharedActivity
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
        self.edit_bar = edit.Toolbar(self.edit)

        self.library = library.View(self)
        library_bar = library.Toolbar(self.library)

        toolbox = ActivityToolbox(self)
        toolbox.connect('current-toolbar-changed', self._toolbar_changed_cb)
        self.set_toolbox(toolbox)
        toolbox.add_toolbar(_('Library'), library_bar)
        toolbox.add_toolbar(_('Edit'), self.edit_bar)

        edit_fake = gtk.EventBox()

        self.notebook.append_page(self.library)
        self.notebook.append_page(self.edit)
        self.notebook.append_page(edit_fake)

        toolbox.set_current_toolbar(1)
        self.show_all()

    def new_instance(self):
        self.instance()

    def resume_instance(self, filepath):
        book.custom = book.CustomBook(filepath)
        self.instance()

    def save_instance(self, filepath):
        book.wiki.sync()
        book.custom.sync(filepath)

    def set_edit_sensitive(self, enable):
        self.edit_bar.props.sensitive = enable
        self.edit_page = (enable and 1 or 2)

    def _toolbar_changed_cb(self, widget, index):
        if index > 0:
            if index == 1:
                index = 0
            else:
                self.library.sync()
                index = self.edit_page
            self.notebook.set_current_page(index)
