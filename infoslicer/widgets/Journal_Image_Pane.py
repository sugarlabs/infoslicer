# Copyright (C) IBM Corporation 2008 
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GObject
import logging

from gettext import gettext as _
from .Editing_View import Editing_View
from infoslicer.widgets.Journal_Gallery_View import Journal_Gallery_View
from infoslicer.processing.Article import Article

logger = logging.getLogger('infoslicer')

class Journal_Image_Pane(Gtk.HBox):
    """
    Created by Aneesh Dogra
    
    See __init__.py for overview of panes.
    
    The Image Pane gives a side-by-side view of the jounal images and edit article.
    The left hand side shows the jounal images. These can be dragged into
    the edit article.
    """
    
    def __init__(self):
        GObject.GObject.__init__(self)
        self.toolitems = []
        
        gallery_box = Gtk.VBox()
        gallery_box.show()

        labeleb = Gtk.EventBox()
        labeleb.modify_bg(Gtk.StateType.NORMAL, Gdk.color_parse("#EEEEEE"))
        gallery_box.pack_start(labeleb, False, False, 0)
        labeleb.show()
        
        self.articletitle = Gtk.Label()
        self.articletitle.set_justify(Gtk.Justification.CENTER)
        labeleb.add(self.articletitle)
        self.articletitle.show()
        
        self.gallery = Journal_Gallery_View()
        self.gallery.set_size_request(Gdk.Screen.width()/2, -1)
        gallery_box.pack_start(self.gallery, True, True, 0)

        self.pack_start(gallery_box, False, False, 0)

        self.editarticle = Editing_View()
        self.pack_start(self.editarticle, True, True, 0)
        self.editarticle.show_all()

    def set_working_article(self, article):
        logger.debug("working received, title %s" % article.article_title)

        self.editarticle.articletitle.set_markup(
                "<span size='medium'><b> %s </b>  %s</span>"% \
                (_("Article:"), article.article_title))

        if self.editarticle.textbox.get_article() != article:
            self.editarticle.textbox.set_article(article)
