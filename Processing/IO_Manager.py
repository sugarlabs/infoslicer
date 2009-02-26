# Copyright (C) IBM Corporation 2008

import gtk
import shutil
import re
import logging
import os
import urllib
import gobject
from gettext import gettext as _

from BeautifulSoup import Tag
from NewtifulSoup import NewtifulStoneSoup as BeautifulStoneSoup
from Article_Builder import Article_Builder
from Processing.Article.Article import Article
from MediaWiki_Helper import MediaWiki_Helper, PageNotFoundError
from MediaWiki_Parser import MediaWiki_Parser

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
mediawiki communication and raw pages/article modifications)
"""    
class IO_Manager(gobject.GObject):
    def __init__(self, foo):
        gobject.GObject.__init__(self)

    def load_map(self):
        # stub
        pass

    def clean_title(self, title):
        """
            removes non-alphanumeric chars from titles and lowercases it
        """
        logger.debug("Cleaning: " + title)
        output = re.sub(re.compile('\W'), "_", title).lower()
        logger.debug("Output: " + output)
        return output
    
    def __add_page_to_library(self, title, path):
        """
            Adds a page to the library.
            
            @param title: The title of the article to add to library.
            @param path: The path of the article to add to library.
        """
        #change to relative path
        path = path.replace(os.path.join(self.workingDir, ""), "", 1)
        map = self.load_map()

        for i in [i for i in map if i['title'] == title]:
            self.remove_page(i['title'])

        map.append({'title': title, 'href': path})
        
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
    
    def load_raw_page(self, title):
        """
            Returns contents of specified page.
            
            @param title: Title of page to open.
            @return: Contents of page.
        """
        logger.debug('load article %s' % title)
        theme_map = self.load_map()

        page_location = [i for i in theme_map if i['title'] == title]
        if page_location:
            page_location = page_location[0]['href']
        else:
            raise page_not_found_error("No match for " + title)
        
        #if not os.access(page_location, os.F_OK):
        if os.access(os.path.join(self.workingDir, page_location), os.F_OK):
            page_location = os.path.join(self.workingDir, page_location)
        else:
            raise page_not_found_error("Page not found at " + page_location)
        page = open(page_location, "r")
        output = page.read()
        page.close()
        return output
        
    def load_page(self, title):    
        return Article_Builder(self.workingDir).get_article_from_dita(
                self.load_raw_page(title))
        
    def load_article(self, title):
        """
            loads the specified article
        """
        article_data = self.load_page(title)
        article = Article(article_data)
        article.article_title = title
        return article
    
    def __open_URL(self, url):
        """
            retrieves content from specified url
        """
        urllib._urlopener = self.New_URL_Opener()
        try:
            logger.debug("opening " + url)
            logger.debug("proxies: " + str(proxies))
            doc = urllib.urlopen(url, proxies=proxies)
            output = doc.read()
            doc.close()
            logger.debug("url opened succesfully")
            return output
        except IOError, e:
            elogger.debug('__open_URL: %s' % e)
    
    def remove_page(self, page):
        """
            Removes specified page from the specified.
            @param page: Page to remove
        """
        theme_map = self.load_map()

        for i, entry in enumerate(theme_map):
            if entry['title'] != title:
                continue
            try:
                os.remove(entry['href'])
            except Exception, e:
                elogger.debug('remove_page: %s' % e)
            del theme_map[i]
    
    def rename_page(self, old_title, new_title):
        """
            renames specified page
        """
        map = self.load_map()

        for entry in map:
            if entry['title'] != old_title:
                continue
            entry['title'] = new_title
    
    def save_article(self, article, overwrite = True):
        """
            wrapper method for save_page to allow saving article objects
        """
        title = article.article_title
        if title != None:
            contents = Article_Builder(self.workingDir).get_dita_from_article(
                    article)
            self.save_page(title, contents, overwrite)
        else:
            raise theme_not_found_error("Title not specified")
        
    def save_page(self, title, contents, get_images=False, statuslabel=None):
        """
            Saves the specified page contents as specified title.
            @param title: Title to save as.
            @param contents: Contents to save.
        """
        new_title = self.clean_title(title)
        if get_images:
            contents = self.image_handler(contents, title, statuslabel)

        directory = os.path.join(self.workingDir, self.clean_title(title))

        if not os.path.exists(directory):
            os.makedirs(directory, 0777)

        contents = contents.replace(
                '<prolog>', '<prolog>\n<resourceid id="%d" />'
                % self.get_unique_article_ID(), 1)

        file = open(os.path.join(directory, "%s.dita" % new_title), "w")
        file.write(contents)
        file.close()
        self.__add_page_to_library(title, os.path.join(directory, "%s.dita" % new_title))

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
        version = "Mozilla/5.0 (X11; U; Linux x86_64; en-US; rv:1.9.1b2)" \
                  "Gecko/20081218 Gentoo Iceweasel/3.1b2"

# http proxy

proxies = {}

proxy_file = os.path.join(os.path.split(os.path.split(__file__)[0])[0], 'proxy.cfg')

if os.access(proxy_file, os.F_OK):
    proxy_file_handle = open(proxy_file, "r")
    for line in proxy_file_handle.readlines():
        parts = line.split(':', 1)
        #logger.debug("setting " + parts[0] + " proxy to " + parts[1])
        proxies[parts[0].strip()] = parts[1].strip()
    proxy_file_handle.close()

if proxies == {}:
    proxies = None
