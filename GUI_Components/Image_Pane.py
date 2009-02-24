# Copyright (C) IBM Corporation 2008 
import pygtk
pygtk.require('2.0')
import gtk
from GUI_Components.Pane import Pane
from GUI_Components.Compound_Widgets.Editing_View import Editing_View
from GUI_Components.Compound_Widgets.Gallery_View import Gallery_View
from Processing.Article.Article import Article
from Processing.IO_Manager import IO_Manager
from gettext import gettext as _

class Image_Pane(Pane):
    """
    Created by Christopher Leonard
    
    See __init__.py for overview of panes.
    
    The Image Pane gives a side-by-side view of the source article and edit article.
    The left hand side shows images in the source article.  These can be dragged into
    the edit article.
    """
    
    def __init__(self):
        Pane.__init__(self)
        self.name = _("Images")   
        
        self.panel = gtk.HBox()
        self.panel.set_homogeneous(True)
        self.panel.show()
        self.gallery = Gallery_View()
        self.panel.pack_start(self.gallery)
        self.editarticle = Editing_View()
        self.panel.pack_start(self.editarticle)
        self.editarticle.show_all()

        self.gallery._source_article = None
        
        self.toolbar = gtk.Toolbar()
        """
        Snapping has been turned off in the Editable Textbox, so we no longer
        make use of snapping.  This has been left in case we turn it back on.
        
        
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
        
    def selection_mode_changed(self, widget, data):
        current_selection = widget.get_active_text()
        if current_selection == _("Nothing"):
            self.editarticle.set_full_edit_mode()
        elif current_selection == _("Sentences"):
            self.editarticle.set_sentence_selection_mode()
        elif current_selection == _("Paragraphs"):
            self.editarticle.set_paragraph_selection_mode()
        elif current_selection == _("Sections"):
            self.editarticle.set_section_selection_mode()
        
        
    def set_source_article(self, source):
        print "source received.  title: %s, theme: %s" % (source.article_title, source.article_theme)
        current = self.gallery._source_article
        self.gallery._source_article = source
        if source and source.article_title:
            source.article_theme = _("Wikipedia Articles")
            if current:
                if current.article_title == source.article_title and current.article_theme == source.article_theme:
                    print "same"
                    return
            self.gallery.current_index = 0
            if source.image_list != []:
                print "setting images"
                self.gallery.set_image_list(source.image_list)
                self.gallery.get_first_item()
                
                self.gallery.theme = _("Wikipedia Articles")
                self.gallery.source_article_id = source.source_article_id
                print source.image_list
            else:
                self.gallery.imagenumberlabel.set_label("")
                self.gallery.image.clear()
                self.gallery.caption.set_text(_("This article does not have any images"))
        else:
            self.gallery.imagenumberlabel.set_label("")
            self.gallery.caption.set_text(_("Please select a Wikipedia article from the menu above"))
    
    def get_source_article(self):
        return self.gallery._source_article
         
    def get_working_article(self):
        article = self.editarticle.textbox.get_article()
        #data = article.getData()
        return article
    
    def set_working_article(self, article):
        print "working received, title %s theme %s " % (article.article_title, article.article_theme)
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
   
        
    
