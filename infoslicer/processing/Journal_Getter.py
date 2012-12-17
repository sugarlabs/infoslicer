# -*- coding: utf-8 -*-
# Copyright (C) Aneesh Dogra <lionaneesh@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# You should have received a copy of the GNU General Public License
# along with this library; if not, write to the Free Software
# Foundation, 51 Franklin Street, Suite 500 Boston, MA 02110-1335 USA

from sugar3.datastore import datastore

def get_starred_images():
    ''' Find all the Starred images in journal. '''
    images = []
    dsobjects, nobjects = datastore.find({'keep': '1'})
    print "Found %d starred images" % (nobjects,)
    for dsobj in dsobjects:
        if hasattr(dsobj, 'metadata') and 'mime_type' in dsobj.metadata and \
            dsobj.metadata['mime_type'][0:5] == 'image':
            if 'title' in dsobj.metadata:
                title = dsobj.metadata['title']
            else:
                title = ''
            images.append((dsobj.file_path, title))

    return images
