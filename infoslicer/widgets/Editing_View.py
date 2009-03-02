# Copyright (C) IBM Corporation 2008 
import pygtk
pygtk.require('2.0')
import gtk
from Editable_Textbox import Editable_Textbox

class Editing_View( gtk.VBox ): 
    """
    Created by Jonathan Mace
    This class wraps an editable textbox into a scrollable window and 
    gives it a title.
    """
    def __init__(self):
        gtk.VBox.__init__(self)
        self.set_border_width(0)
        self.set_spacing(2)
        
        labeleb = gtk.EventBox()
        labeleb.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#EEEEEE"))
        self.pack_start(labeleb, False, False, 0)
        labeleb.show()
        
        self.articletitle = gtk.Label()
        self.articletitle.set_justify(gtk.JUSTIFY_CENTER)
        labeleb.add(self.articletitle)
        self.articletitle.show()
        
        self.textwindow = gtk.ScrolledWindow()
        self.textwindow.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        self.pack_start(self.textwindow)
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
