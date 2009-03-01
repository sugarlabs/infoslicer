# Copyright (C) IBM Corporation 2008

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
from sugar.graphics.alert import ConfirmationAlert, NotifyAlert

from Processing.NewtifulSoup import NewtifulStoneSoup as BeautifulStoneSoup
import book

logger = logging.getLogger('infoslicer')

def publish(activity, force=False):
    if not [i for i in book.custom.map if i['ready']]:
        alert = NotifyAlert(
                title=_('Nothing to publich'),
                msg=_('Mark arcticles from "Custom" panel and try again.'))

        def response(alert, response_id, activity):
            activity.remove_alert(alert)

        alert.connect('response', response, activity)
        alert.show_all()
        activity.add_alert(alert)

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
            alert = ConfirmationAlert(
                    title=_('Overwrite existed bundle?'),
                    msg=_('A bundle for current object was already created. ' \
                          'Click "OK" to overwrite it.'))

            def response(alert, response_id, activity):
                activity.remove_alert(alert)
                if response_id is gtk.RESPONSE_OK:
                    publish(activity, True)

            alert.connect('response', response, activity)
            alert.show_all()
            activity.add_alert(alert)
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

    book.custom.sync()
    jobject.metadata['title'] = title
    _publish(title, jobject)
    jobject.destroy()

"""
@author: Matthew Bailey

This class deals with the creation of content packages, comprised of articles from 
themes, with are zipped up and installed in the relevant OS specific location. From 
here they can be distributed to the consumers 
"""
def _publish(title, jobject):
    zipfilename = os.path.join(get_activity_root(), 'tmp', 'publish.xol')
    zip = zipfile.ZipFile(zipfilename, 'w')

    uid = book.custom.uid

    for i in glob(os.path.join(get_bundle_path(), 'Stylesheets', '*')):
        zip.write(i, os.path.join(uid, 'slicecontent', os.path.basename(i)))

    _info_file(zip, uid, title)
    _index_redirect(zip, uid)
    _dita_management(zip, uid, title)
    
    zip.close()

    jobject.set_file_path(zipfilename)
    datastore.write(jobject)

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

    for entry in book.custom.map:
        if not entry['ready']:
            continue

        atitle = entry['title']
        auid = entry['uid']

        content = BeautifulStoneSoup(book.custom._load(auid))

        for image in content.findAll('image'):
            image_path = image['href'].replace("..", book.wiki.root)
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
                   'name = %s' % uid,\
                   'bundle_id = info.slice.%s' % uid,\
                   'global_name = info.slice.%s' % uid,\
                   'long_name = %s' % title,\
                   'library_version = 1',\
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
