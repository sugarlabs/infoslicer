# Copyright (C) IBM Corporation 2008

import pygtk
import sys
pygtk.require('2.0')
import gtk
import time
import platform
from GUI_Components.Edit_Pane import Edit_Pane
from GUI_Components.Format_Pane import Format_Pane
from GUI_Components.Library_Pane import Library_Pane
from GUI_Components.Image_Pane import Image_Pane
from GUI_Components.Publish_Pane import Publish_Pane
from Processing.Article.Article import Article
from Processing.IO_Manager import IO_Manager
import logging

logger = logging.getLogger('infoslicer')

class Infoslicer_GUI:
    """ 
    Created by Jonathan Mace
    
    This is an abstract class.  Whichever platform decides to run the app
    must created a subclass of this class.
    
    """
    
    def __init__(self):
        logger.info(
                "InfoSlicer version 0.1, Copyright (C) 2008 IBM Corporation; " \
                "InfoSlicer comes with ABSOLUTELY NO WARRANTY; " \
                "for details see LICENSE.txt file.")
        self.__set_up_GUI()
    
    def setpanel(self, panel):
        """
        This method sets the main display to the panel specified.
        """ 
        pass
    
    def clearpanel(self):
        """
        This method clears the main display (if setpanel does not clear it before setting)
        """
        pass
    
    def settoolbars(self):
        """
        This method sets the toolbars.  Toolbars are stored in self.toolbars and the
        corresponding toolbar names are stored in self.toolbarnames
        """
        pass
    
    def switch_page(self, page_num):
        """
        This method sets the current page to page_num when called.
        """
        pass
    
    """
    Change tab shown and available to the user. 
    """
    def mode_switched(self, mode):
        # Mode is the index of the tab that has been switched to
        if self.currentindex != mode:
            pane = self.panes[mode]
            if self.currentpane != None:
                self.source = self.currentpane.get_source_article()
                self.working = self.currentpane.get_working_article()
            pane.set_source_article(self.source)
            pane.set_working_article(self.working)
            self.clearpanel()
            self.setpanel(pane.panel)
            self.currentpane = pane
            self.currentindex = mode
            
    def __set_up_GUI(self):
        # Set up dummy library if appropriate
        running_on = platform.system()
        if running_on == "Linux" and "olpc" in platform.platform().lower():
            themes = IO_Manager().get_themes()
            if themes == []:
                IO_Manager().install_library()
        # Instantiate the panels to be displayed by the GUI
        self.library = Library_Pane()
        self.panes = [self.library,
                      Edit_Pane(),
                      Format_Pane(),
                      Image_Pane(),
                      Publish_Pane()]
        
        # Create the original and edited articles to be used by the GUI
        
        self.source = Article()
        self.working = Article()  
        ignore = False
        
            
        themes = IO_Manager().get_themes()
        if _("Wikipedia Articles") in themes:
            i = themes.index(_("Wikipedia Articles"))
            del themes[i]
            
        wikiarticles = IO_Manager().get_pages_in_theme(_("Wikipedia Articles"))
        for theme in themes:
            articles = IO_Manager().get_pages_in_theme(theme)
            for article in articles:
                if ignore == True:
                    break
                for wikiarticle in wikiarticles:
                    if article in wikiarticle:
                        self.source = IO_Manager().load_article(wikiarticle, _("Wikipedia Articles"))
                        self.working = IO_Manager().load_article(article, theme) 
                        logger.debug("loading source %s from %s" %
                                (wikiarticle, "Wikipedia Articles"))
                        logger.debug("loading edit %s from %s" %
                                (article, theme))
                        ignore = True
        
        self.currentpane = None
        
        self.library.panel.connect("key-press-event", self.go_arrange_mode, None)
                        
        # Add toolbars and panels but keep hidden]
        toolbars = [pane.toolbar for pane in self.panes]
        toolbarnames = [pane.name for pane in self.panes]
        self.settoolbars(toolbars, toolbarnames)
        
        # Set the current index to -1 so that the first pane will always be shown
        self.currentindex = -1
        
    """
    Respond to function key presses
    """
    def go_arrange_mode(self, widget, event, data):
        key = event.keyval
        if key == gtk.keysyms.F1:
            logger.debug("f1")
            self.switch_page(0)
        if key == gtk.keysyms.F2:
            logger.debug("f2")
            self.switch_page(1)
        if key == gtk.keysyms.F3:
            logger.debug("f3")
            self.switch_page(2)
            
    """
    Save and quit current article
    """
    def do_quit_event(self):
        logger.debug("quitting")
        article = self.currentpane.get_working_article()
        IO_Manager().save_article(article)
