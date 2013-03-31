# Copyright (C) IBM Corporation 2008 
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GObject
from gi.repository import GdkPixbuf
import os
import cPickle
import logging

from Editable_Textbox import Editable_Textbox
from infoslicer.processing.Article_Data import *
from infoslicer.processing.Article import Article
import book

logger = logging.getLogger('infoslicer')

class Gallery_View( Gtk.HBox ): 
    """ 
    Created by Christopher Leonard
    Drag-and-drop methods added by Jonathan Mace
    
    The gallery view acts in the same was as the Reading_View
    except instead of displaying the text of an article, it
    displays the images associated with that article, in a scrollable display.
    
    
    Drag-and-drop methods have been added to set up the images as a
    drag source.  The data returned by drag-data-get will be a list
    containing an Image_Data object and a Sentence_Data object.  These
    correspond to the image and caption respectively.
    """
    
    def __init__(self):
        self.image_list = []
        GObject.GObject.__init__(self)
        self.set_size_request(int(Gdk.Screen.width() / 2), -1)
        self.current_index = -1
        
        left_button = Gtk.Button(label="\n\n << \n\n")
        
        right_button = Gtk.Button(label="\n\n >> \n\n")
        
        self.imagenumberlabel = Gtk.Label()
        
        self.image = Gtk.Image()
        
        self.imagebox = Gtk.EventBox()
        self.imagebox.add(self.image)
        
        self.imagebox.drag_source_set(Gdk.ModifierType.BUTTON1_MASK,
                                      [],
                                      Gdk.DragAction.COPY)
        self.imagebox.drag_source_add_image_targets()
        self.imagebox.connect("drag-begin", self.drag_begin_event, None)
        logging.debug('##################### Gallery_View.connect')
        self.imagebox.connect("drag-data-get", self.drag_data_get_event, None)
        
        self.caption = Gtk.Label(label="")
        self.caption.set_size_request(int(Gdk.Screen.width() / 3), -1)
        self.caption.set_line_wrap(True)
        self.caption.set_max_width_chars(40)
        
        self.image_drag_container = Gtk.VBox()
        self.image_drag_container.pack_start(self.imagenumberlabel, expand=False,
                                             fill=False, padding=0)
        self.image_drag_container.pack_start(self.imagebox, False, False, 0)
        self.image_drag_container.pack_start(self.caption, False, False, 0)
        
        image_container = Gtk.VBox()
        image_container.pack_start(Gtk.Label(" "), True, True, 0)
        image_container.pack_start(self.image_drag_container, False, True, 0)
        image_container.pack_start(Gtk.Label(" "), True, True, 0)
        
        left_button_container = Gtk.VBox()
        left_button_container.pack_start(Gtk.Label(" "), True, True, 0)
        left_button_container.pack_start(left_button, False, True, 0)
        left_button_container.pack_start(Gtk.Label(" "), True, True, 0)
        
        right_button_container = Gtk.VBox()
        right_button_container.pack_start(Gtk.Label(" "), True, True, 0)
        right_button_container.pack_start(right_button, False, True, 0)
        right_button_container.pack_start(Gtk.Label(" "), True, True, 0)

        
        self.pack_start(left_button_container, False, True, 0)
        self.pack_start(image_container, True, True, 0)
        self.pack_start(right_button_container, False, True, 0)
   
        self._source_article = None
        self.show_all()
        right_button.connect("clicked", self.get_next_item, None)
        left_button.connect("clicked", self.get_prev_item, None)
        self.get_next_item(right_button, None)
        
        self.source_article_id = 0
        
    def get_next_item(self, button, param):
        if self.image_list == []:
            if self._source_article and self._source_article.article_title:
                self.caption.set_text("This article does not have any images")
            else:
                self.caption.set_text("Please select a Wikipedia article from the menu above")
            self.image.clear()
            return
        self.current_index += 1
        if self.current_index == len(self.image_list):
            self.current_index = 0
        self.imagebuf = GdkPixbuf.Pixbuf.new_from_file(self.image_list[self.current_index][0])
        self.image.set_from_pixbuf(self.imagebuf)
        self.caption.set_text("\n" + self.image_list[self.current_index][1])
        self.imagenumberlabel.set_text("(%d / %d)\n" % (self.current_index+1, len(self.image_list)))   
        
    def get_prev_item(self, button, param):
        if self.image_list == []:
            if self._source_article and self._source_article.article_title:
                self.caption.set_text("This article does not have any images")
            else:
                self.caption.set_text("Please select a Wikipedia article from the menu above")
            self.image.clear()
            return
        if self.current_index == 0:
            self.current_index = len(self.image_list)
        self.current_index -= 1
        self.imagebuf = GdkPixbuf.Pixbuf.new_from_file(self.image_list[self.current_index][0])
        self.image.set_from_pixbuf(self.imagebuf)
        self.caption.set_text("\n" + self.image_list[self.current_index][1])
        self.imagenumberlabel.set_text("(%d / %d)\n" % (self.current_index+1, len(self.image_list)))   
        
    def get_first_item(self):
        if self.image_list == []:
            if self._source_article and self._source_article.article_title:
                self.caption.set_text("This article does not have any images")
            else:
                self.caption.set_text("Please select a Wikipedia article from the menu above")
            self.image.clear()
            return        
        self.current_index = 0
        self.imagebuf = GdkPixbuf.Pixbuf.new_from_file(self.image_list[self.current_index][0])
        self.image.set_from_pixbuf(self.imagebuf)
        self.caption.set_text("\n" + self.image_list[self.current_index][1])    
        logger.debug("setting text to:")
        logger.debug("(%d / %d)\n" %
                (self.current_index+1, len(self.image_list)))
        self.imagenumberlabel.set_text("(%d / %d)\n" % (self.current_index+1, len(self.image_list)))    
        
    def set_image_list(self, image_list):
        logger.debug("validagting image list")
        self.image_list = _validate_image_list(book.wiki.root, image_list)
        logger.debug(self.image_list)
        
    def drag_begin_event(self, widget, context, data):
        logging.debug('########### Gallery_View.drag_begin_event called')
        self.imagebox.drag_source_set_icon_pixbuf(self.imagebuf)
        
    def drag_data_get_event(self, widget, context, selection_data, info, timestamp, data):
        logger.debug('############# Gallery_View.drag_data_get_event')
        atom = Gdk.atom_intern("section", only_if_exists=False)
        imagedata = Picture_Data(self.source_article_id,
                self.image_list[self.current_index][0],
                self.image_list[self.current_index][2])
        captiondata = Sentence_Data(0, self.source_article_id, 0, 0, 0, self.image_list[self.current_index][1])
        paragraph1data = Paragraph_Data(0, self.source_article_id, 0, 0, [imagedata])
        paragraph2data = Paragraph_Data(0, self.source_article_id, 0, 0, [captiondata])
        sectionsdata = [Section_Data(0, self.source_article_id, 0, [paragraph1data, paragraph2data])]
        string = cPickle.dumps(sectionsdata)
        selection_data.set(atom, 8, string)
        
def _validate_image_list(root, image_list):
    """
        provides a mechanism for validating image lists and expanding relative paths
        @param image_list: list of images to validate
        @return: list of images with corrected paths, and broken images removed
    """
    for i in xrange(len(image_list)):
        if not os.access(image_list[i][0], os.F_OK):
            if os.access(os.path.join(root, image_list[i][0]), os.F_OK):
                image_list[i] = (os.path.join(root, image_list[i][0]),
                        image_list[i][1], image_list[i][2])
            else:
                image = None
    #removing during for loop was unreliable
    while None in image_list:
        image_list.remove(None)
    return image_list
