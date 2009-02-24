# Copyright (C) IBM Corporation 2008 
import pygtk
pygtk.require('2.0')
import gtk
import pango
import cPickle
import time
from threading import Timer
from Processing.IO_Manager import *
from Processing.Article.Article import Article
from Processing.Article.Article_Data import *
from GUI_Components.Compound_Widgets.Base_Widgets.Readonly_Textbox import Readonly_Textbox
import logging

logger = logging.getLogger('infoslicer')
elogger = logging.getLogger('infoslicer::except')

theme_xpm = [
"16 16 4 1",
"       c None s None",
".      c black",
"g      c #62F24D",
"G      c black",
"     .......... ",
"     .gggggggg. ",
"   ..........g. ",
"   .gggggggg.g. ",
" ..........g.g. ",
" .gggggggg.g.g. ",
" .gGGGgggg.g.g. ",
" .gggggggg.g.g. ",
" .gGGGGGGg.g.g. ",
" .gggggggg.g.g. ",
" .gGGGGGGg.g.g. ",
" .gggggggg.g... ",
" .gGGGGGGg.g.   ",
" .gggggggg...   ",
" .gGGGGGGg.     ",
" ..........     "]

newtheme_xpm = [
"16 16 4 1",
"       c None s None",
".      c black",
"g      c white",
"G      c black",
"     .......... ",
"     .gggggggg. ",
"   ..........g. ",
"   .gggggggg.g. ",
" ..........g.g. ",
" .gggggggg.g.g. ",
" .gggggggg.g.g. ",
" .gggggggg.g.g. ",
" .gggggggg.g.g. ",
" .gggggggg.g.g. ",
" .gggggggg.g.g. ",
" .gggggggg.g... ",
" .gggggggg.g.   ",
" .gggggggg...   ",
" .gggggggg.     ",
" ..........     "]

wikitheme_xpm = [
"16 16 4 1",
"       c None s None",
".      c black",
"g      c #FC8B65",
"G      c black",
"     .......... ",
"     .gggggggg. ",
"   ..........g. ",
"   .gggggggg.g. ",
" ..........g.g. ",
" .gggggggg.g.g. ",
" .gGGGgggg.g.g. ",
" .gggggggg.g.g. ",
" .gGGGGGGg.g.g. ",
" .gggggggg.g.g. ",
" .gGGGGGGg.g.g. ",
" .gggggggg.g... ",
" .gGGGGGGg.g.   ",
" .gggggggg...   ",
" .gGGGGGGg.     ",
" ..........     "]

mytheme_xpm = [
"16 16 4 1",
"       c None s None",
".      c black",
"g      c #E6E6E6",
"G      c #080808",
"     .......... ",
"     .gggggggg. ",
"   ..........g. ",
"   .gggggggg.g. ",
" ..........g.g. ",
" .gggggggg.g.g. ",
" .gGGGgggg.g.g. ",
" .gggggggg.g.g. ",
" .gGGGGGGg.g.g. ",
" .gggggggg.g.g. ",
" .gGGGGGGg.g.g. ",
" .gggggggg.g... ",
" .gGGGGGGg.g.   ",
" .gggggggg...   ",
" .gGGGGGGg.     ",
" ..........     "]

article_xpm = [
"16 16 4 1",
"       c None s None",
".      c black",
"g      c #62F24D",
"G      c black",
"  ............  ",
"  .gggggggggg.  ",
"  .GGGGgggggg.  ",
"  .gggggggggg.  ",
"  .gGGGGGGGGg.  ",
"  .gggggggggg.  ",
"  .gGGGGGGGGg.  ",
"  .gggggggggg.  ",
"  .gGGGGGGGGg.  ",
"  .gggggggggg.  ",
"  .gGGGGGGGGg.  ",
"  .gggggggggg.  ",
"  .gGGGGGGGGg.  ",
"  .gggggggggg.  ",
"  .gGGGGGGGGg.  ",
"  ............  ",
]

newarticle_xpm = [
"16 16 4 1",
"       c None s None",
".      c black",
"g      c white",
"G      c black",
"  ............  ",
"  .gggggggggg.  ",
"  .gggggggggg.  ",
"  .gggggggggg.  ",
"  .gggggggggg.  ",
"  .gggggggggg.  ",
"  .gggggggggg.  ",
"  .gggggggggg.  ",
"  .gggggggggg.  ",
"  .gggggggggg.  ",
"  .gggggggggg.  ",
"  .gggggggggg.  ",
"  .gggggggggg.  ",
"  .gggggggggg.  ",
"  .gggggggggg.  ",
"  ............  ",
]

wikiarticle_xpm = [
"16 16 4 1",
"       c None s None",
".      c black",
"g      c #FC8B65",
"G      c black",
"  ............  ",
"  .gggggggggg.  ",
"  .GGGGgggggg.  ",
"  .gggggggggg.  ",
"  .gGGGGGGGGg.  ",
"  .gggggggggg.  ",
"  .gGGGGGGGGg.  ",
"  .gggggggggg.  ",
"  .gGGGGGGGGg.  ",
"  .gggggggggg.  ",
"  .gGGGGGGGGg.  ",
"  .gggggggggg.  ",
"  .gGGGGGGGGg.  ",
"  .gggggggggg.  ",
"  .gGGGGGGGGg.  ",
"  ............  ",
]


class Library_View( gtk.HBox ):
    """
    Created by: Jonathan Mace
    
    Library View sets up the view to the library.
    It consists of 3 main widgets:
    1) Treeview widget
        This is populated with the themes and articles in the library.
        They can be renamed, new articles and themes can be added, and
        they can be moved about with drag and drop.
    2) Source-view widget
        This widget displays the current source article.  It is a drag
        destination for drags originating from the treeview.  Upon receiving
        a drag, it will load the appropriate article
    3) Edit-view widget
        This widget displays the current edit article.  It acts the same
        way as the source-view widget.
        
    A few minor things also exist, such as the creation of new blank articles
    and new blank themes if the user goes to editing mode without having anything
    selected.
    
    There is also a method for downloading new articles into the currently selected
    theme, which is activated by a button in the toolbar which is set up in the
    Library_Pane class.
    
    """
        
    # Create the icons
    themeicon = gtk.gdk.pixbuf_new_from_xpm_data(theme_xpm)
    articleicon = gtk.gdk.pixbuf_new_from_xpm_data(article_xpm)
    newarticleicon = gtk.gdk.pixbuf_new_from_xpm_data(newarticle_xpm)
    newthemeicon = gtk.gdk.pixbuf_new_from_xpm_data(newtheme_xpm)
    wikithemeicon = gtk.gdk.pixbuf_new_from_xpm_data(wikitheme_xpm)
    wikiarticleicon = gtk.gdk.pixbuf_new_from_xpm_data(wikiarticle_xpm)
    mythemeicon = gtk.gdk.pixbuf_new_from_xpm_data(mytheme_xpm)
    
    def __init__(self):
        self.ignore = True
            
        gtk.HBox.__init__(self)
        
        # First things first - make it look nice depending on the platform
        running_on = platform.system()
        self.colwidth = 250
        if running_on == "Linux" and "olpc" in platform.platform().lower():
                self.colwidth = 350
            
            
        #self.set_homogeneous(True)
        self.set_spacing(2)
        self.set_border_width(1)
        
        # Create the tree view, pack and show it
        self.treestore, self.treeview = self.__create_tree()
        self.treestorecontainer = gtk.ScrolledWindow()
        self.treestorecontainer.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.treestorecontainer.add(self.treeview)
        self.pack_start(self.treestorecontainer, False, False, 1)
        self.treestorecontainer.set_size_request(self.colwidth, -1)
        self.treestorecontainer.show_all()
        
        # Create a box for the textviews at the top and the status bar at the bottom
        maindisplay = gtk.VBox()
        maindisplay.set_spacing(2)
        self.pack_start(maindisplay)
        maindisplay.show()
        
        # Create a box for the two text views
        textviewbox = gtk.HBox()
        textviewbox.set_spacing(3)
        textviewbox.set_homogeneous(True)
        maindisplay.pack_start(textviewbox)
        textviewbox.show()
        
        # Create the status bar at the bottom of the page
        
        # Not bothering to show the statusbar
        statuseb = gtk.EventBox()
        statuseb.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#EEEEEE"))
        maindisplay.pack_start(statuseb, False, True, 0)
        statuseb.set_size_request(-1, 50)
        statuseb.show()
        
        self.statusbar = gtk.Label()
        statuseb.add(self.statusbar)
        self.statusbar.show()
        
        # Create the sourcepane label and textbox
        self.sourcepanebox = gtk.VBox()
        self.sourcepanebox.set_spacing(2)
        textviewbox.pack_start(self.sourcepanebox)
        self.sourcepanebox.show()
        
        labeleb = gtk.EventBox()
        labeleb.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#EEEEEE"))
        self.sourcepanebox.pack_start(labeleb, False, False, 0)
        labeleb.show()
        
        self.sourcepanelabel = gtk.Label()
        self.sourcepanelabel.set_justify(gtk.JUSTIFY_CENTER)
        self.sourcepanelabel.set_markup("<b>Wikipedia Article:</b>\n ")
        labeleb.add(self.sourcepanelabel)
        self.sourcepanelabel.show()
        
        
        sourcetextbox = gtk.ScrolledWindow()
        sourcetextbox.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        self.sourcepanebox.pack_start(sourcetextbox)
        sourcetextbox.show()
        
        self.sourcetext = Readonly_Textbox(False)
        self.sourcetext.set_editable(False)
        self.sourcetext.set_cursor_visible(False)
        self.sourcetext.connect("button-press-event", self.suppress, None)
        sourcetextbox.add(self.sourcetext)
        self.sourcetext.modify_font(pango.FontDescription('arial 9'))
        self.sourcetext.show()
        self.sourcetext.drag_dest_set(gtk.DEST_DEFAULT_ALL, [("sourcearticle", gtk.TARGET_SAME_APP, 0)], gtk.gdk.ACTION_COPY)
        
        
        # Create the editpane label and textbox
        self.editpanebox = gtk.VBox()
        self.editpanebox.set_spacing(2)
        textviewbox.pack_start(self.editpanebox)
        self.editpanebox.show()
        
        labeleb = gtk.EventBox()
        labeleb.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#EEEEEE"))
        self.editpanebox.pack_start(labeleb, False, False, 0)
        labeleb.show()
        
        self.editpanelabel = gtk.Label()
        self.editpanelabel.set_justify(gtk.JUSTIFY_CENTER)
        self.editpanelabel.set_markup("<b>My Article:</b>\n ")
        labeleb.add(self.editpanelabel)
        self.editpanelabel.show()
        
        edittextbox = gtk.ScrolledWindow()
        edittextbox.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        self.editpanebox.pack_start(edittextbox)
        edittextbox.show()
        
        self.edittext = Readonly_Textbox(False)
        self.edittext.set_editable(False)
        self.edittext.set_cursor_visible(False)
        self.edittext.connect("button-press-event", self.suppress, None)
        edittextbox.add(self.edittext)
        self.edittext.modify_font(pango.FontDescription('arial 9'))
        self.edittext.show()
        self.edittext.drag_dest_set(gtk.DEST_DEFAULT_ALL, [("editarticle", gtk.TARGET_SAME_APP, 0)], gtk.gdk.ACTION_COPY)
        
        
        
    def suppress(self, widget, event, data):
        widget.stop_emission("button-press-event")
        
    def __create_tree(self):
        """
        Written by: Jonathan Mace
        Last Modified: 22/08/2008
        This method sets up the tree structure used to browse topics and articles.
        It populates the treemodel, connects all the events together and then returns the treeview widget.
        """
        
        # Create and populate the treestore.
        # The first element is the text (so, topic title or article title).
        # The second element is the associated icon.
        # The third element is the type (so, theme or article)
        treestore = gtk.TreeStore(str, gtk.gdk.Pixbuf, str, str, bool)
        themes = IO_Manager().get_themes()
        if not "Wikipedia Articles" in themes:
            IO_Manager().add_theme_to_library("Wikipedia Articles")
            themes.append("Wikipedia Articles")
        if not "My Articles" in themes:
            IO_Manager().add_theme_to_library("My Articles")
            themes.append("My Articles")                
            
        for theme in themes:
            if theme == "Wikipedia Articles":
                themeiter = treestore.append(None, ["<b>%s</b>" % (theme, ), self.wikithemeicon, "wikitheme", "aaaaaaaaaaaaaaaaaaa", False])
                articles = IO_Manager().get_pages_in_theme(theme)
                for article in articles:
                    treestore.append(themeiter, [article, self.wikiarticleicon, "wikiarticle", article, False])
            elif theme == "My Articles":
                themeiter = treestore.append(None, ["<b>%s</b>" % (theme, ), self.mythemeicon, "mytheme", "aaaaaaaaaaaaaaaaaab", False])
                articles = IO_Manager().get_pages_in_theme(theme)
                for article in articles:
                    treestore.append(themeiter, [article, self.articleicon, "article", article, True])
                treestore.append(themeiter, ["<i>Create new article</i>", self.newarticleicon, "newarticle", "aaaaaaaaaaaaaaaaaaaa", True])
            else:
                themeiter = treestore.append(None, ["<b>%s</b>" % (theme, ), self.themeicon, "theme", theme, True])
                articles = IO_Manager().get_pages_in_theme(theme)
                for article in articles:
                    treestore.append(themeiter, [article, self.articleicon, "article", article, True])
                treestore.append(themeiter, ["<i>Create new article</i>", self.newarticleicon, "newarticle", "aaaaaaaaaaaaaaaaaaaa", True])
        treestore.append(None, ["<i>Create new theme</i>", self.newthemeicon, "newtheme", "zzzzzzzzzzzzzzzzz", True])
        treestore.set_sort_column_id(3, gtk.SORT_ASCENDING)

        # Create the treeview, set properties.
        treeview = gtk.TreeView(treestore)
        treeview.set_enable_search(False)
        treeview.set_headers_visible(False)
        treeview.set_reorderable(False)
        treeview.enable_model_drag_source(gtk.gdk.BUTTON1_MASK, [('text/plain', 0, 0), ("sourcearticle", gtk.TARGET_SAME_APP, 0), ("editarticle", gtk.TARGET_SAME_APP, 0)], gtk.gdk.ACTION_MOVE | gtk.gdk.ACTION_COPY)
        treeview.enable_model_drag_dest([('text/plain', 0, 0)], gtk.gdk.ACTION_MOVE)
        treeview.connect("drag-begin", self.drag_begin_event, None)
        treeview.connect("drag-drop", self.drag_drop_event, None)
        treeview.connect("drag-data-get", self.drag_data_get_event, None)
        treeview.connect("key-press-event", self.key_pressed, None)
        
        # Create the column to show the data, add to the treeview
        column = gtk.TreeViewColumn()
        treeview.append_column(column)
        
        # Create the cell renderers.  Set properties and add to the column
        iconcell = gtk.CellRendererPixbuf()
        
        cell = gtk.CellRendererText()
        cell.connect("edited", self.name_changed, None)
        
        
        column.pack_start(iconcell, False)
        column.set_attributes(iconcell, pixbuf=1)
        column.set_sort_column_id(0)
        
        column.pack_start(cell, True)
        cell.set_property("editable", True)
        column.set_attributes(cell, markup=0)
        
        path = (0, )
        iter = treestore.get_iter(path)
        path = treestore.get_path(iter)
        treeview.expand_to_path(path)
        
        return treestore, treeview
    
    
    def populate(self):
        # Remove and destroy the current contents of the panel
        self.remove(self.treestorecontainer)
        self.treestorecontainer.destroy()
            
        # Create the new tree view, pack and show it
        self.treestore, self.treeview = self.__create_tree()
        self.treestorecontainer = gtk.ScrolledWindow()
        self.treestorecontainer.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.treestorecontainer.set_size_request(self.colwidth, -1)
        self.treestorecontainer.add(self.treeview)
        self.pack_start(self.treestorecontainer, False, False, 0)
        self.reorder_child(self.treestorecontainer, 0)
        self.treestorecontainer.show_all()
        
    def add_theme_to_tree(self, theme):
        """ Adds a row to the tree with name 'theme'
        Note, that this does not save anything in the IO Manager
        """
        model = self.treestore
        model.append(None, ["<b>" + theme + "</b>", self.themeicon, "theme", theme, True])
        
    def add_article_to_tree(self, theme, title):
        """ Adds a row to the tree under theme 'theme' with title 'title'
        Note, that this does not save anything in the IO Manager
        A typical usage of this would be:
        
        IO_Manager().save_article(article)
        Library_View.add_article_to_tree(article.article_theme, article.article_title)
        Library_View.highlight_article(article.article_theme, article.article_title)
        """
        theme = "<b>%s</b>"%(theme,)
        model = self.treestore
        iter = model.get_iter_first()
        while iter != None:
            if model.get(iter, 0)[0] == theme:
                if theme == "Wikipedia Articles":
                    model.append(iter, [title, self.wikiarticleicon, "wikiarticle", title, True])
                else:
                    model.append(iter, [title, self.articleicon, "article", title, True])
                return
            else:
                iter = model.iter_next(iter)
        
    def article_exists_in_tree(self, theme, title):
        """ Returns true if the article specified exists in the tree structure.
        This is different to whether it exists as said by IO manager.
        Typical usage would be:
        
        IO_Manager().save_article(article)
        if not Library_View.article_exists_in_tree(article.article_theme, article.article_title):
            Library_View.add_article_to_tree(article.article_theme, article.article_title)
        Library_View.highlight_article(article.article_theme, article.article_title)
        
            
        
        """
        
        theme = "<b>%s</b>"%(theme,)
        iter = self.treestore.get_iter_first()
        while iter != None:
            if self.treestore.get(iter, 0)[0] == theme:
                break
            else:
                iter = self.treestore.iter_next(iter)
        if iter == None:
            return False
        iter = self.treestore.iter_children(iter)
        while iter != None:
            if self.treestore.get(iter, 0)[0] == title:
                return True
            else:
                iter = self.treestore.iter_next(iter)
        return False
        
        
    def highlight_theme(self, title):
        # Highlights the theme specified by title
        title = "<b>%s</b>"%(title,)
        iter = self.treestore.get_iter_first()
        while iter != None:
            if self.treestore.get(iter, 0)[0] == title:
                destpath = self.treestore.get_path(iter)
                self.treeview.set_cursor(destpath, None, True)
                return
            else:
                iter = self.treestore.iter_next(iter)
                
    def highlight_article(self, theme, title):
        # Expands the theme specified by theme and highlights
        # the article within this theme, specified by title.
        theme = "<b>%s</b>"%(theme,)
        iter = self.treestore.get_iter_first()
        while iter != None:
            if self.treestore.get(iter, 0)[0] == theme:
                break
            else:
                iter = self.treestore.iter_next(iter)
        if iter == None:
            return
        iter = self.treestore.iter_children(iter)
        while iter != None:
            if self.treestore.get(iter, 0)[0] == title:
                destpath = self.treestore.get_path(iter)
                self.treeview.expand_to_path(destpath)
                self.treeview.set_cursor(destpath, None, True)
                return
            else:
                iter = self.treestore.iter_next(iter)
                
    def get_current_selection_type(self):
        # Returns one of 'article', 'newarticle', 'theme', 'newtheme' or None
        # depending on which element of the tree is selected.
        model, sourceiter = self.treeview.get_selection().get_selected()
        if sourceiter == None:
            return None
        else:
            type = model.get(sourceiter, 2)
            return type
    
    def get_current_theme(self):
        # Returns the current theme if one is selected,
        # otherwise returns none.
        model, sourceiter = self.treeview.get_selection().get_selected()
        if sourceiter == None:
            return None
        title, type = model.get(sourceiter, 0, 2)
        if type == "theme" or type == "wikitheme" or type == "mytheme":
            return title[3:len(title)-4]
        elif type == "article" or type == "newarticle" or type == "wikiarticle":
            theme = model.get(model.get_iter(model.get_path(sourceiter)[0]), 0)[0]
            theme = theme[3:len(theme)-4]   
            return theme
        else:
            return None
    
    def get_current_article(self):
        # Returns the current article if one is selected,
        # otherwise returns none.
        model, sourceiter = self.treeview.get_selection().get_selected()
        if sourceiter == None:
            return None
        title, type = model.get(sourceiter, 0, 2)
        if type == "article" or type == "wikiarticle":
            return title
        else:
            return None   
        
    def set_status(self, status):
        pass
        
        
    def key_pressed(self, widget, event, data):
        # We want the delete key to do something.
        key = event.keyval
        if key == 65535 or key == 65288 or key == 65307:
            model, sourceiter = self.treeview.get_selection().get_selected()
            if sourceiter == None:
                return
            data = model.get(sourceiter, 0, 1, 2)
            title = data[0]
            type = data[2]
            
            if type == "newarticle" or type == "newtheme" or type == "mytheme" or type == "wikitheme":
                # If the current selection is a "Create new article" or "Create new theme" field then we ignore the keypress
                return
            
            if type == "article" or type == "wikiarticle":
                title = data[0]
                theme = model.get(model.get_iter(model.get_path(sourceiter)[0]), 0)[0]
                theme = theme[3:len(theme)-4]
                
                # Delete the article from the theme
                IO_Manager().remove_page(title, theme)
                
                # If the source/working articles are this one then we remove them
                source = self.sourcetext.get_article()
                working = self.edittext.get_article()
                if source != None and source.article_title == title and source.article_theme == theme:
                    self.sourcepanelabel.set_markup("<b>Wikipedia Article:</b>\n ")
                    self.sourcetext.set_article(Article())
                if working != None and working.article_title == title and working.article_theme == theme:
                    self.editpanelabel.set_markup("<b>My Article:</b>\n ")
                    self.edittext.set_article(Article())
                
                # Remove the article from the tree view
                self.treestore.remove(sourceiter)
                
                # Highlight the theme
                destpath = self.treestore.get_path(sourceiter)
                if destpath == None:
                    self.highlight_theme(theme)
                else:
                    self.treeview.set_cursor(destpath, None, True)
                
            elif type == "theme":
                theme = data[0]
                theme = theme[3:len(theme)-4]
                
                # Delete the theme from the filesystem
                IO_Manager().remove_theme(theme)
                
                # Remove the theme from the tree view
                destpath = self.treestore.get_path(sourceiter)
                self.treestore.remove(sourceiter)
                
                # If the source/working articles are in this theme then we remove them
                source = self.sourcetext.get_article()
                working = self.edittext.get_article()
                if working != None and working.article_theme == theme:
                    self.editpanelabel.set_markup("<b>My Article:</b>\n ")
                    self.edittext.set_article(Article())
                
                # Highlight the next theme
                if destpath != None:
                    self.treeview.set_cursor(destpath, None, True)
                
                self.set_status("Theme %s deleted" % (theme, ))
                
    
    def name_changed(self, renderer, path, newtext, data):
        # Disallowed chars are < > and &
        if newtext == "" or newtext.isspace() or '&' in newtext or '<' in newtext or '>' in newtext:
            return
        
        newtext = newtext
        model, sourceiter = self.treeview.get_selection().get_selected()
        data = model.get(sourceiter, 0, 1, 2)
        title = data[0]
        type = data[2]
        if type == "article":
            """ Rename the selected article """
            
            # Find the source theme and strip formatting tags
            sourcetheme = model.get(model.get_iter(model.get_path(sourceiter)[0]), 0)[0]
            sourcetheme = sourcetheme[3:len(sourcetheme)-4]
            
            # Reset the name in the source/working articles if appropriate
            source = self.sourcetext.get_article()
            edit = self.edittext.get_article()
            if source and source.article_title == title and source.article_theme == sourcetheme:
                logger.debug("setting source title")
                source.article_title = newtext
                self.sourcepanelabel.set_markup("<b>Copy from: </b> %s\n "%(newtext, ))
            if edit and edit.article_title == title and edit.article_theme == sourcetheme:
                logger.debug("setting edit title")
                edit.article_title = newtext
                self.editpanelabel.set_markup("<span size='medium'><b>Theme: </b> %s   \n<b>Article to edit: </b> %s</span>"%(sourcetheme, newtext))
            
            # If there is already an article with the new name in the theme, then we ignore the name change and highlight the existing article
            if IO_Manager().page_exists(newtext, sourcetheme):
                self.highlight_article(sourcetheme, newtext)
                return
            
            # Rename the page with IO Manager
            IO_Manager().rename_page(sourcetheme, title, newtext)
            
            # Set text on row to new text
            iter = model.get_iter(path)
            model.set(iter, 0, newtext)
            model.sort_column_changed()
            self.set_status("Article %s renamed to %s in theme %s" % (title, newtext, sourcetheme))
        elif type == "theme":
            """ Rename the selected theme """
            
            # Strip formatting tags
            title = title[3:len(title)-4]
            
            # Reset the theme in the source/working articles if appropriate
            source = self.sourcetext.get_article()
            edit = self.edittext.get_article()
            if source and source.article_theme == title:
                logger.debug("setting source theme")
                source.article_theme = newtext
            if edit and edit.article_theme == title:
                logger.debug("setting edit theme")
                edit.article_theme = newtext   
                self.editpanelabel.set_markup("<span size='medium'><b>Theme: </b> %s   \n<b>Article to edit: </b> %s</span>"%(edit.article_theme, edit.article_title))         
            
            # If there is already a theme with the new name, then we ignore the name change and highlight the existing theme
            if IO_Manager().theme_exists(newtext):
                self.highlight_theme(newtext)
                return
            
            # Rename theme in IO Manager
            IO_Manager().rename_theme(title, newtext)
            
            # Set text on row to the new text (otherwise it would revert back)
            iter = model.get_iter(path)
            model.set(iter, 0, "<b>%s</b>"%(newtext,))
            model.sort_column_changed()
            self.set_status("Theme %s renamed to %s" % (title, newtext))
        elif type == "newarticle":
            
            """ Creating a new article """
            
            if newtext.find("Create new article") != -1:
                # If the contents of the text box haven't changed, then
                # we don't want to do anything.
                return
            
            # Find the source theme and strip formatting tags
            sourceiter = model.get_iter(model.get_path(sourceiter)[0])
            sourcetheme = model.get(sourceiter, 0)[0]
            sourcetheme = sourcetheme[3:len(sourcetheme)-4]
            
            # If there is already a page with the title, we ignore the new article request and highlight the existing article
            if IO_Manager().page_exists(newtext, sourcetheme):
                self.highlight_article(sourcetheme, newtext)
                return
            
            # Create blank article
            data = Article_Data(self, article_title = newtext, article_theme = sourcetheme)
            article = Article(data)
            
            # Save article with IO manager
            IO_Manager().save_article(article)
            
            # Add new row for article
            destiter = model.append(sourceiter, [newtext, self.articleicon, "article", newtext, True])
            
            # Highlight new row
            destpath = model.get_path(destiter)
            self.treeview.set_cursor(destpath, None, True)
            self.set_status("New article '%s' created in theme %s" % (newtext, sourcetheme))
            
        elif type == "newtheme":
            """ Creating a new theme """
            
            if newtext.find("Create new theme") != -1:
                # If the contents of the text box haven't changed, then we don't want to do anything
                return
            
            try:
                # Create new topic in IO manager
                IO_Manager().add_theme_to_library(newtext)
                
                # Add new row for theme
                themeiter = model.append(None, ["<b>%s</b>" % (newtext, ), self.themeicon, "theme", newtext, True])
                model.append(themeiter, ["<i>Create new article</i>", self.newarticleicon, "newarticle", "aaaaaaaaaaaaaaaaaaaa", True])
                
            except theme_exists_error, e:
                elogger.debug('name_changed: %s' % e)
                # If the theme already exists, then we proceed to just highlight it.
                self.highlight_theme(newtext)
                return
            
            # Highlight new theme
            destpath = model.get_path(themeiter)
            self.treeview.expand_to_path(destpath)
            self.treeview.set_cursor(destpath, None, True)
            self.set_status("New theme '%s' created" % (newtext, ))
        
    def drag_begin_event(self, widget, context, data):
        # This just aborts the drag if the user attempts to drag a theme.
        model, sourceiter = widget.get_selection().get_selected()
        type = model.get(sourceiter, 2)[0]
        if type != "article" and type != "newarticle" and type != "wikiarticle":
            context.drag_abort(int(time.time()))
    
    def drag_drop_event(self, widget, context, x, y, time, data):
        """
        This method moves the source article to the topic that the user
        has dragged it to.
        """
        # First, retrieve the initial selection
        model, sourceiter = widget.get_selection().get_selected()
        data = model.get(sourceiter, 0, 1, 2, 3, 4)
        title = data[0]
        type = data[2]
        
        # The source theme is the label of the first node along the path to the current selection
        sourcetheme = model.get(model.get_iter(model.get_path(sourceiter)[0]), 0)[0]
            # Strip bold tags
        sourcetheme = sourcetheme[3:len(sourcetheme)-4]
        
        # Check the type, if the user didn't drag an article, we ignore
        if type == "article":
            # Work out the destination
            destrow = widget.get_dest_row_at_pos(x, y)
            destiter = model.get_iter((destrow[0][0], ))
            destpath = (destrow[0][0], 0)            
            # Strip bold tags
            desttheme = model.get(destiter, 0)[0]
            desttheme = desttheme[3:len(desttheme)-4]
            
            # If the theme already has an article with the name, we do nothing, and highlight the article
            # in the destination theme
            if IO_Manager().page_exists(title, desttheme):
                self.highlight_article(desttheme, title)
                return
            

            
            # If the destination is the "Create new theme" bit, then
            # we create a new theme and put the article in the new theme
            if desttheme == "Wikipedia Articles":
                return
            elif desttheme == "Create new theme":
                themes = IO_Manager().get_themes()
                desttheme = "New Theme 1"
                i = 1
                while desttheme in themes:
                    i = i + 1
                    desttheme = "New Theme %d" % (i,)
                IO_Manager().add_theme_to_library(desttheme)
                
                # Add new row for theme
                destiter = model.append(None, ["<b>%s</b>" % (desttheme, ), self.themeicon, "theme", desttheme, True])
                model.append(destiter, ["<i>Create new article</i>", self.newarticleicon, "newarticle", "aaaaaaaaaaaaaaaaaaaa", True])
            
            # Re-jig the rows on the visual side of things
            destiter = self.treestore.insert(destiter, 0, data)
            self.treestore.remove(sourceiter)
            self.treeview.set_model(self.treestore)
    
            
            # Re-jig the files in the filesystem
            IO_Manager().move_page(sourcetheme, desttheme, title)
            
            # Reset the topic in the source/working articles if appropriate
            source = self.sourcetext.get_article()
            edit = self.edittext.get_article()
            if edit != None and edit.article_title == title and edit.article_theme == sourcetheme:
                logger.debug("setting edit title")
                edit.article_theme = desttheme
                self.editpanelabel.set_markup("<span size='medium'><b>Theme: </b> %s   \n<b>Article to edit: </b> %s</span>"%(desttheme, title))            
            
            # Highlight the result of the drag
            destpath = model.get_path(destiter)
            self.treeview.expand_to_path(destpath)
            self.treeview.set_cursor(destpath, None, True)
            self.set_status("Article %s moved from %s to %s" % (title, sourcetheme, desttheme))
        elif type == "wikiarticle":
            # Work out the destination
            destrow = widget.get_dest_row_at_pos(x, y)
            destiter = model.get_iter((destrow[0][0], ))
            destpath = (destrow[0][0], 0)            
            # Strip bold tags
            desttheme = model.get(destiter, 0)[0]
            desttheme = desttheme[3:len(desttheme)-4]
            # Strip the "from en.wikipedia.org" or equivalent name
            i = title.find(" (from ")
            newtitle = title[0:i]
            
            i = 0
            temptitle = newtitle
            while IO_Manager().page_exists(temptitle, desttheme):
                temptitle = "%s %d" % (newtitle, i)
                
            newtitle = temptitle
            
            # If the theme already has an article with the name, we do nothing, and highlight the article
            # in the destination theme
            if IO_Manager().page_exists(newtitle, desttheme):
                self.highlight_article(desttheme, newtitle)
                return
            

            
            # If the destination is the "Create new theme" bit, then
            # we create a new theme and put the article in the new theme
            if desttheme == "Wikipedia Articles":
                return
            elif desttheme == "Create new theme":
                themes = IO_Manager().get_themes()
                desttheme = "New Theme 1"
                i = 1
                while desttheme in themes:
                    i = i + 1
                    desttheme = "New Theme %d" % (i,)
                IO_Manager().add_theme_to_library(desttheme)
                
                # Add new row for theme
                destiter = model.append(None, ["<b>%s</b>" % (desttheme, ), self.themeicon, "theme", desttheme, True])
                model.append(destiter, ["<i>Create new article</i>", self.newarticleicon, "newarticle", "aaaaaaaaaaaaaaaaaaaa", True])
            
            # Re-jig the rows on the visual side of things
            newdata = [newtitle, self.articleicon, "article", newtitle, True]
            destiter = self.treestore.insert(destiter, 0, newdata)
            self.treeview.set_model(self.treestore)
    
            # Re-jig the files in the filesystem
            IO_Manager().copy_page(title, sourcetheme, desttheme)
            IO_Manager().rename_page(desttheme, title, newtitle)
            
            # Reset the topic in the source/working articles if appropriate
            source = self.sourcetext.get_article()
            edit = self.edittext.get_article()            
            
            # Highlight the result of the drag
            destpath = model.get_path(destiter)
            self.treeview.expand_to_path(destpath)
            self.treeview.set_cursor(destpath, None, True)
            
    def drag_data_get_event(self, widget, context, selection_data, info, timestamp, data):
        model, sourceiter = self.treeview.get_selection().get_selected()
        type = model.get(sourceiter, 2)[0]
        target = selection_data.target
        if target == "sourcearticle":
            if type == "wikiarticle":
                atom = gtk.gdk.atom_intern("article")
                title = self.get_current_article()
                theme = self.get_current_theme()
                string = cPickle.dumps([title, theme])
                selection_data.set(atom, 8, string)
                self.sourcepanelabel.set_markup("<span size='medium'><b>Wikipedia Article: </b> \n%s</span> "%(title, ))
        elif target == "editarticle":        
            if type == "newarticle":
                # If the type is "newarticle" then we create a new article
                # and highlight it.
                
                # Create and save the new article
                theme = self.get_current_theme()
                i = 0
                title = "New Article"
                while IO_Manager().page_exists(title, theme):
                    i = i + 1
                    title = "New Article %d" % (i, )
                data = Article_Data(article_title = title, article_theme = theme)
                article = Article(data)
                IO_Manager().save_article(article)
                
                # Add the row to the tree model
                sourceiter = model.get_iter(model.get_path(sourceiter)[0])
                destiter = model.append(sourceiter, [title, self.articleicon, "article", title, True])
                
                # Highlight new row
                destpath = model.get_path(destiter)
                self.treeview.set_cursor(destpath, None, True)  
                
                # Set the selection data to the new article
                atom = gtk.gdk.atom_intern("article")
                string = cPickle.dumps([title, theme])
                selection_data.set(atom, 8, string)
                self.editpanelabel.set_markup("<span size='medium'><b>Theme: </b> %s   \n<b>Article to edit: </b> %s</span>"%(theme, title))
            elif type == "article":
                # If type is article, set the selection data to the theme and articlename
                atom = gtk.gdk.atom_intern("article")
                title = self.get_current_article()
                theme = self.get_current_theme()
                string = cPickle.dumps([title, theme])
                selection_data.set(atom, 8, string)
                self.editpanelabel.set_markup("<span size='medium'><b>Theme: </b> %s   \n<b>Article to edit: </b> %s</span>"%(theme, title))
            elif type == "wikiarticle":
                title = self.get_current_article()
                theme = self.get_current_theme()
                i = title.find(" (from ")
                newtitle = title[0:i]
                
                i = 0
                temptitle = newtitle
                while IO_Manager().page_exists(temptitle, "My Articles"):
                    i = i + 1
                    temptitle = "%s %d" % (newtitle, i)
                    
                newtitle = temptitle
                article = Article()
                article.article_title = newtitle
                article.article_theme = "My Articles"
                IO_Manager().save_article(article)
                
                
                sourceiter = model.get_iter((1,))
                destiter = model.append(sourceiter, [newtitle, self.articleicon, "article", newtitle, True])
                
                destpath = self.treestore.get_path(destiter)
                self.treeview.expand_to_path(destpath)
                self.treeview.set_cursor(destpath, None, True)
                
                self.sourcetext.set_article(IO_Manager().load_article(title, "Wikipedia Articles"))
                self.sourcepanelabel.set_markup("<span size='medium'><b>Wikipedia Article: </b> \n%s</span> "%(title, ))
                
                
                atom = gtk.gdk.atom_intern("article")
                string = cPickle.dumps([newtitle, "My Articles"])
                selection_data.set(atom, 8, string)
                self.editpanelabel.set_markup("<span size='medium'><b>Theme: </b> %s   \n<b>Article to edit: </b> %s</span>"%("My Articles", newtitle))
                
        else:
            # No data so nothing happens
            pass
        

    def commence_retrieval(self, widget, entry, statuslabel, wikimenu, wikidictionary):
        title = entry.get_text()
        wiki = wikidictionary[wikimenu.get_active_text()]
        theme = "Wikipedia Articles"
        if title == "" or title == None:
            return
        if IO_Manager().page_exists("%s (from %s)"%(title, wiki), theme):
            statuslabel.set_label("%s already exists" % (title, ))
            t = Timer(10, self.clear_label, [statuslabel])
            t.start()
        else:
            t = Timer(0, self.download_and_add, [title, theme, wiki, statuslabel])
            t.start()
        #self.download(title, theme)

                    
    def download_and_add(self, title, theme, wiki, statuslabel):                        
        #exceptions handled by IO_Manager
        try:
            statuslabel.set_label("Downloading %s..."%(title,))
            IO_Manager().download_wiki_article(title=title, theme=theme, wiki = wiki, statuslabel=statuslabel)
        except PageNotFoundError, e:
            elogger.debug('download_and_add: %s' % e)
            statuslabel.set_label("%s could not be found."%(title, ))
            return
        except Exception, e:
            elogger.debug('download_and_add: %s' % e)
            statuslabel.set_label("Error downloading %s. Check your connection."%(title, ))
            return
        
        model = self.treeview.get_model()
        
        wikipath = (0, )
        wikiiter = model.get_iter(wikipath)
        destiter = model.append(wikiiter, ["%s (from %s)"%(title, wiki), self.wikiarticleicon, "wikiarticle", "%s (from %s)"%(title, wiki), False])

        destpath = model.get_path(destiter)
        self.treeview.expand_to_path(destpath)     
        
        statuslabel.set_markup("%s successfully downloaded." % (title, ))
        t = Timer(10, self.clear_label, [statuslabel])
        t.start()
    
    def clear_label(self, label):
        label.set_markup("")
                            
            
    def set_source(self, article):
        # Set the article in the source pane to 'article'
        title = article.article_title
        buf = article.getBuffer()
        text = buf.get_slice(buf.get_start_iter(), buf.get_end_iter())
        if article.article_title != None and text != "" and article.article_theme == "Wikipedia Articles":
            self.sourcetext.set_article(article)
            self.sourcepanelabel.set_markup("<b>Wikipedia Article: </b> \n%s "%(title, ))
        else:
            self.sourcetext.set_article(Article())
        self.sourcetext.set_editable(False)
        self.sourcetext.set_cursor_visible(False)
            
    def get_source(self):
        """ 
        This returns the currently selected source article.
        If the selected source article is from a different theme to the currently
        selected edit article, then the article theme is changed.  This only
        a temporary change and since it is a source article it is read only
        so it will never be saved.
        New themes / articles are created and loaded in the event that
        nothing is currently selected.
        """
        currentarticle = self.sourcetext.get_article()
        if not currentarticle or not currentarticle.article_title or currentarticle.article_title == "":
            article = Article()
        else:
            article = currentarticle
        article.article_theme == "Wikipedia Articles"
        return article
        
        
    def set_working(self, article):
        # Set the working article to 'article'
        theme = article.article_theme
        title = article.article_title
        buf = article.getBuffer()
        text = buf.get_slice(buf.get_start_iter(), buf.get_end_iter())
        if text:
            logger.debug("article has text")
            if not theme:
                theme = "My Articles"
            if not title:
                i = 0
                title = "New Article"
                while IO_Manager().page_exists(title, theme):
                    i = i + 1
                    title = "New Article %s" % (i, )
        else:
            if title and theme and "New Article" in title and not IO_Manager().page_exists(title, theme):
                title == None
        if theme and title and theme != "Wikipedia Articles":
            if not self.article_exists_in_tree(theme, title):
                self.add_article_to_tree(theme, title)
            IO_Manager().save_article(article)
            self.highlight_article(theme, title)
            self.edittext.set_article(article)
            self.editpanelabel.set_markup("<span size='medium'><b>Theme: </b> %s   \n<b>Article to edit: </b> %s</span>"%(theme, title))
        
        self.sourcetext.set_editable(False)
        self.sourcetext.set_cursor_visible(False)
        
    def get_working(self):
        # Return the current working article, or create a new article in the current theme
        # if there is no current working article.
        currentarticle = self.edittext.get_article()
        if currentarticle != None:
            article = currentarticle
        else:
            article = Article()
        title = article.article_title
        theme = article.article_theme
        
        if not theme or theme == "":
            theme = "My Articles"
            article.article_theme = theme
        
        if not title or title == "":
            sourcearticle = self.sourcetext.get_article()
            if sourcearticle and sourcearticle.article_title:
                sourcetitle = sourcearticle.article_title
            else:
                sourcetitle = ""
            j = sourcetitle.find(" (from ")
            if j != -1:
                title = sourcetitle[0:j]
            else:
                title = "New Article"                
            articles = IO_Manager().get_pages_in_theme(theme)
            i = 0
            while title in articles:
                i = i + 1
                title = "New Article %d" % (i, )
            logger.debug(title)
            article.article_title = title
                    
        return article
