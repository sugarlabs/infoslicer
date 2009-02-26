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

        self.connect('init', self._init_cb)
        self.connect('tube', self._tube_cb)

    def read_file(self, filepath):
        pass

    def write_file(self, filepath):
        book.teardown()

    def _init_cb(self, sender):
        book.init()

        self.library = library.View()
        self.library.show()
        self.notebook.append_page(self.library)

        self.edit = edit.View()
        self.edit.show()
        self.notebook.append_page(self.edit)

        toolbox = ActivityToolbox(self)
        toolbox.show()
        toolbox.connect('current-toolbar-changed', self._toolbar_changed_cb)
        self.set_toolbox(toolbox)

        library_bar = library.Toolbar(self.library)
        library_bar.show()
        toolbox.add_toolbar(_('Library'), library_bar)

        edit_bar = edit.Toolbar(self.edit)
        edit_bar.show()
        toolbox.add_toolbar(_('Edit'), edit_bar)

        toolbox.set_current_toolbar(1)

    def _tube_cb(self, activity, tube_conn, initiating):
        pass

    def _toolbar_changed_cb(self, widget, index):
        if index > 0:
            self.notebook.set_current_page(index-1)
