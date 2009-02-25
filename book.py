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
import gtk
import logging
from gettext import gettext as _

from sugar.activity.activity import get_bundle_path, get_activity_root

from Processing.IO_Manager import IO_Manager

logger = logging.getLogger('infoslicer')

wiki = None
custom = None

class Book(IO_Manager):
    def __init__(self, preinstalled, dirname):
        IO_Manager.__init__(self, 0)
        self.workingDir = os.path.join(get_activity_root(), dirname)

        if not os.path.exists(self.workingDir):
            os.makedirs(self.workingDir, 0777)

            for i in preinstalled:
                filepath = os.path.join(get_bundle_path(), 'Processing',
                        'demolibrary', i[1])

                logger.debug("install library: opening %s" % filepath)
                open_file = open(filepath, "r")
                contents = open_file.read()
                open_file.close()

                logger.debug("install library: saving page %s" % i[0])
                self.save_page(i[0], contents, get_images=True)
                logger.debug("install library: save successful")

        pages = self.get_pages()
        if pages:
            self.article = self.load_article(pages[0])
        else:
            self.article = Article()

class WikiBook(Book):
    def __init__(self):
        PREINSTALLED = [
            (_('Lion (from en.wikipedia.org)'),     "lion-wikipedia.dita"),
            (_('Tiger (from en.wikipedia.org)'),    "tiger-wikipedia.dita"),
            (_('Giraffe (from en.wikipedia.org)'),  "giraffe-wikipedia.dita"),
            (_('Zebra (from en.wikipedia.org)'),    "zebra-wikipedia.dita") ]
        Book.__init__(self, PREINSTALLED, 'data/book')

class CustomBook(Book):
    def __init__(self):
        PREINSTALLED = [
            (_('Giraffe'), "giraffe-blank.dita") ]
        Book.__init__(self, PREINSTALLED, 'tmp/book')

def init():
    global wiki, custom
    wiki = WikiBook()
    custom = CustomBook()
