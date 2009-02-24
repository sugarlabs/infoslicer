# Copyright (C) IBM Corporation 2008 
import pygtk
pygtk.require('2.0')
import gtk
from GUI_Components.Pane import Pane
from GUI_Components.Compound_Widgets.Editing_View import Editing_View
from gettext import gettext as _

class Format_Pane(Pane):
    """
    Created by Jonathan Mace
    
    See __init__.py for overview of panes.
    
    The Format Pane shows only the current edit article.
    Users can apply formatting such as bold, underline etc.
    Formatting has currently not been implemented.  Dummy buttons are on the toolbar.
    """
    
    def __init__(self):
        Pane.__init__(self)
        self.name = _("Format")
        
        self.panel = Editing_View()
        self.panel.show()
        
        self.toolbar = gtk.Toolbar()
        
        """
        Snapping has been turned off in the Editable Textbox, so we no longer
        make use of snapping.  This has been left in case we turn it back on.
        
        self.label = gtk.Label("Snap selection to: ")
        self.label.show()
        
        self.labelcontainer = gtk.ToolItem()
        self.labelcontainer.add(self.label)
        self.toolbar.insert(self.labelcontainer, -1)
        self.labelcontainer.show()
        
        
        self.combobox = gtk.combo_box_new_text()
        self.combobox.append_text("Nothing")
        self.combobox.append_text("Sentences")
        self.combobox.append_text("Paragraphs")
        self.combobox.append_text("Sections")
        self.combobox.connect("changed", self.selection_mode_changed, None)
        self.combobox.set_active(1)
        self.combobox.show()
        
        
        self.combocontainer = gtk.ToolItem()
        self.combocontainer.add(self.combobox)
        self.toolbar.insert(self.combocontainer, -1)
        self.combocontainer.show()
        """
        
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
    User wants to change the default snap selection method 
    """
    def selection_mode_changed(self, widget, data):
        current_selection = widget.get_active_text()
        if current_selection == _("Nothing"):
            self.panel.set_full_edit_mode()
        elif current_selection == _("Sentences"):
            self.panel.set_sentence_selection_mode()
        elif current_selection == _("Paragraphs"):
            self.panel.set_paragraph_selection_mode()
        elif current_selection == _("Sections"):
            self.panel.set_section_selection_mode()
            
    def get_source_article(self):
        return self.source
    
    def set_source_article(self, article):
        self.source = article
        
    def get_working_article(self):
        article = self.panel.textbox.get_article()
        return article
    
    def set_working_article(self, article):
        self.panel.articletitle.set_markup("<span size='medium'><b>" + _("Theme:") + "</b>  %s   \n<b>" + _("Article:") + "</b>  %s</span>"%(article.article_theme, article.article_title))
        self.panel.textbox.set_article(article)      
