# Copyright (C) IBM Corporation 2008 

import pygtk
pygtk.require('2.0')
import gtk
from GUI_Components.Pane import Pane
from GUI_Components.Compound_Widgets.Publish_View import Publish_View
from Processing.IO_Manager import *
from gettext import gettext as _

"""
This pane is used when the user decides to package up articles in themes for distribution
"""
class Publish_Pane(Pane):
    
    def __init__(self):
        Pane.__init__(self)
        self.toolbar = gtk.Toolbar()

        self.name = _("Publish")  
        
        self.panel = Publish_View()
        self.panel.show()
                
        self.toolbar = gtk.Toolbar()
    
    def get_source_article(self):
        return self.source
    
    def set_source_article(self, article):
        self.source = article

    def get_working_article(self):
        return self.working
    
    def set_working_article(self, article):        
        theme = article.article_theme
        title = article.article_title
        if theme != None and title != None:
            IO_Manager().save_article(article)   
        self.working = article
        self.panel.populate_themes()
        self.panel.export_message.set_text(_('Select the theme you want, choose the articles you wish to include in the package and click "Publish".'))
