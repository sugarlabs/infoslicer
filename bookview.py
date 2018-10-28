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

import os
from gi.repository import Gtk
import logging
from gi.repository import GObject
from gi.repository import GLib
from gettext import gettext as _

from sugar3.graphics.toolbutton import ToolButton
from sugar3.activity.activity import get_bundle_path, get_activity_root
from sugar3.graphics.style import *

logger = logging.getLogger('infoslicer')

PUBLISH  = 0
TITLE    = 1

class BookView(Gtk.VBox):
    def sync(self):
        if not self._changing:
            return
        GLib.source_remove(self._changing)
        index, column = self.tree.get_cursor()
        self._cursor_changed(index)

    def __init__(self, book, name, tooltip, custom):
        GObject.GObject.__init__(self)
        self.book = book
        self._changing = None
        self._check = None

        title = Gtk.Toolbar()

        # title checkbox

        if custom:
            self._check = Gtk.CheckButton()
            self._check.props.can_focus = False
            self._check.props.tooltip_text = \
                    _('Articles are ready to be published')
            self._check.connect('toggled', self._check_toggled_cb)
            check_box = Gtk.HBox()
            check_box.set_size_request(50, -1)
            check_box.pack_start(self._check, True, False, 0)
            tool_item = Gtk.ToolItem()
            tool_item.add(check_box)
            tool_item.show()
            title.insert(tool_item, -1)
        else:
            tool_item = Gtk.ToolItem()
            tool_item.add(Gtk.Label(label='  '))
            tool_item.show()
            title.insert(tool_item, -1)

        # title caption

        caption_label = Gtk.Label(label=name)
        caption_label.props.tooltip_text = tooltip
        caption_label.modify_fg(Gtk.StateType.NORMAL, COLOR_WHITE.get_gdk_color())
        caption_box = Gtk.HBox()
        caption_box.pack_start(caption_label, False, False, 0)
        caption = Gtk.EventBox()
        caption.add(caption_box)
        caption.modify_bg(Gtk.StateType.NORMAL, COLOR_TOOLBAR_GREY.get_gdk_color())

        tool_item = Gtk.ToolItem()
        tool_item.add(caption)
        tool_item.show()
        title.insert(tool_item, -1)

        separator = Gtk.SeparatorToolItem()
        separator.props.draw = False
        separator.set_expand(True)
        title.insert(separator, -1)

        # create article button

        if custom:
            create = ToolButton('add')
            create.set_tooltip(_('Create new article'))
            create.connect('clicked', self._create_cb)
            title.insert(create, -1)
        else:
            logger.debug('BookView(%s): listen for new articles' % name)
            self.book.connect('article-added', self._article_added_cb)

        # delete article button

        delete = ToolButton('edit-delete')
        delete.set_tooltip(_('Delete current article'))
        delete.connect('clicked', self._delete_cb)
        title.insert(delete, -1)

        # move buttons

        downward = ToolButton('down')
        downward.set_tooltip(_('Move article downward'))
        downward.connect('clicked', self._swap_cb, +1)
        title.insert(downward, -1)

        upward = ToolButton('up')
        upward.set_tooltip(_('Move article upward'))
        upward.connect('clicked', self._swap_cb, -1)
        title.insert(upward, -1)

        # tree

        self.store = Gtk.ListStore(bool, str)
        self.tree = Gtk.TreeView(self.store)
        self.tree.props.headers_visible = False
        self.tree.connect('cursor-changed', self._cursor_changed_cb)

        cell = Gtk.CellRendererToggle()
        cell.connect('toggled', self._cell_toggled_cb)
        cell.props.activatable = True

        # FIXME: insert_column_with_attributes does not exist on pygobject
        # column = self.tree.insert_column_with_attributes(0, '', cell, active=0)

        logging.debug('TODO: this is a workaround due '
                      'https://bugzilla.gnome.org/show_bug.cgi?id=679415')

        column = Gtk.TreeViewColumn('Wiki', cell)
        column.props.sizing = Gtk.TreeViewColumnSizing.FIXED
        column.props.fixed_width = 50
        column.props.visible = custom

        self.tree.insert_column(column, 0)

        cell = Gtk.CellRendererText()
        cell.connect('edited', self._cell_edited_cb)
        cell.props.editable = True

        # FIXME: insert_column_with_attributes does not exist on pygobject
        # self.tree.insert_column_with_attributes(1, '', cell, text=1)

        logging.debug('TODO: this is a workaround due '
                      'https://bugzilla.gnome.org/show_bug.cgi?id=679415')

        column = Gtk.TreeViewColumn('Custom', cell, text=1)
        self.tree.insert_column(column, 1)

        for i in self.book.index:
            self.store.append((i['ready'], i['title']))

        # scrolled tree

        tree_scroll = Gtk.ScrolledWindow()
        tree_scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        tree_scroll.add(self.tree)

        self.pack_start(title, False, False, 0)
        self.pack_start(tree_scroll, True, True, 0)

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
            GLib.source_remove(self._changing)
            self._changing = None

        name = find_name(self.store, _('New article'), 0)
        self.book.props.article = name
        self.store.append((False, name))
        self.tree.set_cursor(len(self.store)-1, self.tree.get_column(1), True)
        self._update_check(self.store[-1][PUBLISH])

    def _delete_cb(self, widget):
        path, focus_column = self.tree.get_cursor()

        if not path:
            return

        if self._changing:
            GLib.source_remove(self._changing)
            self._changing = None

        index = path.get_indices()[0]

        self.book.remove(self.store[index][TITLE])
        self.store.remove(self.tree.props.model.get_iter(index))

        if len(self.store):
            if index >= len(self.store):
                index -= 1
            self.tree.set_cursor(index, self.tree.get_column(1), False)
            self._update_check(self.store[index][PUBLISH])

    def _swap_cb(self, widget, delta):
        path, focus_column = self.tree.get_cursor()

        if not path:
            return

        old_index = path.get_indices()[0]
        new_index = old_index + delta

        if new_index < 0:
            new_index = len(self.store) - 1
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
            GLib.source_remove(self._changing)

        index, column = self.tree.get_cursor()

        if index != None:
            self._changing = GLib.timeout_add(500, self._cursor_changed,
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
