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
from port.widgets import ToolWidget, ToolButton

logger = logging.getLogger('infoslicer')

PUBLISH  = 0
TITLE    = 1

class BookView(gtk.VBox):
    def sync(self):
        if not self._changing:
            return
        gobject.source_remove(self._changing)
        index, column = self.tree.get_cursor()
        self._cursor_changed(index)

    def __init__(self, book, name, tooltip, custom):
        gtk.VBox.__init__(self)
        self.book = book
        self._changing = None
        self._check = None

        title = gtk.Toolbar()

        # title checkbox

        if custom:
            self._check = gtk.CheckButton()
            self._check.props.can_focus = False
            self._check.props.tooltip_text = \
                    _('Articles are ready to be published')
            self._check.connect('toggled', self._check_toggled_cb)
            check_box = gtk.HBox()
            check_box.set_size_request(50, -1)
            check_box.pack_start(self._check, True, False)
            title.insert(ToolWidget(check_box), -1)
        else:
            title.insert(ToolWidget(gtk.Label('  ')), -1)

        # title caption

        caption_label = gtk.Label(name)
        caption_label.props.tooltip_text = tooltip
        caption_label.modify_fg(gtk.STATE_NORMAL, COLOR_WHITE.get_gdk_color())
        caption_box = gtk.HBox()
        caption_box.pack_start(caption_label, False)
        caption = gtk.EventBox()
        caption.add(caption_box)
        caption.modify_bg(gtk.STATE_NORMAL, COLOR_TOOLBAR_GREY.get_gdk_color())
        title.insert(ToolWidget(caption), -1)

        separator = gtk.SeparatorToolItem()
        separator.props.draw = False
        separator.set_expand(True)
        title.insert(separator, -1)

        # create article button

        if custom:
            create = ToolButton('add',
                    padding=0,
                    tooltip=_('Create new article'))
            create.connect('clicked', self._create_cb)
            title.insert(create, -1)
        else:
            logger.debug('BookView(%s): listen for new articles' % name)
            self.book.connect('article-added', self._article_added_cb)

        # delete article button

        delete = ToolButton('edit-delete',
                padding=0,
                tooltip=_('Delete current article'))
        delete.connect('clicked', self._delete_cb)
        title.insert(delete, -1)

        # move buttons

        downward = ToolButton('down',
                padding=0,
                tooltip=_('Move article downward'))
        downward.connect('clicked', self._swap_cb, +1)
        title.insert(downward, -1)
        upward = ToolButton('up',
                padding=0,
                tooltip=_('Move article upward'))
        upward.connect('clicked', self._swap_cb, -1)
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
        column.props.visible = custom

        cell = gtk.CellRendererText()
        cell.connect('edited', self._cell_edited_cb)
        cell.props.editable = True
        self.tree.insert_column_with_attributes(1, '', cell, text=1)

        for i in self.book.index:
            self.store.append((i['ready'], i['title']))

        # scrolled tree

        tree_scroll = gtk.ScrolledWindow()
        tree_scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        tree_scroll.add(self.tree)

        self.pack_start(title, False)
        self.pack_start(tree_scroll)

        if len(self.store):
            self.tree.set_cursor(0, self.tree.get_column(1), False)
            if custom:
                self._update_check(self.store[0][PUBLISH])

        self.show_all()

    def _article_added_cb(self, book, article):
        logger.debug('_article_added_cb: new article %s' % article)

        self.book.props.article = article
        self.store.append((False, article))

    def _create_cb(self, widget):
        def find_name(list, prefix, uniq):
            name = uniq == 0 and prefix or ('%s %d' % (prefix, uniq))
            if not [i for i in list if i[TITLE] == name]:
                return name
            return find_name(list, prefix, uniq+1)

        if self._changing:
            gobject.source_remove(self._changing)
            self._changing = None

        name = find_name(self.store, _('New article'), 0)
        self.book.props.article = name
        self.store.append((False, name))
        self.tree.set_cursor(len(self.store)-1, self.tree.get_column(1), True)
        self._update_check(self.store[-1][PUBLISH])

    def _delete_cb(self, widget):
        index, column = self.tree.get_cursor()
        if not index:
            return
        index = index[0]

        if self._changing:
            gobject.source_remove(self._changing)
            self._changing = None

        self.book.remove(self.store[index][TITLE])
        self.store.remove(self.tree.props.model.get_iter(index))

        if len(self.store):
            if index >= len(self.store):
                index -= 1
            self.tree.set_cursor(index, self.tree.get_column(1), False)
            self._update_check(self.store[index][PUBLISH])

    def _swap_cb(self, widget, delta):
        old_index, column = self.tree.get_cursor()
        if not old_index:
            return

        old_index = old_index[0]
        new_index = old_index + delta

        if new_index < 0:
            new_index = len(self.store)-1
        elif new_index >= len(self.store):
            new_index = 0

        self.book.index[old_index], self.book.index[new_index] = \
                self.book.index[new_index], self.book.index[old_index]
        self.store.swap(self.tree.props.model.get_iter(old_index),
                self.tree.props.model.get_iter(new_index))

    def _check_toggled_cb(self, widget):
        for i, entry in enumerate(self.store):
            entry[PUBLISH] = widget.props.active
            self.book.index[i]['ready'] = widget.props.active
        self._check.props.inconsistent = False

    def _update_check(self, value):
        if not self._check:
            return

        for i in self.store:
            if i[PUBLISH] != value:
                self._check.props.inconsistent = True
                return
        self._check.props.inconsistent = False
        self._check.props.active = value

    def _cell_toggled_cb(self, cell, index):
        value = not self.store[index][PUBLISH]
        self.store[index][PUBLISH] = value
        self.book.index[int(index)]['ready'] = value
        self._update_check(value)

    def _cursor_changed_cb(self, widget):
        if self._changing:
            gobject.source_remove(self._changing)

        index, column = self.tree.get_cursor()

        if index != None:
            self._changing = gobject.timeout_add(500, self._cursor_changed,
                    index)

    def _cursor_changed(self, index):
        self.book.props.article = self.store[index][TITLE]
        self._changing = None
        return False

    def _cell_edited_cb(self, cell, index, newtext):
        logger.debug('_cell_edited_cb(%s, %s)' % (index, newtext))

        # Disallowed chars are < > and &
        if newtext == "" or newtext.isspace() or '&' in newtext \
                or '<' in newtext or '>' in newtext:
            return

        # If there is already an article with the new name in the theme,
        # then we ignore the name change and highlight the existing article
        overides = [i for i, row in enumerate(self.store)
                if row[TITLE] == newtext]
        if overides:
            self.tree.set_cursor(overides[0], self.tree.get_column(1), False)
            return

        self.book.props.article.article_title = newtext
        self.store[index][TITLE] = newtext
