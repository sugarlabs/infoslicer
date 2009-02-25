# Copyright (C) IBM Corporation 2008 
import pygtk
pygtk.require('2.0')
import gtk
import logging
from gettext import gettext as _

from GUI_Components.Compound_Widgets.Editing_View import Editing_View
from GUI_Components.Compound_Widgets.Gallery_View import Gallery_View
from Processing.Article.Article import Article
from Processing.IO_Manager import IO_Manager

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
        
        self.gallery = Gallery_View()
        self.pack_start(self.gallery)
        self.editarticle = Editing_View()
        self.pack_start(self.editarticle)
        self.editarticle.show_all()

        self.gallery._source_article = None
        
    def set_source_article(self, source):
        if self.gallery._source_article == source:
            return
        logger.debug("source received.  title: %s, theme: %s" %
                (source.article_title, source.article_theme))
        current = self.gallery._source_article
        self.gallery._source_article = source
        if source and source.article_title:
            source.article_theme = _("Wikipedia Articles")
            if current:
                if current.article_title == source.article_title and current.article_theme == source.article_theme:
                    logger.debug("same")
                    return
            self.gallery.current_index = 0
            if source.image_list != []:
                logger.debug("setting images")
                self.gallery.set_image_list(source.image_list)
                self.gallery.get_first_item()
                
                self.gallery.theme = _("Wikipedia Articles")
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
        if self.editarticle.textbox.get_article() == article:
            return
        logger.debug("working received, title %s theme %s " %
                (article.article_title, article.article_theme))
        self.editarticle.articletitle.set_markup("<span size='medium'><b> %s </b>  %s   \n<b> %s </b>  %s</span>"% \
            (_("Theme:"), article.article_theme, _("Article:"), article.article_title))
        if article == None:
            article = Article()
        self.editarticle.textbox.set_article(article)
        if article.article_theme == None:
            article.article_theme = _("My Articles")
        theme_list = IO_Manager().get_pages_in_theme(_("Wikipedia Articles"))
        self.gallery.theme = _("Wikipedia Articles")
        count = -1
        self.gallery.articlemenu.get_model().clear()
        
        for item in theme_list:
            count += 1 
            self.gallery.articlemenu.append_text(item)
            if self.gallery._source_article != None and item == self.gallery._source_article.article_title:
                self.gallery.articlemenu.set_active(count)
