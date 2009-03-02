# Copyright (C) IBM Corporation 2008 
import pygtk
pygtk.require('2.0')
import gtk
import pango
import cPickle
from Textbox import Textbox

SELECT_SENTENCE, SELECT_PARAGRAPH, SELECT_SECTION, FULL_EDIT = range(4)

class Readonly_Textbox( Textbox ):    
    """
    Created by Jonathan Mace
    This class implements its own special code for dragging and selecting.
    It has an article class which provides the text buffer, and any modifications
    to the text buffer are done via the article class.
    This class is read-only, so it is not editable and will not act as a drag
    destination.
    """
    
    def __init__(self, use_as_drag_source = True):
        Textbox.__init__(self)
        self.selecting = False
        self.use_as_drag_source = use_as_drag_source
        self.set_mode(SELECT_SENTENCE)
        self.block = True
        self.modify_font(pango.FontDescription('arial 9'))
        
    
    def set_mode(self, mode):
        self.selectionmode = mode
        self.disconnect_handlers()
        if mode == SELECT_SENTENCE: self.__set_select_mode()
        elif mode == SELECT_PARAGRAPH: self.__set_select_mode()
        elif mode == SELECT_SECTION: self.__set_select_mode()
        else: pass
        
    def __set_select_mode(self):
        if self.use_as_drag_source == True:
            self.event_handlers.append(self.connect("button-press-event", self.clicked_event, None))
            self.event_handlers.append(self.connect("motion-notify-event", self.motion_notify, None))
            self.event_handlers.append(self.connect("move-cursor", self.move_cursor, None))
            self.event_handlers.append(self.connect("button-release-event", self.unclicked_event, None))
            self.event_handlers.append(self.connect("drag_data_get", self.drag_data_get_event, None))
        self.event_handlers.append(self.connect("drag-motion", self.drag_motion, None))
        
    def drag_motion(self, widget, context, x, y, timestamp, data):
        context.drag_status(gtk.gdk.ACTION_COPY, timestamp)
        return True
        
    def clicked_event(self, widget, event, data):
        if event.type == gtk.gdk._2BUTTON_PRESS or event.type == gtk.gdk._3BUTTON_PRESS:
            self.stop_emission("button_press_event")
            return
        if event.button == 3:
            self.stop_emission("button_press_event")
            return
        if not self.get_buffer().get_has_selection():
            result = self.do_button_press_event(widget, event)
            
            a = self.article
            loc_iter = self.get_mouse_iter(int(event.x), int(event.y))
            
            self.selecting = True
            self.selectionstart = loc_iter
            self.stop_emission("button-press-event")
            return result
        else:
            buf = self.get_buffer()
            bounds = buf.get_selection_bounds()
            if bounds == ():
                return
            start = bounds[0]
            end = bounds[1]
            if start.compare(end) == 1:
                start, end = end, start
            loc = self.get_mouse_iter(int(event.x), int(event.y))
            if start.compare(loc) == 1 or loc.compare(end) == 1:
                self.do_button_press_event(widget, event)
                a = self.article
                self.selecting = True
                self.selectionstart = loc
                self.stop_emission("button-press-event")
            
    def move_cursor(self, widget, stepsize, count, extend, data):
        if self.selecting:
            result = self.do_move_cursor(widget, event)
            self.stop_emission("move-cursor")
            return result
    
    def motion_notify(self, widget, event, data):
        if self.selecting:
            """ The following code implements the 'snapping' to sentences etc.
            
             The base class responds to motion notify events and does some unknown (to me)
             action which for some reason, must complete, otherwise on some platforms it will
             stop any more motion notify events.
            
             So what happens, is the first 'run through' of the motion notify responder emits another
             motion notify event, ignores it and lets the base class respond to it.  Then when control
             is given back to the first emission, we implement our code.  The order of events is:
            
            1) motion notify event 1 emitted naturally
            2)    our class responds to motion notify event 1
            3)        motion notify event 2 emitted by step 2)
            4)            our class ignores motion notify event 2
            5)            the default class acts upon motion notify event 2
            6)        motion notify event 2 finishes naturally
            7)    our class does its stuff
            8) motion notify event 1 finishes by our class stopping its emission
            
            """
            
            if self.block == True:
                self.stop_emission("motion-notify-event")
                self.block = False
                self.emit("motion-notify-event", event)
                
                buf = self.get_buffer()            
                mouseiter = self.get_mouse_iter(int(event.x), int(event.y))
                article = self.get_article()
                if mouseiter.compare(self.selectionstart) == 1:
                    if self.selectionmode == SELECT_SENTENCE: 
                        selectionstart = article.getSentence(self.selectionstart).getStart()
                        selectionend = article.getSentence(mouseiter).getEnd()
                    if self.selectionmode == SELECT_PARAGRAPH:
                        selectionstart = article.getParagraph(self.selectionstart).getStart()
                        selectionend = article.getParagraph(mouseiter).getEnd()
                    if self.selectionmode == SELECT_SECTION:
                        selectionstart = article.getSection(self.selectionstart).getStart()
                        selectionend = article.getSection(mouseiter).getEnd()
                else:
                    if self.selectionmode == SELECT_SENTENCE: 
                        selectionstart = article.getSentence(mouseiter).getStart()
                        selectionend = article.getSentence(self.selectionstart).getEnd()
                    if self.selectionmode == SELECT_PARAGRAPH:
                        selectionstart = article.getParagraph(mouseiter).getStart()
                        selectionend = article.getParagraph(self.selectionstart).getEnd()
                    if self.selectionmode == SELECT_SECTION:
                        selectionstart = article.getSection(mouseiter).getStart()
                        selectionend = article.getSection(self.selectionstart).getEnd()
                self.scroll_to_iter(mouseiter, 0)
                article.highlight(selectionstart, selectionend)                
                    
            else:
                self.block = True
            
    def unclicked_event(self, widget, event, data):
        self.article.clearArrow()
        self.do_button_release_event(widget, event)
        self.selecting = False
        self.stop_emission("button-release-event")
        
    def drag_data_get_event(self, widget, context, selection_data, info, time, data):
        
        a = self.article
        
        if self.selectionmode == SELECT_SENTENCE:
            atom = gtk.gdk.atom_intern("sentence")
        if self.selectionmode == SELECT_PARAGRAPH:
            atom = gtk.gdk.atom_intern("paragraph")
        if self.selectionmode == SELECT_SECTION:
            atom = gtk.gdk.atom_intern("section")
            
        string = cPickle.dumps(a.getSelection())
        selection_data.set(atom, 8, string)
        self.stop_emission("drag-data-get")
        self.set_editable(False)
        
