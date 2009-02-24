# Copyright (C) IBM Corporation 2008

import gtk
from BeautifulSoup import Tag
from NewtifulSoup import NewtifulStoneSoup as BeautifulStoneSoup
import os, platform, urllib
from Article_Builder import Article_Builder
from Processing.Article.Article import Article
from MediaWiki_Helper import MediaWiki_Helper, PageNotFoundError
from MediaWiki_Parser import MediaWiki_Parser
import shutil
import re
import logging

logger = logging.getLogger('infoslicer')
elogger = logging.getLogger('infoslicer::except')

class theme_not_found_error(Exception):
    def __init__(self, value):
        self.parameter = value
    def __str__(self):
        return repr(self.parameter)

class page_not_found_error(Exception):
    def __init__(self, value):
        self.parameter = value
    def __str__(self):
        return repr(self.parameter)
    
class theme_exists_error(Exception):
    def __init__(self, value):
        self.parameter = value
    def __str__(self):
        return repr(self.parameter)
    
    
"""
This class sits between the GUI and the back end (handling 
mediawiki communication and raw pages/theme/article modifications)
"""    
class IO_Manager:
    
    def __init__(self):
        running_on = platform.system()
        if running_on == "Windows":
            # On Windows, used to save to a data subfolder of the folder that contains this code
            #self.workingDir = os.path.join(__file__.rsplit("\\", 1)[0], "Data")
            # but better to write to user home with os.getenv("USERPROFILE") or os.path.expanduser("~")
            self.workingDir = os.path.join(os.getenv("USERPROFILE"), ".slicedata")
        elif running_on == "Linux":
            if "olpc" in platform.platform().lower():
                from sugar.activity import activity
                # On Sugar, save to the data subfolder of the app directory
                self.workingDir =  os.path.join(activity.get_activity_root(), "data")
                logger.debug("Activity root is: %s" %
                        str(activity.get_activity_root()))
                logger.debug("Data folder is: %s" % self.workingDir)
            else:
                # On Linux, save to a .slicedata subdir of the user's homedir
                self.workingDir = os.path.join(os.getenv("HOME"), ".slicedata")
        self.proxies = {}
        proxy_file = os.path.join(os.path.split(os.path.split(__file__)[0])[0], 'proxy.cfg')
        if os.access(proxy_file, os.F_OK):
            proxy_file_handle = open(proxy_file, "r")
            for line in proxy_file_handle.readlines():
                parts = line.split(':', 1)
                #logger.debug("setting " + parts[0] + " proxy to " + parts[1])
                self.proxies[parts[0].strip()] = parts[1].strip()
            proxy_file_handle.close()
        if self.proxies == {}:
            self.proxies = None
    
    def clean_title(self, title):
        """
            removes non-alphanumeric chars from titles and lowercases it
        """
        logger.debug("Cleaning: " + title)
        output = re.sub(re.compile('\W'), "_", title).lower()
        logger.debug("Output: " + output)
        return output
    
    def install_library(self):
        if platform.system() == "Linux" and "olpc" in platform.platform().lower():
            file_list = [('Lion (from en.wikipedia.org)', os.path.join(os.path.split(__file__)[0], "demolibrary", "lion-wikipedia.dita"), 'Wikipedia Articles'), ('Tiger (from en.wikipedia.org)', os.path.join(os.path.split(__file__)[0], "demolibrary", "tiger-wikipedia.dita"), 'Wikipedia Articles'), ('Giraffe (from en.wikipedia.org)', os.path.join(os.path.split(__file__)[0], "demolibrary", "giraffe-wikipedia.dita"), 'Wikipedia Articles'), ('Giraffe', os.path.join(os.path.split(__file__)[0], "demolibrary", "giraffe-blank.dita"), 'My Articles'), ('Zebra (from en.wikipedia.org)', os.path.join(os.path.split(__file__)[0], "demolibrary", "zebra-wikipedia.dita"), 'Wikipedia Articles')]
            for file in file_list:
                if file[2] not in self.get_themes():
                    logger.debug("install library: creating theme %s" %
                            file[2])
                    self.add_theme_to_library(file[2])
                logger.debug("install library: opening %s" % file[1])
                open_file = open(file[1], "r")
                contents = open_file.read()
                open_file.close()
                if contents:
                    logger.debug("install library: content read sucessfully")
                logger.debug("install library: saving page %s" % file[0])
                self.save_page(file[0], contents, file[2], get_images=True)
                logger.debug("install library: save successful")
                                 
    def __add_page_to_library(self, title, path, theme="My Articles"):
        """
            Adds a page to the library. If a theme is specified it is added to that theme, otherwise it is put into the 'No Assigned Theme' theme.
            
            @param title: The title of the article to add to library.
            @param path: The path of the article to add to library.
            @param theme: Which theme to store the article in. (Optional, defaults to No Assigned Theme).
        """
        try:
            #change to relative path
            path = path.replace(os.path.join(self.workingDir, ""), "", 1)
            map = self.load_map(theme)
            existing_entry = map.find("topicref", attrs={"navtitle" : title})
            if existing_entry != None:
                existing_entry.extract()
            map.map.append(Tag(map, "topicref", [("href", path), ("navtitle", title)]))
            self.save_map(theme, map)
        except Exception, e:
            elogger.debug('__add_page_to_library: %s' % e)
            self.add_theme_to_library(theme)
            self.__add_page_to_library(title, path, theme)
        
    def add_theme_to_library(self, theme):
        """
            Adds themes to the library.
            @param theme: Theme to add.
            @raise theme_exists_error: If trying to add theme that already exists.
        """
        try:
            map = self.load_map("Library")
            # Ensure theme does not exist
            if map.find(attrs={"navtitle" : theme}) == None:
                # create a new entry in the library for the theme
                 map.map.append(Tag(map, "topicref", [("format", "ditamap"), ("href", "%s.ditamap" % self.clean_title(theme)), ("navtitle", theme)]))
                # save the theme file
                 self.__create_map(theme)
            else:
                raise theme_exists_error("Theme already exists")
            self.save_map("Library", map)
        except theme_not_found_error, e:
            elogger.debug('add_theme_to_library: %s' % e)
            # this error is caused by failing to open the library, so create the library and try again
            self.__create_map("Library")
            self.add_theme_to_library(theme)
                
    def __create_map(self, map_name):
        """
            Creates a new map for the specified theme name.
            @param map_name: name of map theme.
        """
        self.save_map(map_name, BeautifulStoneSoup(\
                '<?xml version="1.0" encoding="utf-8"?>\
                <!DOCTYPE map PUBLIC "-//IBM//DTD DITA IBM Map//EN" "ibm-map.dtd">\
                <map title="%s">\
                </map>' % map_name))
    
    def download_wiki_article(self, title, theme, wiki=None, statuslabel = None):
        """
            manages downloading and saving of wiki articles.
            @param title: Title of article to get
            @param theme: Theme to save to
            @param wiki: (optional) wiki to search - see MediaWiki helper for default behaviour
            @param statuslabel: gtk status label to write to

        """
        if statuslabel != None:
            statuslabel.set_label("%s download in progress..." % (title))
        if wiki == None:
            #article, url = MediaWiki_Helper().getArticleAsHTMLByTitle(title)
            wiki = "en.wikipedia.org"
        
        article, url = MediaWiki_Helper().getArticleAsHTMLByTitle(title, wiki)
        if statuslabel != None:
            statuslabel.set_label("Processing %s..." % (title))
        
        parser = MediaWiki_Parser(article, title, url)
        contents = parser.parse()
        #TODO: change line below when taking from other sources:
        self.save_page(title + " (from %s)" % wiki, contents, theme, False, True, statuslabel)
        if statuslabel != None:
                statuslabel.set_label("Done.")
#        unique=2
#        new_title = title.lower()
#        contents = self.image_handler(parser.parse(), title)
#        if not os.path.exists(os.path.join(self.workingDir, title.lower())):
#                os.makedirs(os.path.join(self.workingDir, title.lower()), 0777)
#        while os.access(os.path.join(self.workingDir, title.lower(), "%s.dita" % new_title), os.F_OK):
#            new_title = title.lower() + str(unique)
#            unique += 1
#        contents = contents.replace('<prolog>', '<prolog>\n<resourceid id="%d" />' % self.get_unique_article_ID(), 1)
#        file = open(os.path.join(self.workingDir, title.lower(), "%s.dita" % new_title), "w")
#        file.write(contents)
#        file.close()
    
    def get_pages_in_theme(self, theme):
        """
            Returns a list of all pages in the specified theme.
            @param theme: Theme to query
            @return: List of dictionaries containing page 'path' and 'title'.
        """
        try:
            map = self.load_map(theme)
        except Exception, e:
            elogger.debug('get_pages_in_theme: %s' % e)
            return []
        output = []
        for page in map.map.findAll("topicref"):
            output.append(page['navtitle'])
        output.sort()
        return output
            
    def get_themes(self):
        """
            Returns a list of all themes stored in the library.
            @return: List of theme names.
        """
        try:
            map = self.load_map("Library")
            output = []
            for theme in map.findAll("topicref"):
                output.append(theme["navtitle"])
            output.sort()
            return output
        except Exception, e:
            elogger.debug('get_themes: %s' % e)
            return []
    
    def get_unique_article_ID(self):
        """
            Creates and maintains a file to record the last unique article ID issued.
            when a new ID is requested, returns last id + 1 and upates file.
            @returns: Unique numeric ID
        """
        if not os.access(os.path.join(self.workingDir, "idfile"), os.F_OK):
            # if no ID file, take a guess at where to start numbering.
            id = 1
            # Worst case scenario is that every file is an article, so count all files
            for item in os.walk(self.workingDir):
                id += len(item[2])
            # Multiply by 1000 to prevent any problems caused by deleting files
            id = id * 1000
            logger.debug("ID FILE NOT FOUND, setting ID to " + str(id))
            id_file = open(os.path.join(self.workingDir, "idfile"), "w")
            id_file.write(str(id))
            id_file.close()
            return id
        else:
            id_file = open(os.path.join(self.workingDir, "idfile"), "r")
            id = long(id_file.read())
            id_file.close()
            id += 1
            id_file = open(os.path.join(self.workingDir, "idfile"), "w")
            id_file.write(str(id))
            id_file.close()
            return id          
        
    def image_handler(self, document, title, statuslabel=None):
        """
            Takes a DITA article and downloads images referenced in it (finding all <image> tags).
            Attemps to fix incomplete paths using source url.
            @param document: DITA to work on
            @param title: Title of article 
            @return: The document with image tags adjusted to point to local paths
        """
        document = BeautifulStoneSoup(document)
        dir_path =  os.path.join(self.workingDir, self.clean_title(title), "images")
        logger.debug(dir_path)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path, 0777)
        if statuslabel != None:
            i = title.find(" (from ")
            temptitle = title[0:i]
            statuslabel.set_label("Downloading %s images..." % (temptitle, ))
        for image in document.findAll("image"):
            fail = False
            path = image['href']
            if "#DEMOLIBRARY#" in path:
                path = path.replace("#DEMOLIBRARY#", os.path.join(os.path.split(__file__)[0], "demolibrary"))
                image_title = os.path.split(path)[1]
                shutil.copyfile(path, os.path.join(dir_path, image_title))
            else:
                image_title = path.rsplit("/", 1)[-1]
                # attempt to fix incomplete paths
                if (not path.startswith("http://")) and document.source != None and document.source.has_key("href"):
                    if path.startswith("/"):
                        path = document.source['href'].rsplit("/", 1)[0] + path
                    else:
                        path = document.source['href'].rsplit("/", 1)[0] + "/" + path
                logger.debug("Retrieving image: " + path)
                file = open(os.path.join(dir_path, image_title), 'wb')
                image_contents = self.__open_URL(path)
                if image_contents == None:
                    fail = True
                else:
                    file.write(image_contents)
                file.close()
            #change to relative paths:
            if not fail:
                image['href'] = os.path.join(dir_path.replace(os.path.join(self.workingDir, ""), "", 1), image_title)
            else:
                image.extract()
        return document.prettify()
              
    def load_map(self, map_name):
        """
            Loads the specified theme map.
            @param map_name: Name of theme map to load
            @return: map contents as a Soup
            @raise theme_not_found_error: If theme map not found.
        """
        if not os.access(os.path.join(self.workingDir, "%s.ditamap" % self.clean_title(map_name)), os.F_OK):
            raise theme_not_found_error("Theme '" + map_name + "' not found")
        file = open(os.path.join(self.workingDir, "%s.ditamap" % self.clean_title(map_name)), "r")
        map = BeautifulStoneSoup(file.read())
        file.close()
        return map
    
    def load_raw_page(self, title, theme):
        """
            Returns contents of specified page.
            
            @param title: Title of page to open.
            @param theme: Theme of page to open.
            @return: Contents of page.
        """
        theme_map = self.load_map(theme)
        logger.debug(title + theme)
        page_location = theme_map.find("topicref", attrs={ "navtitle" : title })
        if page_location != None:
            page_location = page_location['href']
        else:
            raise page_not_found_error("No match for " + title + " in " + theme)
        
        #if not os.access(page_location, os.F_OK):
        if os.access(os.path.join(self.workingDir, page_location), os.F_OK):
            page_location = os.path.join(self.workingDir, page_location)
        else:
            raise page_not_found_error("Page not found at " + page_location)
        page = open(page_location, "r")
        output = page.read()
        page.close()
        return output
        
    def load_page(self, title, theme):    
        return Article_Builder().get_article_from_dita(self.load_raw_page(title, theme))    
        
    def copy_page(self, title, fromtheme, totheme):
        """
            Copys a page from one theme to another. If no title specified, all pages in theme are moved.
            @param page_title: Title of page to move. (Optional, defaults to None)
            @param from_theme: Source theme.
            @param to_theme: Destination theme.  
        """
        logger.debug("COPY PAGE %s FROM %s TO %s" %
                (title, fromtheme, totheme))
        article = self.load_raw_page(title, fromtheme)
        self.save_page(title, article, totheme, overwrite=False)
        
    def load_article(self, title, theme):
        """
            loads the specified article
        """
        article_data = self.load_page(title, theme)
        article = Article(article_data)
        article.article_title = title
        article.article_theme = theme
        return article
    
    def move_page(self, from_theme, to_theme, page_title = None):
        """
            Moves a page from one theme to another. If no title specified, all pages in theme are moved.
            @param page_title: Title of page to move. (Optional, defaults to None)
            @param from_theme: Source theme.
            @param to_theme: Destination theme.  
        """
        try:
            from_map = self.load_map(from_theme)
            to_map = self.load_map(to_theme)
            if page_title == None:
                pages = from_map.findAll("topicref")
            else:
                pages = [from_map.find("topicref", attrs={"navtitle" : page_title})]
            if pages == [None] or pages == []:
                raise exception("not found")
            for page in pages:
                to_map.map.append(page)
            self.save_map(to_theme, to_map)
            for page in pages:
                page.extract()
            self.save_map(from_theme, from_map)
        except Exception, e:
            elogger.debug('move_page: %s' % e)
            # Shouldn't ever happen
            pass
    
    def __open_URL(self, url):
        """
            retrieves content from specified url
        """
        urllib._urlopener = self.New_URL_Opener()
        try:
            logger.debug("opening " + url)
            logger.debug("proxies: " + str(self.proxies))
            doc = urllib.urlopen(url, proxies=self.proxies)
            output = doc.read()
            doc.close()
            logger.debug("url opened succesfully")
            return output
        except IOError, e:
            elogger.debug('__open_URL: %s' % e)
    
    def page_exists(self, title, theme):
        """
            boolean check if an article exists
        """
        try:
            map = self.load_map(theme)
            if map.find("topicref", attrs={"navtitle" : title}) != None:
                return True
            else:
                return False
        except Exception, e:
            elogger.debug('page_exists: %s' % e)
            return False
        
    def theme_exists(self, theme):
        """
            boolean check if a theme exists
        """
        themes = self.get_themes()
        if theme in themes:
            return True
        else:
            return False
    
    def remove_page(self, page, theme):
        """
            Removes specified page from the specified theme.
            @param page: Page to remove
            @param theme: Containing theme
        """
        if theme == "Downloaded Articles":
            return
        theme_map = self.load_map(theme)
        entry = theme_map.find("topicref", attrs={"navtitle" : page})
        try:
            os.remove(entry['href'])
        except Exception, e:
            elogger.debug('remove_page: %s' % e)
        entry.extract()
        self.save_map(theme, theme_map)
    
    def remove_theme(self, theme):
        """
            Removes specified theme, moving all articles in it to the 'No Assigned Theme' theme.
            @param theme: Theme to remove
        """    
        try:
            #Just remove map from library at the moment
            #self.move_pages(theme, "No Assigned Theme")
            library = self.load_map("Library")
            entry = library.find("topicref", attrs={"navtitle" : theme})
            if entry != None:
                os.remove(os.path.join(self.workingDir, entry['href']))
                entry.extract()
                self.save_map("Library", library)
        except Exception, e:
            # Trying to remove a theme that doesn't exist, so pretend it worked.
            elogger.debug('remove_theme: %s' % e)
    
    def rename_page(self, theme, old_title, new_title):
        """
            renames specified page in specified theme
        """
        try:
            map = self.load_map(theme)
            page = map.find("topicref", attrs={"navtitle" : old_title})
            if page != None:
                page['navtitle'] = new_title
                self.save_map(theme, map)
        except Exception, e:
            elogger.debug('rename_page: %s' % e)
    
    def rename_theme(self, old_name, new_name):
        """
            renames specified theme
        """
        library = self.load_map("Library")
        entry = library.find("topicref", attrs={"navtitle" : old_name})
        if entry != None and library.find("topicref", attrs={"navtitle" : new_name}) == None:
            self.add_theme_to_library(new_name)
            theme = self.load_map(entry['navtitle'])
            theme.map['name'] = new_name
            self.save_map(new_name, theme)
            self.remove_theme(old_name)
        
    def save_article(self, article, overwrite = True):
        """
            wrapper method for save_page to allow saving article objects
        """
        title = article.article_title
        theme = article.article_theme
        if title != None and theme != None:
            contents = Article_Builder().get_dita_from_article(article)
            self.save_page(title, contents, theme, overwrite)
        else:
            raise theme_not_found_error("Theme or title not specified")
        
    def save_map(self, map_name, map_data):
        """
            Saves the specified map.
            @param map_name: Name of map
            @param map_data: Contents of map
        """
        if not os.path.exists(self.workingDir):
                os.makedirs(self.workingDir, 0777)
        map = open(os.path.join(self.workingDir, "%s.ditamap" % self.clean_title(map_name)), "w")
        map.write(map_data.prettify())
        map.close()
        
    def save_page(self, title, contents, theme="Downloaded Articles", overwrite=True, get_images=False, statuslabel=None):
        """
            Saves the specified page contents as specified title (in optional specified theme).
            @param title: Title to save as.
            @param contents: Contents to save.
            @param theme: Theme to save in.
            @param overwrite: Boolean to specify overwrite if file already exists.
        """
        unique=2
        new_title = self.clean_title(title) + "-" + self.clean_title(theme)
        if get_images:
            contents = self.image_handler(contents, title, statuslabel)
        directory = os.path.join(self.workingDir, self.clean_title(title))
        if not os.path.exists(directory):
                os.makedirs(directory, 0777)
        if overwrite == False:
            while os.access(os.path.join(directory, "%s.dita" % new_title), os.F_OK):
                new_title = self.clean_title(title) + str(unique)
                unique += 1
        contents = contents.replace('<prolog>', '<prolog>\n<resourceid id="%d" />' % self.get_unique_article_ID(), 1)
        file = open(os.path.join(directory, "%s.dita" % new_title), "w")
        file.write(contents)
        file.close()
        self.__add_page_to_library(title, os.path.join(directory, "%s.dita" % new_title), theme)
        logger.debug("Page saved to - " + os.path.join(directory, "%s.dita" %
                new_title))
        return os.path.join(directory, "%s.dita" % new_title)
    
    def validate_image_list(self, image_list):
        """
            provides a mechanism for validating image lists and expanding relative paths
            @param image_list: list of images to validate
            @return: list of images with corrected paths, and broken images removed
        """
        for i in xrange(len(image_list)):
            if not os.access(image_list[i][0], os.F_OK):
                if os.access(os.path.join(self.workingDir, image_list[i][0]), os.F_OK):
                    image_list[i] = (os.path.join(self.workingDir, image_list[i][0]), image_list[i][1])
                else:
                    image = None
        #removing during for loop was unreliable
        while None in image_list:
            image_list.remove(None)
        return image_list

    class New_URL_Opener(urllib.FancyURLopener):
        version = "Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11"
