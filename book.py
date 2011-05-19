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
import zipfile
from gobject import SIGNAL_RUN_FIRST, TYPE_PYOBJECT
from gettext import gettext as _

from sugar.activity.activity import get_bundle_path, get_activity_root

import net
from infoslicer.processing.Article import Article
from infoslicer.processing import Article_Builder

logger = logging.getLogger('infoslicer')

wiki = None
custom = None

image_root = os.path.join(get_activity_root(), 'data', 'book')

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
        self.sync_article()

        if title is None:
            return

        index, entry = self.find(title)

        if entry:
            content = self._load(entry['uid'])
            if content:
                data = Article_Builder.get_article_from_dita(
                        image_root, content)
                self._article = Article(data)
            else:
                self._article = Article()
        else:
            entry = self._create(title, uuid.uuid1())
            self._article = Article()

        self._article.uid = entry['uid']
        self._article.article_title = title
        gobject.idle_add(self._emit_article_selected)

    article = gobject.property(type=object,
            getter=get_article, setter=set_article)

    def _emit_article_selected(self):
        self.emit('article-selected', self._article)

    # save current article
    def sync_article(self):
        # stub
        pass

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
        del self.index[index]
        self.sync_index()

        self.emit('article-deleted', title)

    def find(self, title):
        for i, entry in enumerate(self.index):
            if entry['title'] == title:
                return (i, entry)
        return (None, None)

    def find_by_uuid(self, uid):
        for i in self.index:
            if i['uid'] == uid:
                return i
        return None

    def sync_index(self):
        data = { 'uid'      : self.uid,
                 'index'    : self.index,
                 'revision' : self.revision }

        index = file(os.path.join(self.root, 'index'), 'w')
        index.write(cjson.encode(data))
        index.close()

    def sync(self):
        self.sync_article()
        self.sync_index()

    def __init__(self, preinstalled, root):
        gobject.GObject.__init__(self)
        self.root = root
        self.index = []
        self.uid = None
        self.revision = 0
        self._article = None

        if os.path.exists(self.root):
            try:
                index = file(os.path.join(self.root, 'index'), 'r')
                data = cjson.decode(index.read())
                self.uid = data['uid']
                self.index = data['index']
                self.revision = data['revision']
                if self.index:
                    self.props.article = self.index[0]['title']
            except:
                logger.debug('cannot find index file; use empty')

        if not self.uid:
            self.uid = str(uuid.uuid1())
            self.revision = 1

            if not os.path.exists(self.root):
                os.makedirs(self.root, 0775)

            for i in preinstalled:
                filepath = os.path.join(get_bundle_path(), 'examples', i[1])

                logger.debug("install library: opening %s" % filepath)
                open_file = open(filepath, "r")
                contents = open_file.read()
                open_file.close()

                logger.debug("install library: saving page %s" % i[0])
                self.create(i[0], contents)
                logger.debug("install library: save successful")
                self.sync_index()

    def _create(self, title, uid):
        entry = { 'title': title, 'uid': str(uid), 'ready': False }
        self.index.append(entry)
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

        Book.__init__(self, PREINSTALLED, image_root)

class CustomBook(Book):
    def __init__(self, filepath=None):
        PREINSTALLED = [
            (_('Giraffe'), "giraffe-blank.dita") ]

        root = os.path.join(get_activity_root(), 'tmp', 'book')
        shutil.rmtree(root, True)

        if not filepath:
            Book.__init__(self, PREINSTALLED, root)
        else:
            zip = zipfile.ZipFile(filepath, 'r')
            for i in zip.namelist():
                path = os.path.join(root, i)
                os.makedirs(os.path.dirname(path), 0775)
                file(path, 'wb').write(zip.read(i))
            zip.close()

            Book.__init__(self, [], root)

    def sync(self, filepath):
        Book.sync(self)

        logger.debug('close: save to %s' % filepath)

        zip = zipfile.ZipFile(filepath, 'w')
        for root, dirs, files in os.walk(self.root):
            relpath = root.replace(self.root, '', 1)
            for i in files:
                zip.write(os.path.join(root, i), os.path.join(relpath, i))
        zip.close()

    def sync_article(self):
        if not self._article:
            return

        self.find_by_uuid(self._article.uid)['title'] = \
                self._article.article_title

        contents = Article_Builder.get_dita_from_article(
                image_root, self._article)

        self._save(self._article.uid, contents)
