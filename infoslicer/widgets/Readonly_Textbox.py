# Copyright (C) IBM Corporation 2008 
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import Pango
import pickle
import logging
from .Textbox import Textbox

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
        self.modify_font(Pango.FontDescription('arial 9'))
        self.MANUEL = 0


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
            self.event_handlers.append(self.connect("drag-data-get", self.drag_data_get_event, None))
            logging.debug('------------------------ SIGNALS ; %s', id(self))
        self.event_handlers.append(self.connect("drag-motion", self.drag_motion, None))

    def drag_motion(self, widget, context, x, y, timestamp, data):
        logging.debug('############ Readonly_Textbox.drag_motion')
        Gdk.drag_status(context, Gdk.DragAction.COPY, timestamp)
        return True

    def clicked_event(self, widget, event, data):
        if event.type == Gdk.EventType._2BUTTON_PRESS or event.type == Gdk.EventType._3BUTTON_PRESS:
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
        if self.selecting:
            if self.block == True:
                self.stop_emission("motion-notify-event")
                self.block = False
                logging.debug('FIXME: this is a workaround due '
                              'https://bugzilla.gnome.org/show_bug.cgi?id=679795')
                # I was getting this error:
                #   TypeError: could not convert type EventMotion
                #   to GdkEvent required for parameter 0
                # self.emit("motion-notify-event", event)
                self.emit("motion-notify-event", Gdk.Event())

                buf = self.get_buffer()            
                mouseiter = self.get_mouse_iter(int(event.x), int(event.y))
                article = self.get_article()
                selectionend = None
                selectionstart = None
                if mouseiter.compare(self.selectionstart) == 1:
                    if self.selectionmode == SELECT_SENTENCE:
                        selectionstart = article.get_sentence(self.selectionstart).getStart()
                        selectionend = article.get_sentence(mouseiter).getEnd()
                    if self.selectionmode == SELECT_PARAGRAPH:
                        selectionstart = article.get_paragraph(self.selectionstart).getStart()
                        selectionend = article.get_paragraph(mouseiter).getEnd()
                    if self.selectionmode == SELECT_SECTION:
                        selectionstart = article.get_section(self.selectionstart).getStart()
                        selectionend = article.get_section(mouseiter).getEnd()
                else:
                    if self.selectionmode == SELECT_SENTENCE: 
                        selectionstart = article.get_sentence(mouseiter).getStart()
                        selectionend = article.get_sentence(self.selectionstart).getEnd()
                    if self.selectionmode == SELECT_PARAGRAPH:
                        selectionstart = article.get_paragraph(mouseiter).getStart()
                        selectionend = article.get_paragraph(self.selectionstart).getEnd()
                    if self.selectionmode == SELECT_SECTION:
                        selectionstart = article.get_section(mouseiter).getStart()
                        selectionend = article.get_section(self.selectionstart).getEnd()
                self.scroll_to_iter(mouseiter, 0, False, 0.5, 0.5)
                article.highlight(selectionstart, selectionend)

            else:
                self.block = True

    def unclicked_event(self, widget, event, data):
        self.article.clear_arrow()
        self.do_button_release_event(widget, event)
        self.selecting = False
        self.stop_emission("button-release-event")

    def drag_data_get_event(self, widget, context, selection_data, info, time, data):
        logging.debug('######## Readonly_Textbox.drag_data_get_event')
        logging.debug('############################## %s', self.MANUEL)
        article = self.article

        if self.selectionmode == SELECT_SENTENCE:
            atom = Gdk.atom_intern("sentence", only_if_exists=False)
        if self.selectionmode == SELECT_PARAGRAPH:
            atom = Gdk.atom_intern("paragraph", only_if_exists=False)
        if self.selectionmode == SELECT_SECTION:
            atom = Gdk.atom_intern("section", only_if_exists=False)

        string = pickle.dumps(article.get_selection())
        selection_data.set(atom, 8, string)
        self.stop_emission("drag-data-get")
        self.set_editable(False)
        self.MANUEL += 1
