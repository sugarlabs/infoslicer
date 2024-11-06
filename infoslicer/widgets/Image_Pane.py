# Copyright (C) IBM Corporation 2008 
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GObject
import logging
from gettext import gettext as _

from .Editing_View import Editing_View
from .Gallery_View import Gallery_View
from infoslicer.processing.Article import Article

logger = logging.getLogger('infoslicer')

class Image_Pane(Gtk.HBox):
    """
    Created by Christopher Leonard
    
    See __init__.py for overview of panes.
    
    The Image Pane gives a side-by-side view of the source article and edit article.
    The left hand side shows images in the source article.  These can be dragged into
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
        
        self.gallery = Gallery_View()
        self.gallery.set_size_request(Gdk.Screen.width()/2, -1)
        gallery_box.pack_start(self.gallery, True, True, 0)

        self.pack_start(gallery_box, False, False, 0)
        self.editarticle = Editing_View()
        self.pack_start(self.editarticle, True, True, 0)
        self.editarticle.show_all()

        self.gallery._source_article = None
        
    def set_source_article(self, source):
        self.articletitle.set_markup(
                "<span size='medium'><b> %s </b>  %s</span>"% \
                (_("Article:"), source.article_title))

        if self.gallery._source_article == source:
            return

        logger.debug("source received.  title: %s" % source.article_title)
        current = self.gallery._source_article
        self.gallery._source_article = source

        if source and source.article_title:
            self.gallery.current_index = 0
            if source.image_list != []:
                logger.debug("setting images")
                self.gallery.set_image_list(source.image_list)
                self.gallery.get_first_item()
                
                self.gallery.source_article_id = source.source_article_id
                logger.debug(source.image_list)
            else:
                self.gallery.imagenumberlabel.set_label("")
                self.gallery.image.clear()
                self.gallery.caption.set_text(_("This article does not have any images"))
        else:
            self.gallery.imagenumberlabel.set_label("")
            self.gallery.caption.set_text(_("Please select a Wikipedia article from the menu above"))
    
    def set_working_article(self, article):
        logger.debug("working received, title %s" % article.article_title)

        self.editarticle.articletitle.set_markup(
                "<span size='medium'><b> %s </b>  %s</span>"% \
                (_("Article:"), article.article_title))

        if self.editarticle.textbox.get_article() != article:
            self.editarticle.textbox.set_article(article)
