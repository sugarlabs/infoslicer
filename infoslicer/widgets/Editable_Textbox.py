# Copyright (C) IBM Corporation 2008 
import pygtk
pygtk.require('2.0')
import gtk
import cPickle
import pango
import copy
from Textbox import Textbox

SNAP_SENTENCE, SNAP_PARAGRAPH, SNAP_SECTION, SNAP_NONE = range(4)

class Editable_Textbox( Textbox ):
    """
    Created by Jonathan Mace
    This class implements its own special code for dragging and selecting.
    It has an article class which provides the text buffer, and any modifications
    to the text buffer are done via the article class.
    """
    
    def __init__(self): 
        gtk.TextView.__init__(self)
        self.set_border_width(1)
        self.set_cursor_visible(True)
        self.set_editable(True)  
        self.set_wrap_mode(gtk.WRAP_WORD)
        self.article = None
        self.set_mode(SNAP_SENTENCE)
        self.changed = False
        self.block = True
        
        self.selecting = False
        self.handlers = []
        self.modify_font(pango.FontDescription('arial 9'))
        self.ignore_snap_self = True
        self.drag_source = False
        self.edited = False
        self.set_property("left-margin", 5)

    def set_article(self, article):
        self.article = article
        self.set_buffer(article.getBuffer())
        
    def get_article(self):
        return self.article
        
    def clear(self):
        self.article.delete()
        
    def get_mouse_iter(self, x, y):
        click_coords = self.window_to_buffer_coords(gtk.TEXT_WINDOW_TEXT, x, y)
        mouseClickPositionIter = self.get_iter_at_location(click_coords[0], click_coords[1])
        return mouseClickPositionIter
    
    def set_mode(self, snapto):
        self.snapto = snapto
                
    def set_buffer(self, buffer):
        for handler in self.handlers:
            self.disconnect(handler)
        
        buffer.connect("changed", self.text_changed, None)
        gtk.TextView.set_buffer(self, buffer)
        
        self.handlers = []
        
        self.handlers.append(self.connect("button-press-event", self.clicked_event, None))
        self.handlers.append(self.connect("button-release-event", self.unclicked_event, None))
        self.handlers.append(self.connect("drag_data_get", self.drag_data_get_event, None))
        self.handlers.append(self.connect("drag_begin", self.drag_begin_event, None))
        self.handlers.append(self.connect("drag-motion", self.drag_motion_event, None))
        self.handlers.append(self.connect("drag-drop", self.drag_drop_event, None))
        self.handlers.append(self.connect("drag-leave", self.drag_leave_event, None))
        self.handlers.append(self.connect("drag-data-delete", self.drag_data_delete_event, None))
        self.handlers.append(self.connect("drag_data_received", self.drag_data_received_event, None))
        self.handlers.append(self.connect("drag-end", self.drag_end_event, None))
        self.handlers.append(self.connect("motion-notify-event", self.motion_notify, None))
        self.handlers.append(self.connect("focus-out-event", self.leave_notify, None))
        
    def text_changed(self, buffer, data):
        self.changed = True
        self.selecting = False
    
    def motion_notify(self, widget, event, data):
        if not self.ignore_snap_self and self.selecting:
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
                    if self.snapto == SNAP_SENTENCE: 
                        selectionstart = article.getSentence(self.selectionstart).getStart()
                        selectionend = article.getSentence(mouseiter).getEnd()
                    if self.snapto == SNAP_PARAGRAPH:
                        selectionstart = article.getParagraph(self.selectionstart).getStart()
                        selectionend = article.getParagraph(mouseiter).getEnd()
                    if self.snapto == SNAP_SECTION:
                        selectionstart = article.getSection(self.selectionstart).getStart()
                        selectionend = article.getSection(mouseiter).getEnd()
                else:
                    if self.snapto == SNAP_SENTENCE: 
                        selectionstart = article.getSentence(mouseiter).getStart()
                        selectionend = article.getSentence(self.selectionstart).getEnd()
                    if self.snapto == SNAP_PARAGRAPH:
                        selectionstart = article.getParagraph(mouseiter).getStart()
                        selectionend = article.getParagraph(self.selectionstart).getEnd()
                    if self.snapto == SNAP_SECTION:
                        selectionstart = article.getSection(mouseiter).getStart()
                        selectionend = article.getSection(self.selectionstart).getEnd()
                self.scroll_to_iter(mouseiter, 0)
                article.highlight(selectionstart, selectionend)                
                    
            else:
                self.block = True
        
    def clicked_event(self, widget, event, data):
        if event.type == gtk.gdk._2BUTTON_PRESS or event.type == gtk.gdk._3BUTTON_PRESS:
            self.stop_emission("button_press_event")
            return
        if event.button == 3:
            self.stop_emission("button_press_event")
            return
        if self.changed == True:
            buf = self.get_buffer()
            article = self.get_article()
            
            article.checkIntegrity()
            self.changed = False  
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
            
    def leave_notify(self, widget, event, data):
        if self.changed == True:
            offset = self.get_buffer().get_property("cursor-position")
            self.article.checkIntegrity()
            newbuf = self.article.getBuffer()
            self.set_buffer(newbuf)
            self.changed = False
            iter = newbuf.get_iter_at_offset(offset)
            newbuf.place_cursor(iter)        
        
    def unclicked_event(self, widget, event, data):
        if self.snapto != SNAP_NONE:
            self.article.clearArrow()
            self.do_button_release_event(widget, event)
            self.selecting = False
            return True
        else:
            return False
        
    def drag_begin_event(self, widget, context, data):
        self.grab_focus()
        if self.snapto != SNAP_NONE:
            a = self.article
            a.rememberSelection()
            self.drag_source = True
    
    def drag_drop_event(self, widget, context, x, y, time, data):
        if self.snapto != SNAP_NONE:
            self.article.clearArrow()
            self.set_cursor_visible(True)
    
    def drag_motion_event(self, widget, drag_context, x, y, time, data):
        if self.snapto != SNAP_NONE and not self.ignore_snap_self or (not self.drag_source and self.ignore_snap_self):
            self.delete_on_fail = False
            self.set_cursor_visible(False)
            a = self.article
            loc_iter = self.get_mouse_iter(x, y)
            
            if self.snapto == SNAP_SENTENCE:
                a.mark(a.getBestSentence(loc_iter).getStart())
                #a.markSentence(loc_iter)
            if self.snapto == SNAP_PARAGRAPH:
                a.mark(a.getBestParagraph(loc_iter).getStart())
                #a.markParagraph(loc_iter)
            if self.snapto == SNAP_SECTION:
                a.mark(a.getBestSection(loc_iter).getStart())
                #a.markSection(loc_iter)
              
            result = self.do_drag_motion(widget, drag_context, x, y, time)
            self.stop_emission("drag-motion")
            return result
            self.changed = False
        else:
            self.set_cursor_visible(True)
            self.drag_source = True
    
    
    def drag_leave_event(self, widget, context, time, data):
        if self.snapto != SNAP_NONE and not self.ignore_snap_self or (not self.drag_source and self.ignore_snap_self):
            self.delete_on_fail = True
            self.article.clearArrow()
            self.do_drag_leave(widget, context, time)
            self.stop_emission("drag-leave")
            self.changed = False
            self.set_cursor_visible(True)
        
    def drag_data_delete_event(self, widget, context, data):
        if self.snapto != SNAP_NONE and not self.ignore_snap_self or (not self.drag_source and self.ignore_snap_self):
            a = self.article
            a.deleteDragSelection()
            self.stop_emission("drag-data-delete")
            self.changed = False
        
    def drag_data_received_event(self, widget, context, x, y, selection_data, info, time, data):
        if self.snapto != SNAP_NONE and not self.ignore_snap_self or (not self.drag_source and self.ignore_snap_self):    
            a = self.article
            insert_loc = self.get_mouse_iter(x, y)
            data_received_type = str(selection_data.type)    
            data = cPickle.loads(str(selection_data.data))
            
            if data_received_type == "sentence":
                bestpoint = insert_loc  
            if data_received_type == "paragraph":
                bestpoint = a.getBestParagraph(insert_loc).getStart()
            if data_received_type == "section":
                bestpoint = a.getBestSection(insert_loc).getStart()
                
            a.insert(data, insert_loc)
                
            self.stop_emission("drag-data-received")
            context.finish(True, True, time)
            self.grab_focus()
        
    def drag_data_get_event(self, widget, context, selection_data, info, time, data):
        if not self.ignore_snap_self and self.snapto != SNAP_NONE:
            a = self.article
            
            if self.snapto == SNAP_SENTENCE:
                atom = gtk.gdk.atom_intern("sentence")
            if self.snapto == SNAP_PARAGRAPH:
                atom = gtk.gdk.atom_intern("paragraph")
            if self.snapto == SNAP_SECTION:
                atom = gtk.gdk.atom_intern("section")
                
            string = cPickle.dumps(a.getSelection())
            selection_data.set(atom, 8, string)
            self.stop_emission("drag-data-get")
            
    def drag_end_event(self, widget, context, data):
        self.drag_source = False
