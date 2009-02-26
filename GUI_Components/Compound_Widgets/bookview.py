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

import os
import gtk
import logging
import gobject
from gettext import gettext as _

from sugar.graphics.toolbutton import ToolButton
from sugar.activity.activity import get_bundle_path, get_activity_root
from sugar.graphics.style import *

from Processing.IO_Manager import IO_Manager
from GUI_Components.Compound_Widgets.toolbar import WidgetItem, ButtonItem

logger = logging.getLogger('infoslicer')

class BookView(gtk.VBox):
    def __init__(self, book, name):
        gtk.VBox.__init__(self)
        self.book = book
        self._changing = None

        title = gtk.Toolbar()

        # title checkbox

        self._check = gtk.CheckButton()
        self._check.props.can_focus = False
        self._check.props.tooltip_text = _('Chech/uncheck all articles')
        self._check.connect('toggled', self._check_toggled_cb)
        check_box = gtk.HBox()
        check_box.set_size_request(50, -1)
        check_box.pack_start(self._check, True, False)
        title.insert(WidgetItem(check_box), -1)

        # title caption

        caption_label = gtk.Label(name)
        caption_label.modify_fg(gtk.STATE_NORMAL, COLOR_WHITE.get_gdk_color())
        caption_box = gtk.HBox()
        caption_box.pack_start(check_box, False)
        caption_box.pack_start(caption_label, False)
        caption = gtk.EventBox()
        caption.add(caption_box)
        caption.modify_bg(gtk.STATE_NORMAL, COLOR_TOOLBAR_GREY.get_gdk_color())
        title.insert(WidgetItem(caption), -1)

        separator = gtk.SeparatorToolItem()
        separator.props.draw = False
        separator.set_expand(True)
        title.insert(separator, -1)

        # move buttons
        
        downward = ButtonItem('go-down',
                label='Move downward',
                tooltip_text=_('Move article downward'))
        downward.connect('clicked', self._downward_clicked_cb)
        title.insert(downward, -1)
        upward = ButtonItem('go-up',
                label=_('Move upward'),
                tooltip_text=_('Move article upward'))
        upward.connect('clicked', self._upward_clicked_cb)
        title.insert(upward, -1)

        # tree

        self.store = gtk.ListStore(bool, str)
        self.tree = gtk.TreeView(self.store)
        self.tree.props.headers_visible = False
        self.tree.connect('cursor-changed', self._cursor_changed_cb)

        cell = gtk.CellRendererToggle()
        cell.connect('toggled', self._cell_toggled_cb)
        cell.props.activatable = True

        column = self.tree.insert_column_with_attributes(0, '', cell, active=0)
        column.props.sizing = gtk.TREE_VIEW_COLUMN_FIXED
        column.props.fixed_width = 50

        cell = gtk.CellRendererText()
        cell.connect('edited', self._cell_edited_cb)
        cell.props.editable = True
        self.tree.insert_column_with_attributes(1, '', cell, text=1)

        for i in self.book.map:
            self.store.append((False, i['title']))

        # scrolled tree

        tree_scroll = gtk.ScrolledWindow()
        tree_scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        tree_scroll.add_with_viewport(self.tree)

        self.pack_start(title, False)
        self.pack_start(tree_scroll)
        self.tree.set_cursor(0, self.tree.get_column(1), False)
        self.show_all()

    def _downward_clicked_cb(self, widget):
        pass

    def _upward_clicked_cb(self, widget):
        pass

    def _check_toggled_cb(self, widget):
        for i in self.store:
            i[0] = widget.props.active
        self._check.props.inconsistent = False

    def _cell_toggled_cb(self, cell, index):
        value = not self.store[index][0]
        self.store[index][0] = value

        for i in self.store:
            if i[0] != value:
                self._check.props.inconsistent = True
                return

        self._check.props.inconsistent = False
        self._check.props.active = value

    def _cursor_changed_cb(self, widget):
        if self._changing:
            gobject.source_remove(self._changing)
        index, column = self.tree.get_cursor()
        self._changing = gobject.timeout_add(1000, self._cursor_changed, index)

    def _cursor_changed(self, index):
        self.book.props.article = self.store[index][1]
        self._changing = False
        return False

    def _cell_edited_cb(self, cell, index, newtext):
        # Disallowed chars are < > and &
        if newtext == "" or newtext.isspace() or '&' in newtext \
                or '<' in newtext or '>' in newtext:
            return

        index, column = self.tree.get_cursor()

        if self._changing:
            gobject.source_remove(self._changing)
            _cursor_changed(index)
        
        # If there is already an article with the new name in the theme,
        # then we ignore the name change and highlight the existing article
        overides = [i for i, row in enumerate(self.store) if row[1] == newtext]
        if overides:
            self.tree.set_cursor(overides[0], self.tree.get_column(1), False)
            return
        
        self.book.rename(newtext)
        self.store[index][1] = newtext
