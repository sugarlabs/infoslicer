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

from infoslicer.widgets.Edit_Pane import Edit_Pane
from infoslicer.widgets.Format_Pane import Format_Pane
from infoslicer.widgets.Image_Pane import Image_Pane
import book

TABS = (Edit_Pane(),
        Image_Pane(),
        Format_Pane())

class View(gtk.Notebook):
    def __init__(self):
        gtk.Notebook.__init__(self)
        self.props.show_border = False
        self.props.show_tabs = False

        for i in TABS:
            self.append_page(i)
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

        self.txt_toggle = ToggleToolButton('ascii')
        self.img_toggle = ToggleToolButton('image')

        self.txt_toggle.set_tooltip(_('Text'))
        self.txt_toggle.connect('toggled', self._toggle_cb,
            [self.txt_toggle, self.img_toggle])
        toolbar.insert(self.txt_toggle, -1)

        self.img_toggle.set_tooltip(_('Images'))
        self.img_toggle.connect('toggled', self._toggle_cb,
            [self.txt_toggle, self.img_toggle])
        toolbar.insert(self.img_toggle, -1)

        self.separator = gtk.SeparatorToolItem()
        toolbar.insert(self.separator, -1)

        for tab in TABS:
            for i in tab.toolitems:
                toolbar.insert(i, -1)

        self.txt_toggle.set_active(True)

    def sensitize_all(self):
        self.txt_toggle.set_sensitive(True)
        self.img_toggle.set_sensitive(True)

    def unsensitize_all(self):
        self.txt_toggle.set_sensitive(False)
        self.img_toggle.set_sensitive(False)

    def _toggle_cb(self, widget, toggles):
        for tab in TABS:
            for i in tab.toolitems:
                i.hide()

        if not widget.get_active():
            index = 2
        else:
            another = toggles[0] == widget and 1 or 0
            toggles[another].set_active(False)
            index = int(not another)

        for i in TABS[index].toolitems:
            i.show()

        if book.wiki.article:
            TABS[index].set_source_article(book.wiki.article)
        if book.custom.article:
            TABS[index].set_working_article(book.custom.article)

        self.edit.set_current_page(index)
