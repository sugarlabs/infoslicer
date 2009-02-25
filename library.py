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
from sugar.graphics.toolcombobox import ToolComboBox

from GUI_Components.Compound_Widgets.Library_View import Library_View
from GUI_Components.Compound_Widgets.toolbar import WidgetItem

class View(gtk.EventBox): #Library_View):
    def __init__(self):
        gtk.EventBox.__init__(self)
        #Library_View.__init__(self)

        """

        def get_source_article(self):
            return self.librarypanel.get_source()
        
        def set_source_article(self, article):
            self.librarypanel.set_source(article)   
        
        def get_working_article(self):
            return self.librarypanel.get_working()
        
        def set_working_article(self, article):
            self.librarypanel.set_working(article)


        # Set up dummy library if appropriate
        IO_Manager().install_library()

        themes = IO_Manager().get_themes()
        if "Wikipedia Articles" in themes:
            i = themes.index("Wikipedia Articles")
            del themes[i]
            
        wikiarticles = IO_Manager().get_pages_in_theme("Wikipedia Articles")
        for theme in themes:
            articles = IO_Manager().get_pages_in_theme(theme)
            for article in articles:
                if ignore == True:
                    break
                for wikiarticle in wikiarticles:
                    if article in wikiarticle:
                        self.source = IO_Manager().load_article(wikiarticle, "Wikipedia Articles")
                        self.working = IO_Manager().load_article(article, theme) 
                        logger.debug("loading source %s from %s" %
                                (wikiarticle, "Wikipedia Articles"))
                        logger.debug("loading edit %s from %s" %
                                (article, theme))
                        ignore = True
        """

class Toolbar(gtk.Toolbar):
    def __init__(self, library):
        gtk.Toolbar.__init__(self)
        self.library = library
        return

        wikimenu = ToolComboBox(label_text=_('Get article from:'))
        wikimenu.combo.connect('changed', self._wikimenu_changed_cb)
        for i in sorted(WIKI.keys()):
            wikimenu.combo.append_item(WIKI[i], i)
        self.insert(wikimenu, -1)
        wikimenu.show()

        searchentry = gtk.Entry()
        searchentry.set_size_request(int(gtk.gdk.screen_width() / 4), -1)
        searchentry.set_text(_("Article name"))
        searchentry.connect('changed', self._search_activate_cb)
        searchentry_item = WidgetItem(searchentry)
        self.insert(searchentry_item, -1)
        searchentry_item.show()

        self.searchbutton = ToolButton('search', tooltip=_('Find article'))
        self.searchbutton.connect("clicked", self.library.commence_retrieval,
                searchentry, self.library.statusbar, wikimenu, WIKI)
        self.insert(self.searchbutton, -1)
        self.searchbutton.show()

        separator = gtk.SeparatorToolItem()
        self.insert(separator, -1)
        separator.show()

        new = ToolButton('add', tooltip=_('New article'))
        new.connect("clicked", self._new_clicked_cb)
        self.insert(new, -1)
        new.show()

        erase = ToolButton('edit-delete', tooltip=_('Delete selected articles'))
        erase.connect("clicked", self._erase_clicked_cb)
        self.insert(erase, -1)
        erase.show()

        separator = gtk.SeparatorToolItem()
        self.insert(separator, -1)
        separator.show()

        publish = ToolButton('filesave', tooltip=_('Publish selected articles'))
        publish.connect("clicked", self._publish_clicked_cb)
        self.insert(publish, -1)
        publish.show()

    def _publish_clicked_cb(self):
        pass

    def _erase_clicked_cb(self):
        pass

    def _new_clicked_cb(self):
        pass

    def _search_activate_cb(self, widget):
        self.searchbutton.emit("clicked")

    def _wikimenu_changed_cb(self, widget, data):
        self.searchbutton.emit("clicked")

WIKI = { _("English Wikipedia")         : "en.wikipedia.org", 
         _("Simple English Wikipedia")  : "simple.wikipedia.org", 
         _("German Wikipedia")          : "de.wikipedia.org" }
