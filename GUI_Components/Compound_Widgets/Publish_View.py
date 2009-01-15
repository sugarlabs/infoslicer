# Copyright (C) IBM Corporation 2008 
import pygtk
pygtk.require('2.0')
import gtk
import cPickle
import pango
from Processing.IO_Manager import *
from Processing.Article.Article import Article
from Processing.Package_Creator import Package_Creator

class Publish_View( gtk.VBox ):
      
    def __init__(self):
        gtk.VBox.__init__(self)
        self.articlestocopy = []
        self.themeselected = ''
        running_on = platform.system()
        
        
        paddingbox = gtk.HBox()
        paddingbox.set_homogeneous(True)
        self.pack_start(paddingbox)
        self.child_set(paddingbox, "expand", True, "fill", True)
        paddingbox.show()
        
        pad1 = gtk.Label()
        paddingbox.pack_start(pad1)
        pad1.show()
        
        self.themeviewcontainer = gtk.VBox()
        self.themeviewcontainer.set_border_width(2)
        paddingbox.pack_start(self.themeviewcontainer)
        self.themeviewcontainer.show()
        
        pad2 = gtk.Label()
        paddingbox.pack_start(pad2)
        pad2.show()
        
        heading = gtk.Label("Click a theme:")
        self.themeviewcontainer.pack_start(heading, False, False, 5)
        heading.modify_font(pango.FontDescription('11'))
        heading.show()
        
        themeviewwindow = gtk.ScrolledWindow()
        themeviewwindow.set_border_width(2)
        themeviewwindow.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        self.themeviewcontainer.pack_start(themeviewwindow)        
        themeviewwindow.show()
        
        self.themeview = gtk.VBox()
        themeviewwindow.add_with_viewport(self.themeview)
        themeviewwindow.get_child().set_shadow_type(gtk.SHADOW_NONE)
        if running_on == "Linux" and "olpc" in platform.platform().lower():
            themeviewwindow.get_child().modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse('#c0c0c0'))
        self.themeview.show()
        
        self.articleviewcontainer = gtk.VBox()
        self.articleviewcontainer.set_border_width(2)
        self.pack_start(self.articleviewcontainer)
        self.articleviewcontainer.show()
        
        box = gtk.HBox()
        box.set_border_width(2)
        self.articleviewcontainer.pack_start(box)
        self.articleviewcontainer.child_set(box, "expand", False, "fill", False, "padding", 1)
        box.show()
               
        articleviewwindow = gtk.ScrolledWindow()
        articleviewwindow.set_border_width(2)
        articleviewwindow.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        self.articleviewcontainer.pack_start(articleviewwindow)
        articleviewwindow.show()
        
        self.articleview = gtk.VBox()
        articleviewwindow.add_with_viewport(self.articleview)
        articleviewwindow.get_child().set_shadow_type(gtk.SHADOW_NONE)
        if running_on == "Linux" and "olpc" in platform.platform().lower():
            articleviewwindow.get_child().modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse('#c0c0c0'))
        self.articleview.show()
        
        box2 = gtk.VBox()
        box2.set_border_width(2)
        self.articleviewcontainer.pack_start(box2)
        box2.show()
        
        box3 = gtk.HBox()
        box2.pack_start(box3)
        box3.show()        
        
        paddingbox = gtk.HBox()
        paddingbox.set_homogeneous(True)
        box3.pack_start(paddingbox)
        paddingbox.show()
        
        pad1 = gtk.Label()
        paddingbox.pack_start(pad1)
        pad1.show()
        
        
        
        self.exportbutton = gtk.Button('Publish')
        if running_on == "Linux" and "olpc" in platform.platform().lower():
            self.exportbutton.connect("clicked", self.sugarexport, self.articlestocopy)
        else:
            self.exportbutton.connect("clicked", self.export, self.articlestocopy)
        self.articleviewcontainer.child_set(box2, "expand", False, "fill", False, "padding", 1)
        paddingbox.pack_start(self.exportbutton)
        self.exportbutton.show()
        
        pad2 = gtk.Label()
        paddingbox.pack_start(pad2)
        pad2.show()
        
        if running_on == "Linux" and "olpc" in platform.platform().lower():
            None
        else:
            self.combobox = gtk.combo_box_new_text()
            self.combobox.append_text("Create Zip package")
            self.combobox.append_text("Create bundle for Sugar")
            self.combobox.set_active(0)
            self.combobox.show()
            box3.pack_start(self.combobox)
        
        self.export_message = gtk.Label('Select the theme you want, choose the articles you wish to include in the package and click "Publish".')
        self.export_message.show()
        box2.pack_start(self.export_message)
        
        self.populate_themes()
                
    def populate_themes(self):
        """
        Clears the topics in the Topic View and re-populates by retrieving the topics from the library using IO_Manager       
        """
        
        # Remove children currently in the topic view
        for child in self.themeview.get_children():
            self.themeview.remove(child)
            child.destroy()
        self.themebuttons = []
        
        # Get topics from IO_Manager
        themes = IO_Manager().get_themes()
 
        button = gtk.RadioButton(None, "Hidden button!", None)
        self.themeview.pack_start(button)
        self.themeview.child_set(button, "expand", False, "fill", False)
        button.connect("released", self.theme_selected, None)   
        self.themebuttons.append(button)
        group = button
#        button.show()        

        
        # For each topic in the library, we create a button to represent the topic in the topic view,
        # along with a button which will delete the topic when pressed.  When the delete button is pressed,
        # all the articles currently in the topic will be moved to the "Downloaded Articles" topic.
        # We also set the button to be a drag destination for dragging in articles.
        for theme in themes:
            box = gtk.HBox()
            self.themeview.pack_start(box)
            self.themeview.child_set(box, "expand", False, "fill", False)
            box.show()
            
            button = gtk.RadioButton(group, theme, None)
            box.pack_start(button)
            button.set_mode(False)
            button.set_relief(gtk.RELIEF_NONE)
            button.set_property("can-focus", False)
            box.child_set(button, "expand", True, "fill", True)
            button.connect("released", self.theme_selected, None)
            self.themebuttons.append(button)
            group = button
            button.show()
            
    def populate_articles(self, theme):
        """
        Clears the articles in the list and re-populates by retrieving the articles in the theme selected from the library
        using IO_Manager
        @param theme: the name of the topic whose articles are to be displayed      
        """
        
        # Remove everything in the article view
        for child in self.articleview.get_children():
            self.articleview.remove(child)
            child.destroy()
        self.articlebuttons = []
        
        # Retrieve the articles for the specified topic, using IO_Manager
        articles = IO_Manager().get_pages_in_theme(theme)
        if articles == []:
            return
        
        length = len(articles)
        wikiarticles = []
        realarticles = []
        for article in articles:
            if "(from en.wikipedia.org)" in article or "(From En.Wikipedia.Org)" in article:
                wikiarticles.append(article)
            else:
                realarticles.append(article)
        
        
        group = None
        
        # For each article, we package a button corresponding to the article, which when
        # pressed is equivalent to the article being "selected". Also, a delete button, to
        # delete the article, and then we also set it up as a drag source so that articles
        # can be dragged between topics.
        for article in realarticles:
            title = article[0]
            if title != "Blank Article":
                box = gtk.HBox()
                self.articleview.pack_start(box)
                self.articleview.child_set(box, "expand", False, "fill", False)
                box.show()
                
                button = gtk.CheckButton(article)
                button.set_mode(True)
                button.connect("toggled", self.checked, button.get_children()[0].get_text())
                button.set_active(True)
                box.pack_start(button)
                self.articlebuttons.append(button)
                group = button
                button.show()
                
        for article in wikiarticles:
            title = article[0]
            if title != "Blank Article":
                box = gtk.HBox()
                self.articleview.pack_start(box)
                self.articleview.child_set(box, "expand", False, "fill", False)
                box.show()
                
                button = gtk.CheckButton(article)
                button.set_mode(True)
                button.connect("toggled", self.checked, button.get_children()[0].get_text())
                button.set_active(False)
                box.pack_start(button)
                self.articlebuttons.append(button)
                group = button
                button.show()
    
    def checked(self, name, label):
        """
        Creates a list of articles to copy based on checked items
        @param name: Name of the object which called the function
        @param label: The name of the article to be added to the list
        """
        if name.get_active() == True:
            self.articlestocopy.append(label)
        else:
            self.articlestocopy.remove(label)
            
    def sugarexport(self, name, articlestocopy):
        """
        Creates a list of articles to copy based on checked items
        @param name: Name of the object which called the function
        @param articlestocopy: List of articles to copy
        """
        if not self.themeselected:
            self.export_message.set_text('You need to choose a theme to package first.')
        else:
            Package_Creator(self.articlestocopy, self.themeselected, None, 'xol', self)
    
    def export(self, name, articlestocopy):
        """
        Creates a list of articles to copy based on checked items
        @param name: Name of the object which called the function
        @param articlestocopy: List of articles to copy
        """
        #createPackage(self.articlestocopy, self.themeselected)
        #self.notexported.hide()
        #self.exported.show()
        
        if not self.themeselected:
            self.export_message.set_text('You need to choose a theme to bundle first.')
        else:
            combobox_choice = self.combobox.get_active_text()
            if combobox_choice == 'Create bundle for Sugar':
                package_type = 'xol'
            elif combobox_choice == 'Create Zip package':
                package_type = 'zip'
            self.filechooser = gtk.FileChooserDialog(title=None,action=gtk.FILE_CHOOSER_ACTION_SAVE,buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_SAVE,gtk.RESPONSE_OK))
            self.filechooser.set_do_overwrite_confirmation(True)
            self.filechooser.show()
            response = self.filechooser.run()
            
            if response == gtk.RESPONSE_OK:
                filename = self.filechooser.get_filename()
                filename = [filename]
                filename.append(package_type)
                full_filename = ".".join(filename)
                Package_Creator(self.articlestocopy, self.themeselected, full_filename, package_type)
                self.filechooser.destroy()
                self.export_message.set_text('Bundle created. It has been saved to %s' % full_filename)
            elif response == gtk.RESPONSE_CANCEL:
                self.filechooser.destroy()
    
    def destroy(self, widget):
        gtk.main_quit()
    
    def go_to_editpane(self, widget, event, data):
        if event.type == gtk.gdk._2BUTTON_PRESS:
            event = gtk.gdk.Event(gtk.gdk.KEY_PRESS)
            event.keyval = gtk.keysyms.F2
            event.time = 0 # assign current time
            self.emit('key_press_event', event)
            
    def highlight_theme(self, theme):
        for button in self.themebuttons:
            if button.get_label() == theme:
                self.theme_selected(button, None)
                button.clicked()
    
    def highlight_article(self, title):
        for button in self.articlebuttons:
            if button.get_label() == title:
                self.article_selected(button, None)
                button.clicked()
            
    def get_current_theme(self):
        for button in self.themebuttons:
            if button.get_active():
                return button.get_label()
            
    def get_current_theme_button(self):
        for button in self.themebuttons:
            if button.get_active():
                return button
            
    def set_source(self, article):
        article = Article()
        return article        
            
    def get_source(self):
        article = Article()
        return article
                
    def set_working(self, article):
        article = Article()
        return article           
        
    def get_working(self):
        article = Article()          
        return article

    def theme_selected(self, button, data):
        self.themeselected = button.get_label()
        self.articlestocopy = []
        self.populate_articles(self.themeselected)