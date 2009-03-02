# Copyright (C) IBM Corporation 2008 
import pygtk
pygtk.require('2.0')
import gtk
from Readonly_Textbox import Readonly_Textbox
import logging

logger = logging.getLogger('infoslicer')
elogger = logging.getLogger('infoslicer::except')

class Reading_View( gtk.VBox ):
    """ 
    Created by Jonathan Mace
    
    This class wraps a Readonly_Textbox in a scrollable window, and adds
    a combobox.  
    The combobox is populated, externally, with the names of
    articles which can be selected.   
    If an article is selected in the combobox, the readonly_textbox will
    be set to display the newly selected article.
    """
     
    def __init__(self):
        gtk.VBox.__init__(self)
        
        self.articlewindow = gtk.ScrolledWindow()
        self.articlewindow.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        self.pack_start(self.articlewindow)
        self.articlewindow.show()
        
        self.textbox = Readonly_Textbox()
        self.articlewindow.add(self.textbox)
        self.textbox.show()
        
    def set_sentence_selection_mode(self):
        self.textbox.set_mode(0)
        
    def set_paragraph_selection_mode(self):
        self.textbox.set_mode(1)
        
    def set_section_selection_mode(self):
        self.textbox.set_mode(2)
        
    def set_full_edit_mode(self):
        self.textbox.set_mode(3)

    def clear_contents(self):
        self.textbox.clear()
        
