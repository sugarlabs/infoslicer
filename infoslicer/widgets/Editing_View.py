# Copyright (C) IBM Corporation 2008 
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GObject
from .Editable_Textbox import Editable_Textbox

class Editing_View( Gtk.VBox ): 
    """
    Created by Jonathan Mace
    This class wraps an editable textbox into a scrollable window and 
    gives it a title.
    """
    def __init__(self):
        GObject.GObject.__init__(self)
        self.set_border_width(0)
        self.set_spacing(2)
        
        labeleb = Gtk.EventBox()
        labeleb.modify_bg(Gtk.StateType.NORMAL, Gdk.color_parse("#EEEEEE"))
        self.pack_start(labeleb, False, False, 0)
        labeleb.show()
        
        self.articletitle = Gtk.Label()
        self.articletitle.set_justify(Gtk.Justification.CENTER)
        labeleb.add(self.articletitle)
        self.articletitle.show()
        
        self.textwindow = Gtk.ScrolledWindow()
        self.textwindow.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.pack_start(self.textwindow, True, True, 0)
        self.textwindow.show()
        
        self.textbox = Editable_Textbox()
        self.textwindow.add(self.textbox)
        self.textbox.show()
        
    def set_sentence_selection_mode(self):
        self.textbox.set_mode(0)
        
    def set_paragraph_selection_mode(self):
        self.textbox.set_mode(1)
        
    def set_section_selection_mode(self):
        self.textbox.set_mode(2)
        
    def set_full_edit_mode(self):
        self.textbox.set_mode(3)

    def clear_contents(self):
        self.textbox.clear()
