# Copyright (C) IBM Corporation 2008
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


# @author: Matthew Bailey
# This class deals with the creation of content packages, comprised of articles from
# themes, with are zipped up and installed in the relevant OS specific location. From
# here they can be distributed to the consumers


import os
import copy
from gi.repository import Gtk
import zipfile
import uuid
import logging
import parse
from glob import glob
from gettext import gettext as _

from sugar3.activity.activity import get_bundle_path, get_activity_root, get_bundle_name
from sugar3.datastore import datastore
from sugar3 import activity
from sugar3.graphics.alert import NotifyAlert, ConfirmationAlert

from infoslicer.processing.newtiful_soup import NewtifulStoneSoup \
        as BeautifulStoneSoup
import book

logger = logging.getLogger('infoslicer')


def __alert_notify_response_cb(alert, response_id, activity):
    activity.remove_alert(alert)


def __alert_response_cb(alert, response_id, activity, force):
    activity.remove_alert(alert)
    publish(activity, force)


def publish(activity, force=False):
    if not [i for i in book.CUSTOM.index if i['ready']]:
        alert = NotifyAlert(5)
        alert.props.title = _('Nothing to publish')
        alert.props.msg = _('Mark arcticles from "Custom" '
                            'panel and try again.')
        alert.connect('response', __alert_notify_response_cb, activity)
        activity.add_alert(alert)
        alert.show()
        return

    title = activity.metadata['title']
    jobject = datastore.find({
            'activity_id': activity.get_id(),
            'activity'   : book.CUSTOM.uid})[0] or None

    logger.debug('publish: title=%s jobject=%s force=%s' \
            % (title, jobject and jobject[0].metadata['activity'], force))

    if jobject:
        if force:
            jobject = jobject[0]
        else:
            alert = ConfirmationAlert()
            alert.props.title = _('Overwrite existed bundle?')
            alert.props.msg = _('A bundle for current object was already created. '
                                'Click "OK" to overwrite it.')
            alert.connect('response', __alert_response_cb, activity, True)
            activity.add_alert(alert)
            alert.show()
            jobject[0].destroy()
            return
    else:
        jobject = datastore.create()
        jobject.metadata['activity_id'] = activity.get_id()
        jobject.metadata['activity'] = book.CUSTOM.uid
        jobject.metadata['mime_type'] = 'application/vnd.olpc-content'
        jobject.metadata['description'] = \
                'This is a bundle containing articles on {}.\n' \
                'To view these articles, open the \'Browse\' Activity.\n' \
                'Go to \'Books\', and select \'{}\'.'.format(title, title)

    book.CUSTOM.sync_article()
    book.CUSTOM.revision += 1

    jobject.metadata['title'] = title
    _publish(title, jobject)
    jobject.destroy()

    book.CUSTOM.sync_index()

    alert = NotifyAlert()
    alert.props.title = _('Book published to your Journal')
    alert.props.msg = _('You can read the book in Browse or '
                        'access the .xol file from your Journal')
    alert.connect('response', __alert_notify_response_cb, activity)
    activity.add_alert(alert)
    alert.show()


def _publish(title, jobject):
    zipfilename = '/tmp/infoslicer.xol'
    zip = zipfile.ZipFile(zipfilename, 'w')

    uid = book.CUSTOM.uid

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

    for entry in book.CUSTOM.index:
        if not entry['ready']:
            continue

        atitle = entry['title']
        auid = entry['uid']

        content = BeautifulStoneSoup(book.CUSTOM._load(auid))

        for image in content.findAll('image'):
            image_path = book.WIKI.root + '/' + image['href']
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
        zipstr(zip, os.path.join(uid, 'slicecontent', '%s.html' % auid),
                parse.parse_dita(content.prettify()))

        map.append('<topicref href="%s.dita" navtitle="%s">' % (auid, atitle))
        map.append('</topicref>')

    map.append('</map>')
    zipstr(zip, os.path.join(uid, 'slicecontent', 'librarymap.ditamap'),
            "\n".join(map))
    zipstr(zip, os.path.join(uid, 'slicecontent', 'librarymap.html'),
            parse.parse_ditamap("\n".join(map)))

def _index_redirect(zip, uid):
    """
        Creates the redirecting index.html
    """
    redirect_loc = 'slicecontent/librarymap.html'

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
                   'library_version = %d' % book.CUSTOM.revision,\
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
    zipinfo = copy.copy(zip.infolist()[0])
    zipinfo.filename = arcname
    zip.writestr(zipinfo, str)
