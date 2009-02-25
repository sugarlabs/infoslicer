# Copyright (C) IBM Corporation 2008 
import pygtk
pygtk.require('2.0')
import gtk
import logging
from gettext import gettext as _

from sugar.graphics.toolcombobox import ToolComboBox

from GUI_Components.Compound_Widgets.Reading_View import Reading_View
from GUI_Components.Compound_Widgets.Editing_View import Editing_View
from Processing.Article.Article import Article
from Processing.IO_Manager import IO_Manager

logger = logging.getLogger('infoslicer')

class Edit_Pane(gtk.HBox):
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
        gtk.HBox.__init__(self)
        self.toolitems = []

        """
        Create reading and editing panels
        """
        self.readarticle = Reading_View()  
        self.pack_start(self.readarticle)
        self.readarticle.show()
        
        self.editarticle = Editing_View()
        self.pack_start(self.editarticle)
        self.editarticle.show()
        
        """ Snap selection box """
        snap = ToolComboBox(label_text=_('Snap selection to:'))
        snap.combo.append_item(0, _("Nothing"))
        snap.combo.append_item(1, _("Sentences"))
        snap.combo.append_item(2, _("Paragraphs"))
        snap.combo.append_item(3, _("Sections"))
        snap.combo.connect("changed", self.selection_mode_changed, None)
        snap.combo.set_active(1)
        self.toolitems.append(snap)
        
    """
    When highlighting text, while editing, different selection snap methods 
    can be used (characters, sentences, paragraphs and sections). Change the selection
    mode based on user request 
    """        
    def selection_mode_changed(self, widget, data):
        current_selection = widget.get_active()
        if current_selection == 0:
            self.readarticle.set_full_edit_mode()
            self.editarticle.set_full_edit_mode()
        elif current_selection == 1:
            self.readarticle.set_sentence_selection_mode()
            self.editarticle.set_sentence_selection_mode()
        elif current_selection == 2:
            self.readarticle.set_paragraph_selection_mode()
            self.editarticle.set_paragraph_selection_mode()
        elif current_selection == 3:
            self.readarticle.set_section_selection_mode()
            self.editarticle.set_section_selection_mode()
        #logger.debug(current_selection)
        
    """
    Grab source article from IO manager and set up as editing source.
    """
    def set_source_article(self, article):
        if self.readarticle.textbox.get_article() == article:
            return
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
        
    def set_working_article(self, article):
        if self.editarticle.textbox.get_article() == article:
            return
        self.editarticle.articletitle.set_markup("<span size='medium'><b> %s </b>  %s  \n<b> %s </b>  %s</span>" % \
            (_("Theme:"), article.article_theme, _("Article:"), article.article_title))
        self.editarticle.textbox.set_article(article)
        self.editarticle.article_theme = _("Wikipedia Articles")
