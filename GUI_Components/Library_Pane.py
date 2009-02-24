# Copyright (C) IBM Corporation 2008 
import pygtk
pygtk.require('2.0')
import gtk
from GUI_Components.Pane import Pane
from GUI_Components.Compound_Widgets.Library_View import Library_View
from GUI_Components.Compound_Widgets.Reading_View import Reading_View
from Processing.IO_Manager import *
from gettext import gettext as _

class Library_Pane(Pane):
    """ 
    Created by Jonathan Mace
    
    The Library Pane sets up a Library View and includes a toolbar which has
    a text entry used for getting articles from Wikipedia.

    The Library View contains the entire sum of articles downloaded from Wikipedia. 
    These articles can then be added to themes, editing and bundled into content packages
    """
    
    def __init__(self):
        Pane.__init__(self)
        self.wikis = {"English Wikipedia" : "en.wikipedia.org", 
                      "Simple English Wikipedia" : "simple.wikipedia.org", 
                      "German Wikipedia": "de.wikipedia.org"}
        self.toolbar = gtk.Toolbar()
        
        
        self.panel  = gtk.HBox()
        self.panel.set_homogeneous(True)
        self.panel.show()
        
        self.librarypanel = Library_View()
        self.panel.pack_start(self.librarypanel)
        self.librarypanel.show()
        
        statuslabel = self.librarypanel.statusbar
        
        # Set up the components of the toolbar
        searchlabelitem = gtk.ToolItem()
        self.toolbar.insert(searchlabelitem, -1)
        searchlabelitem.show()
        
        """
        User search dialog 
        """
        searchlabel = gtk.Label(_("Get article from "))
        searchlabelitem.add(searchlabel)
        searchlabel.show()
        
        wikitoolitem = gtk.ToolItem()
        self.toolbar.insert(wikitoolitem, -1)
        wikitoolitem.show()
        
        wikimenu = gtk.combo_box_new_text()
        keys = self.wikis.keys()
        keys.sort()
        for wiki in keys:
            wikimenu.append_text(wiki)
        wikimenu.set_active(0)
        wikitoolitem.add(wikimenu)
        wikimenu.show()
        
        searchentryitem = gtk.ToolItem()
        self.toolbar.insert(searchentryitem, -1)
        searchentryitem.show()
        
        searchentry = gtk.Entry()
        searchentry.set_text(_("Article name"))
        searchentry.connect("activate", self.click_search_button, None)
        searchentryitem.add(searchentry)
        searchentry.show()
        
        self.searchbutton = gtk.ToolButton(gtk.STOCK_FIND)
        self.searchbutton.connect("clicked", self.librarypanel.commence_retrieval, searchentry, statuslabel, wikimenu, self.wikis)
        self.toolbar.insert(self.searchbutton, -1)
        self.searchbutton.show()
        
        # Add some blank space
        blanklabel = gtk.Label("     ")
        blanklabel.show()
        
        blankitem = gtk.ToolItem()
        blankitem.add(blanklabel)
        self.toolbar.insert(blankitem, -1)
        blankitem.show()
        
        
        self.toolbar = self.toolbar
        self.name = _("Library")

    def click_search_button(self, widget, data):
        self.searchbutton.emit("clicked")
    
    def get_source_article(self):
        return self.librarypanel.get_source()
    
    def set_source_article(self, article):
        self.librarypanel.set_source(article)   
    
    def get_working_article(self):
        return self.librarypanel.get_working()
    
    def set_working_article(self, article):
        self.librarypanel.set_working(article)
            
