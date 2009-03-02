# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import os
import shutil
import urllib
import logging
from gettext import gettext as _

from sugar.activity.activity import get_bundle_path

import book
from infoslicer.processing.NewtifulSoup import NewtifulStoneSoup \
        as BeautifulStoneSoup
from infoslicer.processing.MediaWiki_Parser import MediaWiki_Parser
from infoslicer.processing.MediaWiki_Helper import MediaWiki_Helper
from infoslicer.processing.MediaWiki_Helper import PageNotFoundError

logger = logging.getLogger('infoslicer')
elogger = logging.getLogger('infoslicer::except')

proxies = None

def download_wiki_article(title, wiki, progress):
    try:
        progress.set_label(_('"%s" download in progress...') % title)
        article, url = MediaWiki_Helper().getArticleAsHTMLByTitle(title, wiki)

        progress.set_label(_('Processing "%s"...') % title)
        parser = MediaWiki_Parser(article, title, url)
        contents = parser.parse()

        progress.set_label(_('Downloading "%s" images...') % title)
        book.wiki.create(title + _(' (from %s)') % wiki, contents)

        progress.set_label(_('"%s" successfully downloaded') % title)

    except PageNotFoundError, e:
        elogger.debug('download_and_add: %s' % e)
        progress.set_label(_('"%s" could not be found') % title)

    except Exception, e:
        elogger.debug('download_and_add: %s' % e)
        progress.set_label(_('Error downloading "%s"; check your connection') % title)

def image_handler(root, uid, document):
    """
        Takes a DITA article and downloads images referenced in it
        (finding all <image> tags).
        Attemps to fix incomplete paths using source url.
        @param document: DITA to work on
        @return: The document with image tags adjusted to point to local paths
    """
    document = BeautifulStoneSoup(document)
    dir_path =  os.path.join(root, uid, "images")

    logger.debug('image_handler: %s' % dir_path)

    if not os.path.exists(dir_path):
        os.makedirs(dir_path, 0777)

    for image in document.findAll("image"):
        fail = False
        path = image['href']
        if "#DEMOLIBRARY#" in path:
            path = path.replace("#DEMOLIBRARY#",
                    os.path.join(get_bundle_path(), 'examples'))
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
            image_contents = _open_url(path)
            if image_contents == None:
                fail = True
            else:
                file.write(image_contents)
            file.close()
        #change to relative paths:
        if not fail:
            image['href'] = os.path.join(dir_path.replace(os.path.join(root, ""), "", 1), image_title)
            image['orig_href'] = path
        else:
            image.extract()

    return document.prettify()

def _open_url(url):
    """
        retrieves content from specified url
    """
    urllib._urlopener = _new_url_opener()
    try:
        logger.debug("opening " + url)
        logger.debug("proxies: " + str(proxies))
        doc = urllib.urlopen(url, proxies=proxies)
        output = doc.read()
        doc.close()
        logger.debug("url opened succesfully")
        return output
    except IOError, e:
        elogger.debug('_open_url: %s' % e)

class _new_url_opener(urllib.FancyURLopener):
    version = "Mozilla/5.0 (X11; U; Linux x86_64; en-US; rv:1.9.1b2)" \
              "Gecko/20081218 Gentoo Iceweasel/3.1b2"

# http proxy

_proxy_file = os.path.join(os.path.split(os.path.split(__file__)[0])[0],
        'proxy.cfg')
_proxylist = {}

if os.access(_proxy_file, os.F_OK):
    proxy_file_handle = open(_proxy_file, "r")
    for line in proxy_file_handle.readlines():
        parts = line.split(':', 1)
        #logger.debug("setting " + parts[0] + " proxy to " + parts[1])
        _proxylist[parts[0].strip()] = parts[1].strip()
    proxy_file_handle.close()

if _proxylist:
    proxies = _proxylist
