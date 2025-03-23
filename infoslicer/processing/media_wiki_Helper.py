# -*- coding: utf-8 -*-
# Copyright (C) IBM Corporation 2008

import urllib.request as urllib
from xml.dom import minidom
import logging
import json
import re
import net


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


# Default media wikihost

defaultWiki = "en.wikipedia.org"


class MediaWiki_Helper:
    """
    This class handles interaction with Media Wiki. Getting 
    content based on a number of parameters such as URL, Title, Revision.
    """

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
        if page != []:
            if ("missing" in page[0].attributes.keys()):
                raise PageNotFoundError("The article with title '%s' could not be found on wiki '%s'" % (title, wiki))
        #check if there are any redirection tags defined
        redirectList = xmldoc.getElementsByTagName("r")
        #if the redirect list is empty, return the title
        if redirectList == []:
            return title
        #if there is a redirect, recursively follow the chain
        else:
            return self.resolveTitle(redirectList[0].attributes["to"].value, wiki=wiki)

    def resolveRevision(self, revision, wiki=defaultWiki):
        """ get an article by revision number.
        
         @param revision: revision number to resolve
         @param wiki: optional. Defaults to default wiki
         @return: revision number if valid
         @rtype: string
         @raise PageNotFoundError: if page not found"""
        path = "http://%s/w/api.php?action=query&format=xml&revids=%s" % (wiki, revision)
        if "page" in self.getDoc(path):
            return revision
        else:
            raise PageNotFoundError("The article with revision id '%s' could not be found on wiki '%s'" % (revision, wiki))

    def getArticleAsHTMLByTitle(self, title, wiki=defaultWiki):
        """Gets the HTML markup of an article by its title from the wiki specified.
        
        @param title: title of article to retrieve
        @param wiki: optional. Defaults to default wiki
        @return: article content in HTML markup
        @rtype: string"""
        # Resolve the title (handle redirects)
        title = self.resolveTitle(title, wiki)

        # Create the API request URL
        path = "http://%s/w/api.php?action=parse&page=%s&format=json" % (wiki, title)

        # Fetch the document content
        doc = self.getDoc(path)

        # Extract article content inside <text> tag
        article_content, strip_revid = self.stripTags(doc, "text")
        # Fix HTML entities
        return self.fixHTML(article_content), path, strip_revid

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
        doc = urllib.urlopen(pathencoded)
        output = doc.read()
        doc.close()
        logger.debug("url opened successfully")
        return output

    def urlEncodeNonAscii(self, b):
        return re.sub('[\x80-\xFF]', lambda c: '%%%02x' % ord(c.group(0)), b)

    def stripTags(self, input_json, tag):
        """Extracts content inside a specific XML tag.
        
        @param input: XML string
        @param tag: The tag to extract content from
        @return: Content inside the tag
        """
        try:
            load_data = json.loads(input_json)
            strip_html = load_data["parse"][tag]['*']
            strip_revid = load_data['parse']['revid']
            return strip_html, strip_revid
        except Exception as e:
            logger.error(f"Error extracting tag {tag}: {e}")
            return ""

    def fixHTML(self, input_content):
        """fixes HTML entities and malformed tags in HTML
        
        @param input: input string to work on
        @return: modified version of input
        @rtype: string"""
        # First pass: Fix standard HTML entities
        try:
            content = input_content.replace("&lt;", " ").replace("&gt;", " ").replace("&quot;", '"')

            # Second pass: Remove HTML tags and citations
            patterns = [
                r'</?sup>',                    # Remove sup tags
                r'\[\d+\]',                    # Remove citation numbers
                r'&lt;/?sup&gt;',             # Remove escaped sup tags
                r'&lt;sup&gt;',               # Remove malformed sup tags
                r'\[citation needed\]',        # Remove citation needed tags
                r'\[\d+\)',                    # Remove citations with parentheses
                r'\s+',                        # Normalize whitespace
            ]

            for pattern in patterns:
                content = re.sub(pattern, ' ', content)

            # Clean up any remaining HTML entities
            content = re.sub(r'&[a-zA-Z]+;', '', content)  # Remove any other HTML entities
            content = re.sub(r'\s+', ' ', content)         # Clean up whitespace

            return content.strip()
        except Exception as e:
            logger.error('The error FixHTML %s', e)

    def getImageURLs(self, title, wiki=defaultWiki, revision=None):
        """returns a list of the URLs of every image on the specified page on the (optional) specified wiki
        @deprecated: This task is now performed at the parsing stage
        """
        #check article title is valid, follow redirects
        title = self.resolveTitle(title, wiki)
        #proceed if title is valid
        if title is not None:
            #create the API request string
            path = "http://%s/w/api.php?action=query&prop=images&titles=%s&format=xml" % (wiki, title)
            xmldoc = minidom.parseString(self.getDoc(path))
            imglist = xmldoc.getElementsByTagName("im")
            outputlist = []
            for i in range(len(imglist)):
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
        imglist = self.getImageURLs(title, wiki)
        outputlist = []
        if imglist !=[]:
            for i in imglist:
                outputlist.append(self.getDoc(i))
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
