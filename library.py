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
import logging
from threading import Timer
from datetime import datetime
from gettext import gettext as _
import locale

from sugar.graphics.toolbutton import ToolButton
from sugar.graphics.toggletoolbutton import ToggleToolButton
from sugar.activity.activity import ActivityToolbox
from sugar.graphics.toolcombobox import ToolComboBox
from sugar.graphics.icon import Icon
from sugar.datastore import datastore
import sugar.graphics.style as style
from port.widgets import ToolWidget

import xol
import net
import book
from bookview import BookView
from infoslicer.widgets.Reading_View import Reading_View

logger = logging.getLogger('infoslicer')

class View(gtk.EventBox):
    def sync(self):
        self.wiki.sync()
        self.custom.sync()

    def __init__(self, activity):
        gtk.EventBox.__init__(self)
        self.activity = activity

        self.wiki = BookView(book.wiki,
                _('Wiki'), _('Wiki articles'), False)
        self.custom = BookView(book.custom,
                _('Custom'), _('Custom articles'), True)

        # stubs for empty articles

        def create_stub(icon_name, head_text, tail_text):
            head_label = gtk.Label(head_text)
            head_label_a = gtk.Alignment(0.5, 1, 0, 0)
            head_label_a.add(head_label)
            icon = Icon(icon_name=icon_name,
                    icon_size=gtk.ICON_SIZE_LARGE_TOOLBAR)
            tail_label = gtk.Label(tail_text)
            tail_label_a = gtk.Alignment(0.5, 0, 0, 0)
            tail_label_a.add(tail_label)
            stub = gtk.VBox()
            stub.pack_start(head_label_a)
            stub.pack_start(icon, False)
            stub.pack_start(tail_label_a)
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
        search_box = gtk.HBox()
        self.wikimenu = ToolComboBox(label_text=_('Get article from:'))
        for i in sorted(WIKI.keys()):
            self.wikimenu.combo.append_item(WIKI[i], i)
            if WIKI[i].startswith(wiki_prefix):
                language_order = order
            order = order + 1
        self.wikimenu.combo.set_active(language_order)
        search_box.pack_start(self.wikimenu, False)

        self.searchentry = gtk.Entry()
        self.searchentry.set_size_request(int(gtk.gdk.screen_width() / 4), -1)
        self.searchentry.set_text(_("Article name"))
        self.searchentry.select_region(0, -1)
        self.searchentry.connect('activate', self._search_activate_cb)
        search_box.pack_start(self.searchentry)
        search_box.show_all()

        self.searchbutton = gtk.Button(label=_('Search'))
        self.searchbutton.connect('clicked', self._search_clicked_cb)
        search_box.pack_start(self.searchbutton, False)

        wiki_widget = Reading_View()
        wiki = gtk.Notebook()
        wiki.props.show_border = False
        wiki.props.show_tabs = False
        wiki.append_page(wiki_stub)
        wiki.append_page(wiki_widget)

        self.progress = gtk.Label()
        #self.progress.set_size_request(-1, style.SMALL_ICON_SIZE+4)
        #progress_box = gtk.HBox()
        #progress_box.pack_start(gtk.HSeparator(), False)
        #progress_box.pack_start(self.progress, False)

        wiki_box = gtk.VBox()
        wiki_box.pack_start(search_box, False)
        wiki_box.pack_start(wiki)
        wiki_box.pack_start(self.progress, False)
        wiki_box.set_size_request(gtk.gdk.screen_width()/4*3,
                gtk.gdk.screen_height()/2)

        custom_widget = Reading_View()
        custom = gtk.Notebook()
        custom.props.show_border = False
        custom.props.show_tabs = False
        custom.append_page(custom_stub)
        custom.append_page(custom_widget)
        custom.set_size_request(gtk.gdk.screen_width()/4*3,
                gtk.gdk.screen_height()/2)

        # workspace

        articles_box = gtk.HBox()
        articles_box.pack_start(self.wiki)
        articles_box.pack_start(gtk.VSeparator(), False)
        articles_box.pack_start(wiki_box, False)

        custom_box = gtk.HBox()
        custom_box.pack_start(self.custom)
        custom_box.pack_start(gtk.VSeparator(), False)
        custom_box.pack_start(custom, False)

        workspace = gtk.VBox()
        workspace.pack_start(articles_box, False)
        workspace.pack_start(custom_box, False)
        workspace.show_all()

        self.add(workspace)

        # init components

        book.wiki.connect('article-selected', self._article_selected_cb,
                wiki_widget, [wiki, custom])
        book.wiki.connect('article-deleted', self._article_deleted_cb,
                [wiki, custom])
        book.custom.connect('article-selected', self._article_selected_cb,
                custom_widget, [custom, wiki])
        book.custom.connect('article-deleted', self._article_deleted_cb,
                [custom, wiki])

        self._article_selected_cb(book.wiki, book.wiki.article,
                wiki_widget, [wiki, custom])
        self._article_selected_cb(book.custom, book.custom.article,
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

        if book.wiki.find('%s (from %s)' % (title, wiki))[0]:
            self.activity.notify_alert(
                    _('Exists'),
                    _('"%s" article already exists') % title)
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

        self.publish = ToolButton('filesave',
                tooltip=_('Publish selected articles'))
        self.publish.connect("clicked", self._publish_clicked_cb)
        toolbar.insert(self.publish, -1)


    def _publish_clicked_cb(self, widget):
        xol.publish(self.activity)

WIKI = { _("English Wikipedia")         : "en.wikipedia.org", 
         _("Simple English Wikipedia")  : "simple.wikipedia.org", 
         _("German Wikipedia")          : "de.wikipedia.org",
         _("Spanish Wikipedia")         : "es.wikipedia.org",
         _("French Wikipedia")          : "fr.wikipedia.org" }
