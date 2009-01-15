#!/usr/bin/env python
# Copyright (C) IBM Corporation 2008
# Taken from the OLPC Wiki.
try:
    from sugar.activity import bundlebuilder
    bundlebuilder.start("InfoSlicer")
except ImportError:
    import os
    os.system("find ./ | sed 's,^./,InfoSlicer.activity/,g' > MANIFEST")
    os.system('rm InfoSlicer.xo')
    os.chdir('..')
    os.system('zip -r InfoSlicer.xo InfoSlicer.activity')
    os.system('mv InfoSlicer.xo ./InfoSlicer.activity')
    os.chdir('InfoSlicer.activity')