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
import gtk
import zipfile
import uuid
import logging
from glob import glob
from gettext import gettext as _

from sugar.activity.activity import get_bundle_path, get_activity_root, get_bundle_name
from sugar.datastore import datastore
from sugar import activity

from infoslicer.processing.NewtifulSoup import NewtifulStoneSoup \
        as BeautifulStoneSoup
import book

logger = logging.getLogger('infoslicer')

def publish(activity, force=False):
    if not [i for i in book.custom.index if i['ready']]:
        activity.notify_alert(
                _('Nothing to publish'),
                _('Mark arcticles from "Custom" panel and try again.'))
        return

    title = activity.metadata['title']
    jobject = datastore.find({
            'activity_id': activity.get_id(),
            'activity'   : book.custom.uid})[0] or None

    logger.debug('publish: title=%s jobject=%s force=%s' \
            % (title, jobject and jobject[0].metadata['activity'], force))

    if jobject:
        if force:
            jobject = jobject[0]
        else:
            try:
                # check for 0.84 code
                from jarabe import config
            except:
                # 0.82 couldn't override .xol bundles
                activity.notify_alert(
                        _('Bundle exists'),
                        _('A bundle by "%s" name already exists. Please ' \
                        'click "Erase" in the Journal. You can click ' \
                        '"Publish" again afterwards.') % \
                        jobject[0].metadata['title'])
                return

            activity.confirmation_alert(
                    _('Overwrite existed bundle?'),
                    _('A bundle for current object was already created. ' \
                          'Click "OK" to overwrite it.'),
                    publish, activity, True)
            jobject[0].destroy()
            return
    else:
        jobject = datastore.create()
        jobject.metadata['activity_id'] = activity.get_id()
        jobject.metadata['activity'] = book.custom.uid
        jobject.metadata['mime_type'] = 'application/vnd.olpc-content'
        jobject.metadata['description'] = \
                'This is a bundle containing articles on %s.\n' \
                'To view these articles, open the \'Browse\' Activity.\n' \
                'Go to \'Books\', and select \'%s\'.' % (title, title)

    book.custom.sync_article()
    book.custom.revision += 1

    jobject.metadata['title'] = title
    _publish(title, jobject)
    jobject.destroy()

    book.custom.sync_index()

"""
@author: Matthew Bailey

This class deals with the creation of content packages, comprised of articles from 
themes, with are zipped up and installed in the relevant OS specific location. From 
here they can be distributed to the consumers 
"""
def _publish(title, jobject):
    zipfilename = '/tmp/infoslicer.xol'
    zip = zipfile.ZipFile(zipfilename, 'w')

    uid = book.custom.uid

    for i in glob(os.path.join(get_bundle_path(), 'Stylesheets', '*')):
        zip.write(i, os.path.join(uid, 'slicecontent', os.path.basename(i)))

    _info_file(zip, uid, title)
    _index_redirect(zip, uid)
    _dita_management(zip, uid, title)
    
    zip.close()

    jobject.set_file_path(zipfilename)
    datastore.write(jobject, transfer_ownership=True)

def _dita_management(zip, uid, title):
    """
        Creates a DITA map, and copies the requested articles and their associated images into the zipped directories
    """
    map = [ '<?xml version=\'1.0\' encoding=\'utf-8\'?>',\
            '<!DOCTYPE map PUBLIC "-//IBM//DTD DITA IBM Map//EN" ' \
                    '"ibm-map.dtd">',\
            '<?xml-stylesheet type="text/xsl" href="mapstylesheet.xsl"?>',\
            '<map title="%s">' % title ]
    
    images = {}

    for entry in book.custom.index:
        if not entry['ready']:
            continue

        atitle = entry['title']
        auid = entry['uid']

        content = BeautifulStoneSoup(book.custom._load(auid))

        for image in content.findAll('image'):
            image_path = book.wiki.root + '/' + image['href']
            image_name = os.path.basename(image_path)
            image_ext = os.path.splitext(image_name)[1]

            image_num = images.get(image_name, len(images))
            images[image_name] = image_num
            image_name = ('%08d%s' % (image_num, image_ext)).encode('CP437')

            zip.write(image_path, os.path.join(uid, 'slicecontent', image_name))
            image['href'] = image_name

        content.insert(1, '<?xml-stylesheet type="text/xsl" ' \
                'href="ditastylesheet.xsl"?>')
        zipstr(zip, os.path.join(uid, 'slicecontent', '%s.dita' % auid),
                content.prettify())

        map.append('<topicref href="%s.dita" navtitle="%s">' % (auid, atitle))
        map.append('</topicref>')

    map.append('</map>')
    zipstr(zip, os.path.join(uid, 'slicecontent', 'librarymap.ditamap'),
            "\n".join(map))

def _index_redirect(zip, uid):
    """
        Creates the redirecting index.html
    """
    redirect_loc = 'slicecontent/librarymap.ditamap'

    html = ['<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN">',\
            '<html>',\
            '<head>',\
            '<title>Redirecting to index</title>',\
            '<meta http-equiv="REFRESH" content="0;url=%s">' % redirect_loc,\
            '</head>',\
            '<body>',\
            '</body>',\
            '</html>']
    
    zipstr(zip, os.path.join(uid, 'index.html'), "\n".join(html))

def _info_file(zip, uid, title):
    """
        Creates the library.info file
    """
    libraryfile = ['[Library]',\
                   'name = %s' % title,\
                   'bundle_class = %s' % uid,\
                   'global_name = info.slice.%s' % title,\
                   'long_name = %s' % title,\
                   'library_version = %d' % book.custom.revision,\
                   'host_version = 1',\
                   'l10n = false',\
                   'locale = en',\
                   'category = books',\
                   'subcategory = slice',\
                   'icon = book.png',\
                   'activity = Web',\
                   'activity_start = index.html']
    
    zipstr(zip, os.path.join(uid, 'library', 'library.info'),
            "\n".join(libraryfile))

# XXX setup mode_t for files written by writestr()
def zipstr(zip, arcname, str):
    import copy
    zipinfo = copy.copy(zip.infolist()[0])
    zipinfo.filename = arcname
    zip.writestr(zipinfo, str)
