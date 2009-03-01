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
import uuid
import logging
import gobject
import cjson
import shutil
from gobject import SIGNAL_RUN_FIRST, TYPE_PYOBJECT
from gettext import gettext as _

from sugar.activity.activity import get_bundle_path, get_activity_root

import net
from Processing.Article.Article import Article
from Processing.Article_Builder import Article_Builder

logger = logging.getLogger('infoslicer')

wiki = None
custom = None

class Book(gobject.GObject):
    __gsignals__ = {
        'article-selected' : (SIGNAL_RUN_FIRST, None, [TYPE_PYOBJECT]),
        'article-added'    : (SIGNAL_RUN_FIRST, None, [TYPE_PYOBJECT]),
        'article-deleted'  : (SIGNAL_RUN_FIRST, None, [TYPE_PYOBJECT]) } 

    def get_article(self):
        return self._article

    def set_article(self, title):
        if self._article and self._article.article_title == title:
            return

        logger.debug('set_article: %s' % title)
        self.sync()

        if title is None:
            return

        index, entry = self.find(title)

        if entry:
            content = self._load(entry['uid'])
            if content:
                data = Article_Builder(self.root).get_article_from_dita(content)
                self._article = Article(data)
            else:
                self._article = Article()
        else:
            entry = self._create(title, uuid.uuid1())
            self._article = Article()

        self._article.uid = entry['uid']
        self._article.article_title = title
        self.emit('article-selected', self._article)

    article = gobject.property(type=object,
            getter=get_article, setter=set_article)

    # save current article
    def sync(self):
        if not self._article:
            return

        self.find_by_uuid(self._article.uid)['title'] = \
                self._article.article_title
        contents = Article_Builder(self.root).get_dita_from_article(
                self._article)
        self._save(self._article.uid, contents)

    def create(self, title, content):
        uid = str(uuid.uuid1())
        content = net.image_handler(self.root, uid, content)
        self._save(uid, content)
        self._create(title, uid)

    def remove(self, title):
        index, entry = self.find(title)

        if not entry:
            logger.debug('cannot find %s to remove' % title)
            return

        if self._article and self._article.article_title == title:
            self._article = None

        shutil.rmtree(os.path.join(self.root, entry['uid']), True)
        del self.map[index]
        self.save_map()

        self.emit('article-deleted', title)

    def find(self, title):
        for i, entry in enumerate(self.map):
            if entry['title'] == title:
                return (i, entry)
        return (None, None)

    def find_by_uuid(self, uid):
        for i in self.map:
            if i['uid'] == uid:
                return i
        return None

    def save_map(self):
        data = { 'uid': self.uid,
                 'map': self.map }

        mapfile = file(os.path.join(self.root, 'map'), 'w')
        mapfile.write(cjson.encode(data))
        mapfile.close()

    def __init__(self, preinstalled, dirname):
        gobject.GObject.__init__(self)
        self.root = os.path.join(get_activity_root(), dirname)
        self.map = []
        self.uid = None
        self._article = None

        if os.path.exists(self.root):
            try:
                mapfile = file(os.path.join(self.root, 'map'), 'r')
                data = cjson.decode(mapfile.read())
                self.uid = data['uid']
                self.map = data['map']
                if self.map:
                    self.props.article = self.map[0]['title']
            except:
                logger.debug('cannot find map file; use empty')
        else:
            self.uid = str(uuid.uuid1())
            os.makedirs(self.root, 0777)

            for i in preinstalled:
                filepath = os.path.join(get_bundle_path(), 'examples', i[1])

                logger.debug("install library: opening %s" % filepath)
                open_file = open(filepath, "r")
                contents = open_file.read()
                open_file.close()

                logger.debug("install library: saving page %s" % i[0])
                self.create(i[0], contents)
                logger.debug("install library: save successful")
                self.save_map()

    def _create(self, title, uid):
        entry = { 'title': title, 'uid': str(uid), 'ready': False }
        self.map.append(entry)
        self.emit('article-added', title)
        return entry

    def _load(self, uid):
        logger.debug('load article %s' % uid)

        path = os.path.join(self.root, str(uid), 'page.dita')
        if not os.access(path, os.F_OK):
            logger.debug('_load: cannot find %s' % path)
            return None

        page = open(path, "r")
        output = page.read()
        page.close()

        return output

    def _save(self, uid, contents):
        directory = os.path.join(self.root, str(uid))

        if not os.path.exists(directory):
            os.makedirs(directory, 0777)

        contents = contents.replace(
                '<prolog>', '<prolog>\n<resourceid id="%s" />'
                % uuid.uuid1(), 1)

        file = open(os.path.join(directory, 'page.dita'), 'w')
        file.write(contents)
        file.close()

        logger.debug('save: %s' % directory)

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

def teardown():
    wiki.props.article = None
    wiki.save_map()
    custom.props.article = None
    custom.save_map()
