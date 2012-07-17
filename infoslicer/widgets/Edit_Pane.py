# Copyright (C) IBM Corporation 2008 
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GObject
import logging
from gettext import gettext as _

from sugar3.graphics.toolcombobox import ToolComboBox

from Reading_View import Reading_View
from Editing_View import Editing_View
from infoslicer.processing.Article import Article

logger = logging.getLogger('infoslicer')

class Edit_Pane(Gtk.HBox):
    """
    Created by Jonathan Mace
    
    See __init__.py for overview of panes.
    
    The Edit Pane gives a side-by-side view of the source article and edit
    article and allows users to drag text selections from the left hand
    (source) to the right hand side (edited version).
    
    The article displayed in the left hand side (source) can be changed by the 
    drop-down menu (implemented in Compound_Widgets.Reading_View)
    
    The toolbar gives options to change the selection type.
    """
    
    def __init__(self):
        GObject.GObject.__init__(self)
        self.toolitems = []

        readarticle_box = Gtk.VBox()
        readarticle_box.show()

        labeleb = Gtk.EventBox()
        labeleb.modify_bg(Gtk.StateType.NORMAL, Gdk.color_parse("#EEEEEE"))
        readarticle_box.pack_start(labeleb, False, False, 0)
        labeleb.show()
        
        self.articletitle = Gtk.Label()
        self.articletitle.set_justify(Gtk.Justification.CENTER)
        labeleb.add(self.articletitle)
        self.articletitle.show()

        vbox = Gtk.VBox()

        snap = ToolComboBox(label_text=_('Snap selection to:'))
        snap.combo.append_item(0, _("Nothing"))
        snap.combo.append_item(1, _("Sentences"))
        snap.combo.append_item(2, _("Paragraphs"))
        snap.combo.append_item(3, _("Sections"))
        snap.combo.set_active(1)
        vbox.pack_start(snap, False, False, 0)

        """
        Create reading and editing panels
        """
        self.readarticle = Reading_View()  
        self.readarticle.set_size_request(Gdk.Screen.width()/2, -1)
        self.readarticle.show()
        readarticle_box.pack_start(self.readarticle, True, True, 0)
        vbox.pack_start(readarticle_box, True, True, 0)

        self.pack_start(vbox, False, False, 0)

        self.editarticle = Editing_View()
        self.pack_start(self.editarticle, True, True, 0)
        self.editarticle.show()

        snap.combo.connect("changed", self.selection_mode_changed, None)
        
        
    """
    When highlighting text, while editing, different selection snap methods 
    can be used (characters, sentences, paragraphs and sections). Change the
    selection mode based on user request
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
        
    def set_source_article(self, article):
        self.articletitle.set_markup(
                "<span size='medium'><b> %s </b>  %s</span>" % \
                (_("Article:"), article.article_title))

        if self.readarticle.textbox.get_article() != article:
            self.readarticle.textbox.set_article(article)
        
    def set_working_article(self, article):
        self.editarticle.articletitle.set_markup(
                "<span size='medium'><b> %s </b>  %s</span>" % \
                (_("Article:"), article.article_title))
        if self.editarticle.textbox.get_article() != article:
            self.editarticle.textbox.set_article(article)
