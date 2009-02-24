# Copyright (C) IBM Corporation 2008 
import pygtk
pygtk.require('2.0')
import gtk
from GUI_Components.Compound_Widgets.Base_Widgets.Readonly_Textbox import Readonly_Textbox
from Processing.IO_Manager import IO_Manager
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
    The articles are loaded using IO_Manager
    """
     
    def __init__(self):
        gtk.VBox.__init__(self)
        
        self.articlemenu = gtk.combo_box_new_text()
        self.articlemenu.connect("changed", self.source_selected, None)
        self.pack_start(self.articlemenu, False, False, 1)
        self.articlemenu.show()
        
        self.articlewindow = gtk.ScrolledWindow()
        self.articlewindow.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        self.pack_start(self.articlewindow)
        self.articlewindow.show()
        
        self.textbox = Readonly_Textbox()
        self.articlewindow.add(self.textbox)
        self.textbox.show()
        
    def source_selected(self, combo, data):
        title = combo.get_active_text()
        if title == "Select a source article from this menu" or title == None:
            return
        if self.textbox.get_article() == None or self.textbox.get_article().article_title == title:
            return
        if combo.get_active != 0:
            model = combo.get_model()
            firstiter = model.get_iter_first()
            firstvalue = model.get_value(firstiter, 0)
            logger.debug(firstvalue)
            if firstvalue == "Select a source article from this menu":
                combo.remove_text(0)
        
        if self.textbox.get_article() != None:
            theme = "Wikipedia Articles"
            try:
                newarticle = IO_Manager().load_article(title, theme)
                self.textbox.set_article(newarticle)
            except Exception, e:
                elogger.debug('source_selected: %s' % e)
        
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
        
