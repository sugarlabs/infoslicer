# Copyright (C) IBM Corporation 2008 

import pygtk
pygtk.require('2.0')
import gtk

class Pane:
    """
    An instance of the Pane class has a panel which is the main view,
    a toolbar which interacts with the panel,
    and methods for getting and setting the source and working articles.
    
    """
    
    def __init__(self):
        # Pane instances have a panel, which is the main view of the pane
        self.panel = gtk.Label()
        
        # Pane instances have a toolbar
        self.toolbar = gtk.Toolbar()
        
    def get_working_article(self):
        return self.working
    
    def set_working_article(self, article):
        self.working = article
    
    def get_source_article(self):
        return self.source
    
    def set_source_article(self, article):
        self.source = article