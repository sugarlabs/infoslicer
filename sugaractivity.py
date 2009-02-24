# Copyright (C) IBM Corporation 2008

import gtk
from Infoslicer_GUI import Infoslicer_GUI
from sugar.activity import activity
from gettext import gettext as _
from Processing.IO_Manager import IO_Manager 

class sugaractivity( activity.Activity, Infoslicer_GUI ):
    """
    Created by Jonathan Mace
    
    This is the Sugar implementation of the infoslicer GUI.
    
    It sets things in the sugar.activity class in the abstract methods. 
    """
    
    """
    Set up Sugar specific GUI config and show interface
    """
    def __init__(self, handle):
        activity.Activity.__init__(self, handle)
        gtk.gdk.threads_init()
        gtk.gdk.threads_enter()
        self.toolbox = activity.ActivityToolbox(self)
        Infoslicer_GUI.__init__(self)
        self._name = handle
        self.toolbox.connect("current-toolbar-changed", self.page_switched, None)
        
        self.set_title(_('InfoSlicer'))
        
        self.set_toolbox(self.toolbox)
        self.toolbox.show() 
        
        self.show_all()
        self.toolbox.set_current_toolbar(2)
        
        print "dictionary:"
        print handle.get_dict()
        
    """
    Operating system specific file reading and writing methods are below
    """
    def read_file(self, file_path):
        print "reading the file"
        """ 
        At the moment, the format of a saved file will just be:
        sourcetitle
        edittitle
        edittheme
        currentindex
        """
        
        file = open(file_path, 'r')
        text = file.read()
        file.close()
        lines = text.splitlines()
        if len(lines) < 3:
            return
        sourcetitle = lines[0]
        workingtitle = lines[1]
        workingtheme = lines[2]
        currentindex = lines[3]
        
        print "file read"
        print "sourcetitle: %s, workingtitle: %s, workingtheme: %s, currentindex: %s" % (sourcetitle, workingtitle, workingtheme, currentindex)
        iomanager = IO_Manager()
        if iomanager.page_exists(sourcetitle, "Wikipedia Articles"):
            sourcearticle = iomanager.load_article(sourcetitle, "Wikipedia Articles")
        else:
            sourcearticle = Article()
            sourcearticle.article_title = sourcetitle
            sourcearticle.article_theme = "Wikipedia Articles"
        if iomanager.page_exists(workingtitle, workingtheme):
            workingarticle = iomanager.load_article(workingtitle, workingtheme)
        else:
            workingarticle = Article()
            workingarticle.article_title = workingtitle
            workingarticle.article_theme = workingtheme
        
        self.switch_page(currentindex)
        
        self.currentpane.set_source_article(sourcearticle)
        self.currentpane.set_working_article(workingarticle)
    
    def write_file(self, file_path):
        print "writing the file to %s" % file_path
        sourcearticle = self.currentpane.get_source_article()
        workingarticle = self.currentpane.get_working_article()
        
        sourcetitle = sourcearticle.article_title
        if not sourcetitle:
            sourcetitle = "none"
        workingtitle = workingarticle.article_title
        if not workingtitle:
            workingtitle = "none"
        workingtheme = workingarticle.article_theme
        if not workingtheme:
            workingtheme = "none"
        currentindex = self.currentindex
        
        file = open(file_path, 'w')
        print "writing source: %s, working: %s, theme: %s" % (sourcetitle, workingtitle, workingtheme)
        file.write("%s\n%s\n%s\n%s" % (sourcetitle, workingtitle, workingtheme, str(currentindex)))
        file.close()
        
        
        
    def settoolbars(self, toolbars, toolbarnames):
        for i in range(0, len(toolbars)):
            self.toolbox.add_toolbar(toolbarnames[i], toolbars[i])
            toolbars[i].show()
        
            
    def setpanel(self, panel):
        self._main_view = panel
        self.set_canvas(self._main_view)
        self._main_view.show()
        
        
    def page_switched(self, widget, page_num, data):
        print "page_switched to %s" % (page_num, )
        if page_num > 0:
            self.mode_switched(page_num - 1)
        
    def switch_page(self, page_num):
        self.mode_switched(page_num)
        
    def can_close(self):
        self.do_quit_event()
        return True
