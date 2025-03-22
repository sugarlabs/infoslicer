# -*- coding: utf-8 -*-
# Copyright (C) Aneesh Dogra <lionaneesh@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# You should have received a copy of the GNU General Public License
# along with this library; if not, write to the Free Software
# Foundation, 51 Franklin Street, Suite 500 Boston, MA 02110-1335 USA

from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GObject
from gi.repository import GdkPixbuf
import os
import pickle
import pickle
import logging

from .Editable_Textbox import Editable_Textbox
from infoslicer.processing.article_data import *
from infoslicer.processing.article import Article
import book
# from infoslicer.processing import Journal_Getter as journal

logger = logging.getLogger('infoslicer')

# For journal images
IMG_WIDTH  = 400
IMG_HEIGHT = 300

class Journal_Gallery_View( Gtk.HBox ): 
    """
    Created by Aneesh Dogra
    Journal Gallery View

    The journal gallery view displays the jounal images. 
    
    Drag-and-drop methods have been added to set up the images as a drag
    source.  
    The data returned by drag-data-get will be a list containing
    an Image_Data object and a Sentence_Data object.  
    These correspond to the image
    and caption respectively.
    """

    def __init__(self):
        self.image_list = []
        GObject.GObject.__init__(self)
        self.current_index = -1
        self.source_article_id = -1
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
        logging.debug('##################### Galler_View.connect')
        self.imagebox.connect("drag-data-get", self.drag_data_get_event, None)

        self.caption = Gtk.Label(label="")
        self.caption.set_line_wrap(True)

        self.image_drag_container = Gtk.VBox()
        self.image_drag_container.pack_start(self.imagenumberlabel, expand=False,
                                             fill=False, padding=0)
        self.image_drag_container.pack_start(self.imagebox, False, True, 0)
        self.image_drag_container.pack_start(self.caption, False, True, 0)

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

        self.show_all()
        right_button.connect("clicked", self.get_next_item, None)
        left_button.connect("clicked", self.get_prev_item, None)
        self.get_next_item(right_button, None)

    def get_next_item(self, button, param):
        if self.image_list == []:
            self.caption.set_text("No images were found in the journal.")
            self.image.clear()
            return
        self.current_index += 1
        if self.current_index == len(self.image_list):
            self.current_index = 0
        self.imagebuf = GdkPixbuf.Pixbuf.new_from_file(self.image_list[self.current_index][0])
        self.imagebuf = self.imagebuf.scale_simple(IMG_WIDTH, IMG_HEIGHT,
                                            GdkPixbuf.InterpType.BILINEAR)
        self.image.set_from_pixbuf(self.imagebuf)
        self.caption.set_text("\n" + self.image_list[self.current_index][1])
        self.imagenumberlabel.set_text("(%d / %d)\n" % (self.current_index+1, len(self.image_list)))

    def get_prev_item(self, button, param):
        if self.image_list == []:
            self.caption.set_text("No images were found in the journal.")
            self.image.clear()
            return
        if self.current_index == 0:
            self.current_index = len(self.image_list)
        self.current_index -= 1
        self.imagebuf = GdkPixbuf.Pixbuf.new_from_file(self.image_list[self.current_index][0])
        self.imagebuf =  self.imagebuf.scale_simple(IMG_WIDTH, IMG_HEIGHT,
                                             GdkPixbuf.InterpType.BILINEAR)
        self.image.set_from_pixbuf(self.imagebuf)
        self.caption.set_text("\n" + self.image_list[self.current_index][1])
        self.imagenumberlabel.set_text("(%d / %d)\n" % (self.current_index+1, len(self.image_list)))

    def get_first_item(self):
        if self.image_list == []:
            self.caption.set_text("No images were found in the journal.")
            self.image.clear()
            return
        self.current_index = 0
        self.imagebuf = GdkPixbuf.Pixbuf.new_from_file(self.image_list[self.current_index][0])
        self.imagebuf = self.imagebuf.scale_simple(IMG_WIDTH, IMG_HEIGHT,
                                       GdkPixbuf.InterpType.BILINEAR)
        self.image.set_from_pixbuf(self.imagebuf)
        self.caption.set_text("\n" + self.image_list[self.current_index][1])    
        logger.debug("setting text to:")
        logger.debug("(%d / %d)\n" %
                (self.current_index+1, len(self.image_list)))
        self.imagenumberlabel.set_text("(%d / %d)\n" % (self.current_index+1, len(self.image_list)))

    def drag_begin_event(self, widget, context, data):
        logging.debug('########### Journal_Journal_Gallery_View.drag_begin_event called')
        self.imagebox.drag_source_set_icon_pixbuf(self.imagebuf)

    def drag_data_get_event(self, widget, context, selection_data, info, timestamp, data):
        logger.debug('############# Journal_Journal_Gallery_View.drag_data_get_event')
        atom = Gdk.atom_intern("section", only_if_exists=False)
        imagedata = PictureData(self.source_article_id,
                                 self.image_list[self.current_index][0])
        captiondata = SentenceData(0, self.source_article_id, 0, 0, 0, self.image_list[self.current_index][1])
        paragraph1data = ParagraphData(0, self.source_article_id, 0, 0, [imagedata])
        paragraph2data = ParagraphData(0, self.source_article_id, 0, 0, [captiondata])
        sectionsdata = [SectionData(0, self.source_article_id, 0, [paragraph1data, paragraph2data])]
        string = pickle.dumps(sectionsdata)
        selection_data.set(atom, 8, string)

    def add_image(self, image_path, title):
        logger.debug('############# Journal_Journal_Gallery_View.add_image')
        self.image_list.append((image_path, title))
        logger.debug(self.image_list)
        self.get_first_item()
