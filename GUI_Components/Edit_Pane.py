# Copyright (C) IBM Corporation 2008 
import pygtk
pygtk.require('2.0')
import gtk
from GUI_Components.Pane import Pane
from GUI_Components.Compound_Widgets.Reading_View import Reading_View
from GUI_Components.Compound_Widgets.Editing_View import Editing_View
from GUI_Components.Compound_Widgets.Library_View import Library_View
from Processing.Article.Article import Article
from Processing.IO_Manager import IO_Manager
import logging

logger = logging.getLogger('infoslicer')

class Edit_Pane(Pane):
    """
    Created by Jonathan Mace
    
    See __init__.py for overview of panes.
    
    The Edit Pane gives a side-by-side view of the source article and edit article
    and allows users to drag text selections from the left hand (source) to the right
    hand side (edited version).
    
    The article displayed in the left hand side (source) can be changed by the 
    drop-down menu (implemented in Compound_Widgets.Reading_View)
    
    The toolbar gives options to change the selection type.
    """
    
    def __init__(self):
        Pane.__init__(self)
        self.name = _("Edit")

        """
        Create reading and editing panels
        """
        self.panel = gtk.HBox()
        self.panel.set_homogeneous(True)
        self.panel.show()        
        
        self.readarticle = Reading_View()  
        self.panel.pack_start(self.readarticle)
        self.readarticle.show()
        
        self.editarticle = Editing_View()
        self.panel.pack_start(self.editarticle)
        self.editarticle.show()
        
        self.toolbar = gtk.Toolbar()
        
        self.label = gtk.Label(_("Snap selection to: "))
        self.label.show()
        
        self.labelcontainer = gtk.ToolItem()
        self.labelcontainer.add(self.label)
        self.toolbar.insert(self.labelcontainer, -1)
        self.labelcontainer.show()
        
        """ Snap selection box """
        self.combobox = gtk.combo_box_new_text()
        self.combobox.append_text(_("Nothing"))
        self.combobox.append_text(_("Sentences"))
        self.combobox.append_text(_("Paragraphs"))
        self.combobox.append_text(_("Sections"))
        self.combobox.connect("changed", self.selection_mode_changed, None)
        self.combobox.set_active(1)
        self.combobox.show()
        
        self.combocontainer = gtk.ToolItem()
        self.combocontainer.add(self.combobox)
        self.toolbar.insert(self.combocontainer, -1)
        self.combocontainer.show()
        
    """
    When highlighting text, while editing, different selection snap methods 
    can be used (characters, sentences, paragraphs and sections). Change the selection
    mode based on user request 
    """        
    def selection_mode_changed(self, widget, data):
        current_selection = widget.get_active_text()
        if current_selection == _("Nothing"):
            self.readarticle.set_full_edit_mode()
            self.editarticle.set_full_edit_mode()
        elif current_selection == _("Sentences"):
            self.readarticle.set_sentence_selection_mode()
            self.editarticle.set_sentence_selection_mode()
        elif current_selection == _("Paragraphs"):
            self.readarticle.set_paragraph_selection_mode()
            self.editarticle.set_paragraph_selection_mode()
        elif current_selection == _("Sections"):
            self.readarticle.set_section_selection_mode()
            self.editarticle.set_section_selection_mode()
        #logger.debug(current_selection)
        
    def get_source_article(self):
        return self.readarticle.textbox.get_article()

    """
    Grab source article from IO manager and set up as editing source.
    """
    def set_source_article(self, article):
        # Populate the drop down menu with the articles in the current theme
        article_theme = article.article_theme
        article_title = article.article_title
        if article_title == None:
            article_title = ""
        """ Grab media wiki pages from default wikipedia theme """
        titles = IO_Manager().get_pages_in_theme(_("Wikipedia Articles"))
        self.readarticle.articlemenu.get_model().clear()
        """ Check user has downloaded some source articles """
        if titles != []:
            self.readarticle.articlemenu.append_text(_("Select a source article from this menu"))
            if article_title == "":
                buf = article.getBuffer()
                start = buf.get_start_iter()
                end = buf.get_end_iter()
                buf.delete(start, end)
                buf.insert(buf.get_start_iter(), _("You can choose a Wikipedia article to copy from by selecting it from the drop-down menu above."))
                buf.insert(buf.get_end_iter(), _("If you want to download more articles from Wikipedia, you can do this in the Library tab."))
        else:
            buf = article.getBuffer()
            buf.insert(buf.get_start_iter(), _("You have not downloaded any articles from Wikipedia. You can download new articles in the Library tab."))
       
        i = 0
        selectionindex = 0
        for title in titles:
            self.readarticle.articlemenu.append_text(title)
            i = i + 1
            if title == article_title:
                selectionindex = i
                
        self.readarticle.articlemenu.set_active(selectionindex)
        
        # Set the read article as appropriate.
        self.readarticle.textbox.set_article(article)
        
    
    def get_working_article(self):
        article = self.editarticle.textbox.get_article()
        return article
    
    def set_working_article(self, article):
        self.editarticle.articletitle.set_markup("<span size='medium'><b> %s </b>  %s  \n<b> %s </b>  %s</span>" % \
            (_("Theme:"), article.article_theme, _("Article:"), article.article_title))
        self.editarticle.textbox.set_article(article)
        self.editarticle.article_theme = _("Wikipedia Articles")
        
    
