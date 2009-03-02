# Copyright (C) IBM Corporation 2008 
import pygtk
pygtk.require('2.0')
import gtk
from gettext import gettext as _

from Editing_View import Editing_View

class Format_Pane(Editing_View):
    """
    Created by Jonathan Mace
    
    See __init__.py for overview of panes.
    
    The Format Pane shows only the current edit article.
    Users can apply formatting such as bold, underline etc.
    Formatting has currently not been implemented.  Dummy buttons are on the toolbar.
    """
    
    def __init__(self):
        Editing_View.__init__(self)
        self.toolitems = []
        
        """
        self.combocontainer = gtk.ToolItem()
        self.combocontainer.add(self.combobox)
        self.toolbar.insert(self.combocontainer, -1)
        self.combocontainer.show()
        
        self.boldbutton = gtk.ToolButton(gtk.STOCK_BOLD)
        self.boldbutton.set_expand(False)
        self.toolbar.insert(self.boldbutton, -1)
        self.boldbutton.show()
        
        self.italicbutton = gtk.ToolButton(gtk.STOCK_ITALIC)
        self.italicbutton.set_expand(False)
        self.toolbar.insert(self.italicbutton, -1)
        self.italicbutton.show()
        
        self.underlinebutton = gtk.ToolButton(gtk.STOCK_UNDERLINE)
        self.underlinebutton.set_expand(False)
        self.toolbar.insert(self.underlinebutton, -1)
        self.underlinebutton.show()
        """

    def set_source_article(self, article):
        self.source = article
        
    def set_working_article(self, article):
        self.articletitle.set_markup(
                "<span size='medium'><b> %s </b>  %s</span>" % \
                (_("Article:"), article.article_title))
        if self.textbox.get_article() != article:
            self.textbox.set_article(article)      
