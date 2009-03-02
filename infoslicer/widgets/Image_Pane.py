# Copyright (C) IBM Corporation 2008 
import pygtk
pygtk.require('2.0')
import gtk
import logging
from gettext import gettext as _

from Editing_View import Editing_View
from Gallery_View import Gallery_View
from infoslicer.processing.Article import Article

logger = logging.getLogger('infoslicer')

class Image_Pane(gtk.HBox):
    """
    Created by Christopher Leonard
    
    See __init__.py for overview of panes.
    
    The Image Pane gives a side-by-side view of the source article and edit article.
    The left hand side shows images in the source article.  These can be dragged into
    the edit article.
    """
    
    def __init__(self):
        gtk.HBox.__init__(self)
        self.toolitems = []
        
        gallery_box = gtk.VBox()
        gallery_box.show()

        labeleb = gtk.EventBox()
        labeleb.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#EEEEEE"))
        gallery_box.pack_start(labeleb, False, False, 0)
        labeleb.show()
        
        self.articletitle = gtk.Label()
        self.articletitle.set_justify(gtk.JUSTIFY_CENTER)
        labeleb.add(self.articletitle)
        self.articletitle.show()
        
        self.gallery = Gallery_View()
        self.gallery.set_size_request(gtk.gdk.screen_width()/2, -1)
        gallery_box.pack_start(self.gallery)

        self.pack_start(gallery_box, False)
        self.editarticle = Editing_View()
        self.pack_start(self.editarticle)
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
