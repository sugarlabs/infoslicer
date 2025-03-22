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
import logging
from threading import Timer
from gettext import gettext as _
import locale

from sugar3.graphics.toolbutton import ToolButton
from sugar3.graphics.toggletoolbutton import ToggleToolButton
from sugar3.graphics.toolcombobox import ToolComboBox
from sugar3.graphics.icon import Icon
from sugar3.datastore import datastore
from sugar3.graphics.alert import Alert
import sugar3.graphics.style as style

import xol
import net
import book
from bookview import BookView
from infoslicer.widgets.Reading_View import Reading_View

logger = logging.getLogger('infoslicer')

class View(Gtk.EventBox):
    def sync(self):
        self.wiki.sync()
        self.custom.sync()

    def __init__(self, activity):
        logger.info("View initialized with activity: %s", activity)

        GObject.GObject.__init__(self)
        self.activity = activity

        self.wiki = BookView(book.WIKI,
                _('Wiki'), _('Wiki articles'), False)
        self.custom = BookView(book.CUSTOM,
                _('Custom'), _('Custom articles'), True)

        # stubs for empty articles

        def create_stub(icon_name, head_text, tail_text):
            head_label = Gtk.Label(label=head_text)
            head_label_a = Gtk.Alignment.new(0.5, 1, 0, 0)
            head_label_a.add(head_label)
            icon = Icon(icon_name=icon_name,
                    pixel_size=Gtk.IconSize.LARGE_TOOLBAR)
            tail_label = Gtk.Label(label=tail_text)
            tail_label_a = Gtk.Alignment.new(0.5, 0, 0, 0)
            tail_label_a.add(tail_label)
            stub = Gtk.VBox()
            stub.pack_start(head_label_a, True, True, 0)
            stub.pack_start(icon, False, False, 0)
            stub.pack_start(tail_label_a, True, True, 0)
            return stub

        wiki_stub = create_stub('white-search',
                _('To download Wiki article\ntype "Article name" and click'),
                _('button on the top "Library" panel'))
        custom_stub = create_stub('add',
                _('To create custom article click'),
                _('button on the left "Custom" panel'))

        # articles viewers
        lang_code = locale.getdefaultlocale()[0] or 'en_US'
        wiki_prefix = lang_code[0:2] + '.'
        language_order = 0
        order = 0
        search_box = Gtk.HBox()
        self.wikimenu = ToolComboBox(label_text=_('Get article from:'))
        for i in sorted(WIKI.keys()):
            self.wikimenu.combo.append_item(WIKI[i], i)
            if WIKI[i].startswith(wiki_prefix):
                language_order = order
            order = order + 1
        self.wikimenu.combo.set_active(language_order)
        search_box.pack_start(self.wikimenu, False, False, 0)

        self.searchentry = Gtk.Entry()
        self.searchentry.set_size_request(int(Gdk.Screen.width() / 6), -1)
        self.searchentry.set_text(_("Article name"))
        self.searchentry.select_region(0, -1)
        self.searchentry.connect('activate', self._search_activate_cb)
        search_box.pack_start(self.searchentry, True, True, 0)
        search_box.show_all()

        self.searchbutton = Gtk.Button(label=_('Search'))
        self.searchbutton.connect('clicked', self._search_clicked_cb)
        search_box.pack_start(self.searchbutton, False, False, 0)

        wiki_widget = Reading_View()
        wiki = Gtk.Notebook()
        wiki.props.show_border = False
        wiki.props.show_tabs = False
        wiki.append_page(wiki_stub, None)
        wiki.append_page(wiki_widget, None)

        self.progress = Gtk.Label()

        wiki_box = Gtk.VBox()
        wiki_box.pack_start(search_box, False, False, 0)
        wiki_box.pack_start(wiki, True, True, 0)
        wiki_box.pack_start(self.progress, False, False, 0)
        logging.debug(int(Gdk.Screen.width() * 3 / 4.))
        wiki_box.set_size_request(int(Gdk.Screen.width() * 3 / 4.),
                                  int((Gdk.Screen.height() - \
                                           style.GRID_CELL_SIZE) / 2))

        custom_widget = Reading_View()
        custom = Gtk.Notebook()
        custom.props.show_border = False
        custom.props.show_tabs = False
        custom.append_page(custom_stub, None)
        custom.append_page(custom_widget, None)
        # custom.set_size_request(Gdk.Screen.width()/4*3,
        #         Gdk.Screen.height()/2 - 55)
        custom.set_size_request(int(Gdk.Screen.width() * 3 / 4.),
                                  int((Gdk.Screen.height() - \
                                           style.GRID_CELL_SIZE) / 2))

        # workspace
        articles_box = Gtk.HBox()
        articles_box.pack_start(self.wiki, True, True, 0)
        articles_box.pack_start(Gtk.VSeparator(), False, False, 0)
        articles_box.pack_start(wiki_box, False, False, 0)

        custom_box = Gtk.HBox()
        custom_box.pack_start(self.custom, True, True, 0)
        custom_box.pack_start(Gtk.VSeparator(), False, False, 0)
        custom_box.pack_start(custom, False, False, 0)

        workspace = Gtk.VBox()
        workspace.pack_start(articles_box, False, False, 0)
        workspace.pack_start(custom_box, False, False, 0)
        workspace.show_all()

        self.add(workspace)

        # init components

        book.WIKI.connect('article-selected', self._article_selected_cb,
                wiki_widget, [wiki, custom])
        book.WIKI.connect('article-deleted', self._article_deleted_cb,
                [wiki, custom])
        book.CUSTOM.connect('article-selected', self._article_selected_cb,
                custom_widget, [custom, wiki])
        book.CUSTOM.connect('article-deleted', self._article_deleted_cb,
                [custom, wiki])

        self._article_selected_cb(book.WIKI, book.WIKI.article,
                wiki_widget, [wiki, custom])
        self._article_selected_cb(book.CUSTOM, book.CUSTOM.article,
                custom_widget, [custom, wiki])

        self.connect('map', self._map_cb)

    def _article_selected_cb(self, abook, article, article_widget, notebooks):
        if not article:
            return

        if not abook.index:
            notebooks[0].set_current_page(0)
            return

        if notebooks[0].get_current_page() in (-1, 0):
            notebooks[0].set_current_page(1)
            if notebooks[1].get_current_page() == 1:
                self.activity.set_edit_sensitive(True)

        article_widget.textbox.set_article(article)

    def _article_deleted_cb(self, abook, article, notebooks):
        if not abook.index:
            notebooks[0].set_current_page(0)
            self.activity.set_edit_sensitive(False)

    def _search_activate_cb(self, widget):
        self.searchbutton.emit("clicked")

    def _search_clicked_cb(self, widget):
        title = self.searchentry.get_text()
        wiki = self.wikimenu.combo.props.value

        if not title:
            return

        if book.WIKI.find('%s (from %s)' % (title, wiki))[0]:
            alert = Alert()
            alert.props.title = _('Exists')
            alert.props.msg = _('"%s" article already exists' % title)
            alert.show()
        else:
            Timer(0, self._download, [title, wiki]).start()

    def _download(self, title, wiki):
        net.download_wiki_article(title, wiki, self.progress)
        Timer(10, self._clear_progress).start()

    def _clear_progress(self):
        self.progress.set_label('')

    def _map_cb(self, widget):
        self.searchentry.grab_focus()


class ToolbarBuilder():
    def __init__(self, library, toolbar):
        self.library = library
        self.activity = library.activity

        self.publish = ToolButton('export-to-journal',
                tooltip=_('Publish selected articles'))
        self.publish.connect("clicked", self._publish_clicked_cb)

        if hasattr(toolbar, 'insert'):  # Add button to the main toolbar...
            toolbar.insert(self.publish, -1)
        else:  # ...or a secondary toolbar.
            toolbar.props.page.insert(self.publish, -1)

    def _publish_clicked_cb(self, widget):
        xol.publish(self.activity)

WIKI = { _('English Wikipedia')         : 'en.wikipedia.org',
         _('Simple English Wikipedia')  : 'simple.wikipedia.org',
         _('French Wikipedia')          : 'fr.wikipedia.org',
         _('German Wikipedia')          : 'de.wikipedia.org',
         _('Polish Wikipedia')         : 'pl.wikipedia.org',
         _('Spanish Wikipedia')         : 'es.wikipedia.org'}
