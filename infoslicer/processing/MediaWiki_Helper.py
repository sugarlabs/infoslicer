# Copyright (C) IBM Corporation 2008

import urllib
from xml.dom import minidom
import logging

import net

import re

logger = logging.getLogger('infoslicer')

"""
Extend urllib class to spoof user-agent
"""
class NewURLopener(urllib.FancyURLopener):
    version = "Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11"

class PageNotFoundError(Exception):
    def __init__(self, value):
        self.parameter = value
    def __str__(self):
        return repr(self.parameter)

class NoResultsError(Exception):
    def __init__(self, value):
        self.parameter = value
    def __str__(self):
        return repr(self.parameter)

"""
Default media wikihost 
"""
defaultWiki = "en.wikipedia.org"


"""
This class handles interaction with Media Wiki. Getting 
content based on a number of parameters such as URL, Title, Revision.
"""
class MediaWiki_Helper:
    
    def __init__(self):
        self.proxies = net.proxies

    def resolveTitle(self, title, wiki=defaultWiki):
        """Check if a wiki article exists using the mediawiki api. Follow redirects.
        
        @param title: article title to resolve
        @param wiki: optional. Defaults to default wiki
        @return: validated article title
        @rtype: string
        @raise PageNotFoundError: if page not found"""
        #replace spaces with underscores
        title = title.replace(" ", "_")
        #create the API request string
        path = "http://%s/w/api.php?action=query&titles=%s&redirects&format=xml" % (wiki, title)
        #parse the xml
        xmldoc = minidom.parseString(self.getDoc(path))
        #check page exists, return None if it doesn't
        page = xmldoc.getElementsByTagName("page")
        if (page != []):
            if ("missing" in page[0].attributes.keys()):
                raise PageNotFoundError("The article with title '%s' could not be found on wiki '%s'" % (title, wiki))
        #check if there are any redirection tags defined
        redirectList = xmldoc.getElementsByTagName("r")
        #if the redirect list is empty, return the title
        if redirectList == []:
            return title
        #if there is a redirect, recursively follow the chain
        else:
            return self.resolveTitle(redirectList[0].attributes["to"].value)
    
    def resolveRevision(self, revision, wiki=defaultWiki):
        """ get an article by revision number.
        
         @param revision: revision number to resolve
         @param wiki: optional. Defaults to default wiki
         @return: revision number if valid
         @rtype: string
         @raise PageNotFoundError: if page not found"""
        path = "http://%s/w/api.php?action=query&format=xml&revids=%s" % (wiki, revision)
        if ("page" in self.getDoc(path)):
            return revision
        else:
            raise PageNotFoundError("The article with revision id '%s' could not be found on wiki '%s'" % (revision, wiki))
        
    def getArticleAsWikiTextByTitle(self, title, wiki=defaultWiki):
        """Gets the wiki markup of an article by its title from the wiki specified.
        
        @param title: title of article to retrieve
        @param wiki: optional. Defaults to default wiki
        @return: article content in wiki markup
        @rtype: string"""
        #resolve the article title 
        title = self.resolveTitle(title)
        #create the API request string
        path = "http://%s/w/api.php?action=query&prop=revisions&titles=%s&rvprop=content&format=xml" % (wiki, title)
        #remove xml tags around article
        return self.stripTags(getDoc(path), "rev")
        
    def getArticleAsWikiTextByURL(self, url):
        """Gets the wiki markup of an article by its title from the wiki specified.
        
        @param url: url of article to retrieve
        @param wiki: optional. Defaults to default wiki
        @return: article content in wiki markup
        @rtype: string"""
        args = self.breakdownURL(url)
        if len(args) == 3:
            return self.getArticleAsWikiTextByRevision(args[2], args[0])
        else:
            return self.getArticleAsWikiTextByTitle(args[1], args[0])
        
    def getArticleAsWikiTextByRevision(self, revision, wiki=defaultWiki):
        """Gets the wiki markup of an article by its revision id from the wiki specified.
        
        @param revision: revision id of article to retrieve
        @param wiki: optional. Defaults to default wiki
        @return: article content in wiki markup
        @rtype: string"""
        self.resolveRevision(revision, wiki)
        path = "http://%s/w/api.php?action=query&prop=revisions&revids=%s&rvprop=content&format=xml" % (wiki, revision)
        return self.stripTags(getDoc(path), "rev")
        
    def getArticleAsHTMLByTitle(self, title, wiki=defaultWiki):
        """Gets the HTML markup of an article by its title from the wiki specified.
        
        @param title: title of article to retrieve
        @param wiki: optional. Defaults to default wiki
        @return: article content in HTML markup
        @rtype: string"""
        #resolve article title
        title = self.resolveTitle(title, wiki)
        #create the API request string
        path = "http://%s/w/api.php?action=parse&page=%s&format=xml" % (wiki,title)
        #remove xml tags around article and fix HTML tags and quotes
        #return fixHTML(stripTags(getDoc(path), "text"))
        return self.fixHTML(self.getDoc(path)), path
        
    def getArticleAsHTMLByURL(self, url):
        """Gets the HTML markup of an article by its title from the wiki specified.
        
        @param url: url of article to retrieve
        @param wiki: optional. Defaults to default wiki
        @return: article content in HTML markup
        @rtype: string"""
        args = self.breakdownURL(url)
        if len(args) == 3:
            return self.getArticleAsHTMLByRevision(args[2], args[0])
        else:
            return self.getArticleAsHTMLByTitle(args[1], args[0])
    
    def getArticleAsHTMLByRevision(self, revision, wiki=defaultWiki):
        """Gets the HTML markup of an article by its revision id from the wiki specified.
        
        @param revision: revision id of article to retrieve
        @param wiki: optional. Defaults to default wiki
        @return: article content in HTML markup
        @rtype: string"""
        self.resolveRevision(revision, wiki)
        path = "http://%s/w/api.php?action=parse&oldid=%s&format=xml" % (wiki,revision)
        #remove xml tags around article and fix HTML tags and quotes
        return self.fixHTML(stripTags(getDoc(path), "text"))
    
    def breakdownURL(self, url):
        """pulls out wiki address, title and revision id from a wiki URL
        
        @param url: url to process
        @return: information from url
        @rtype: list"""
        outputlist = []
        url = url.replace("http://", "")
        outputlist.append(url.split("/")[0])
        if ("title=" in url):
            outputlist.append(url.split("title=")[-1].split("&")[0])
        if ("oldid=" in url):
            outputlist.append(url.split("oldid=")[-1].split("&")[0])
        else:
            outputlist.append(url.split("/")[-1])
        return outputlist
        
    def getDoc(self, path):
        """opens a remote file by http and retrieves data
        
        @param path: location of remote file 
        @return: page contents
        @rtype: string"""
        urllib._urlopener = NewURLopener()
        logger.debug("opening " + path)
        logger.debug("proxies: " + str(self.proxies))
        pathencoded = self.urlEncodeNonAscii(path)
        logger.debug("pathencoded " + pathencoded)
        doc = urllib.urlopen(pathencoded, proxies=self.proxies)
        output = doc.read()
        doc.close()
        logger.debug("url opened successfully")
        return output
    
    def urlEncodeNonAscii(self, b):
        return re.sub('[\x80-\xFF]', lambda c: '%%%02x' % ord(c.group(0)), b)

    def stripTags(self, input, tag):
        """removes specified tag
    
        @param input: string to work on
        @param tag: tag to remove
        @return: original string with specified tag removed
        @rtype: string"""
        return input.split("<%s>" % (tag), 1)[1].split("</%s>" % (tag), 1)[0]
    
    def fixHTML(self, input):
        """fixes <, > and " characters in HTML
        
        @param input: input string to work on
        @return: modified version of input
        @rtype: string"""
        return input.replace("&lt;", "<").replace("&gt;", ">").replace("&quot;",'"')
    
    def getImageURLs(self, title, wiki=defaultWiki, revision=None):
        """returns a list of the URLs of every image on the specified page on the (optional) specified wiki
        @deprecated: This task is now performed at the parsing stage
        """
        #check article title is valid, follow redirects
        title = self.resolveTitle(title, wiki)
        #proceed if title is valid
        if (title != None):
            #create the API request string
            path = "http://%s/w/api.php?action=query&prop=images&titles=%s&format=xml" % (wiki, title)
            xmldoc = minidom.parseString(self.getDoc(path))
            imglist = xmldoc.getElementsByTagName("im")
            outputlist = []
            for i in xrange(len(imglist)):
                #create the API request string
                path = "http://%s/w/api.php?action=query&titles=%s&prop=imageinfo&iiprop=url&format=xml" % (wiki, imglist[i].attributes["title"].value.replace(" ","_"))
                xmldoc2 = minidom.parseString(self.getDoc(path))
                #append image url to output
                outputlist.append(xmldoc2.getElementsByTagName("ii")[0].attributes["url"].value)
            #return outputlist
            return []
        
    def getImages(self, title, wiki=defaultWiki):
        """returns a list of the URLs of every image on the specified page on the (optional) specified wiki
        @deprecated: This task is now performed at the saving stage
        """
        imglist = getImageURLs(title, wiki)
        outputlist = []  
        if imglist !=[]:
            for i in imglist:
                outputlist.append(getDoc(i))
        return outputlist
    
    def searchWiki(self, search, wiki=defaultWiki):
        """Search a wiki using the openSearch protocol.
        
        @param search: string to search for
        @param wiki: optional. Defaults to default wiki
        @return: search results and description pairs
        @rtype: list"""
        path = "http://%s/w/api.php?action=opensearch&search=%s&format=xml" % (wiki, search)
        output = minidom.parseString(self.getDoc(path))
        results = []
        for item in output.getElementsByTagName("Item"):
            results.append((item.getElementsByTagName("Text")[0].firstChild.data, item.getElementsByTagName("Description")[0].firstChild.data))
        return results
        
    # TODO: make this work with new searchWiki method
    """def getFirstSearchResult(search, wiki=defaultWiki):
        xmldoc = minidom.parseString(searchWiki(search, wiki))
        resultList = xmldoc.getElementsByTagName("Item")
        if (len(resultList) > 0):
            return stripTags(resultList[0].getElementsByTagName("Text")[0].toxml(), "Text")
        else:
            raise noResultsError("No results found for '%s' on wiki: %s" % (search, wiki))"""
