# Copyright (C) IBM Corporation 2008 
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository import GObject
from gi.repository import Pango
import pickle

SELECT_SENTENCE, SELECT_PARAGRAPH, SELECT_SECTION, FULL_EDIT = list(range(4))

class Textbox( Gtk.TextView ):
    """ 
    Created by Jonathan Mace
    The Textbox class is the base class for our own custom textboxes which implement
    the snapping to sentences/paragraphs/sections.  The two subclasses are:
        Editable_Textbox - this is a textbox with full editing features
        Readonly_Textbox - this textbox is not editable and will not respond to
                            drags.
    """
    
    
    def __init__(self): 
        GObject.GObject.__init__(self)
        self.set_border_width(1)
        self.event_handlers = []
        self.set_wrap_mode(Gtk.WrapMode.WORD)
        self.set_cursor_visible(False)
        self.set_editable(False)  
        self.modify_font(Pango.FontDescription('arial 9'))
        self.article = None
        self.set_property("left-margin", 2)
        
    def set_article(self, article):
        self.article = article
        self.set_buffer(article.getBuffer())
        
    def get_article(self):
        return self.article
        
    def show(self):
        Gtk.TextView.show(self)  
        
    def clear(self):
        self.article.delete()     
        
    def disconnect_handlers(self):
        self.set_editable(False)
        self.set_cursor_visible(False)
        for handler in self.event_handlers:
            self.disconnect(handler) 
        self.event_handlers = []   
        
    def get_mouse_iter(self, x, y):
        # Convenience method to get the iter in the buffer of x, y coords.
        click_coords = self.window_to_buffer_coords(Gtk.TextWindowType.TEXT, x, y)
        mouseClickPositionIter = self.get_iter_at_location(click_coords[0], click_coords[1])
        if Gtk.check_version(3, 19, 8) is None:
            mouseClickPositionIter = mouseClickPositionIter[1]
        return mouseClickPositionIter
