# Copyright (C) IBM Corporation 2008
#
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
import urllib.request, urllib.parse, urllib.error
import logging
from gettext import gettext as _

from sugar3.activity.activity import get_bundle_path

import book
from infoslicer.processing.newtiful_soup import NewtifulStoneSoup \
        as BeautifulStoneSoup
from infoslicer.processing.media_wiki_Parser import MediaWiki_Parser
from infoslicer.processing.media_wiki_Helper import MediaWiki_Helper
from infoslicer.processing.media_wiki_Helper import PageNotFoundError

logger = logging.getLogger('infoslicer')
elogger = logging.getLogger('infoslicer::except')

proxies = None

def download_wiki_article(title, wiki, progress):
    try:
        progress.set_label(_('"%s" download in progress...') % title)
        try:
            article, url, strip_revid = MediaWiki_Helper().getArticleAsHTMLByTitle(title, wiki)

            # Optional: force decode if it's bytes
            if isinstance(article, bytes):
                article = article.decode('utf-8', errors='ignore')

        except Exception as e:
            progress.set_label(_('Error getArticleAsHTMLByTitle: %s') % e)
            raise

        progress.set_label(_('Processing "%s"...') % title)
        parser = MediaWiki_Parser(document_to_parse=article, revid=strip_revid, title=title, source_url=url)
        contents = parser.parse()

        progress.set_label(_('Downloading "%s" images...') % title)
        book.WIKI.create(title + _(' (from %s)') % wiki, contents)

        progress.set_label(_('"%s" successfully downloaded') % title)

    except PageNotFoundError as e:
        elogger.debug(f'download_and_add:{e}')
        progress.set_label(_('"%s" could not be found') % title)


    except Exception as e:
        # More detailed error logging
        logger.error(f'Detailed error: {e}', exc_info=True)
        raise

def image_handler(root, uid, document):
    """
    Takes a DITA article and downloads images referenced in it
    (finding all <image> tags).
    Attempts to fix incomplete paths using source url.
    """
    document = BeautifulStoneSoup(document)
    dir_path = os.path.join(root, uid, "images")

    logger.debug('image_handler: %s' % dir_path)

    if not os.path.exists(dir_path):
        os.makedirs(dir_path, 0o777)

    for image in document.findAll("image"):
        fail = False
        path = image['href']

        # Handle protocol-relative URLs and other URL formats
        if path.startswith("//"):
            path = "https:" + path
        elif "#DEMOLIBRARY#" in path:
            path = path.replace("#DEMOLIBRARY#",
                    os.path.join(get_bundle_path(), 'examples'))
            image_title = os.path.split(path)[1]
            shutil.copyfile(path, os.path.join(dir_path, image_title))
            continue

        image_title = path.rsplit("/", 1)[-1]

        # Fix incomplete paths
        if not any(path.startswith(proto) for proto in ['http://', 'https://']):
            if document.source and "href" in document.source:
                base_url = document.source['href'].rsplit("/", 1)[0]
                if path.startswith("/"):
                    path = base_url + path
                else:
                    path = base_url + "/" + path

        logger.debug("Retrieving image: " + path)

        try:
            file = open(os.path.join(dir_path, image_title), 'wb')
            image_contents = _open_url(path)
            if image_contents is None:
                fail = True
            else:
                file.write(image_contents)
            file.close()
        except Exception as e:
            logger.error(f"Failed to download image {path}: {str(e)}")
            fail = True

        # Change to relative paths
        if not fail:
            image['href'] = os.path.join(dir_path.replace(os.path.join(root, ""), "", 1), image_title)
            image['orig_href'] = path
        else:
            image.extract()

    return document.prettify()

def _open_url(url):
    """
    Retrieves content from specified url with improved error handling
    """
    urllib.request._urlopener = _new_url_opener()

    try:
        # Ensure URL has a protocol
        if url.startswith("//"):
            url = "https:" + url

        logger.debug(f"Opening URL: {url}")
        logger.debug(f"Using proxies: {proxies}")

        # Create Request object with headers
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        req = urllib.request.Request(url, headers=headers)

        # Open URL with timeout
        with urllib.request.urlopen(req, timeout=30) as response:
            return response.read()

    except Exception as e:
        logger.error(f"Failed to open URL {url}: {str(e)}")
        return None

class _new_url_opener(urllib.request.FancyURLopener):
    version = "Mozilla/5.0 (X11; U; Linux x86_64; en-US; rv:1.9.1b2)" \
              "Gecko/20081218 Gentoo Iceweasel/3.1b2"

# http proxy

_proxy_file = os.path.join(os.path.split(os.path.split(__file__)[0])[0],
        'proxy.cfg')
_proxylist = {}

if os.access(_proxy_file, os.F_OK):
    proxy_file_handle = open(_proxy_file, "r", encoding="utf-8")
    for line in proxy_file_handle.readlines():
        parts = line.split(':', 1)
        #logger.debug("setting " + parts[0] + " proxy to " + parts[1])
        _proxylist[parts[0].strip()] = parts[1].strip()
    proxy_file_handle.close()

if _proxylist:
    proxies = _proxylist
