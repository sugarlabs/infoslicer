# Copyright (C) IBM Corporation 2008

import os, platform, zipfile, shutil, re
from IO_Manager import IO_Manager
from NewtifulSoup import NewtifulStoneSoup as BeautifulStoneSoup

class Package_Creator:
    """
    @author: Matthew Bailey
    
    This class deals with the creation of content packages, comprised of articles from 
    themes, with are zipped up and installed in the relevant OS specific location. From 
    here they can be distributed to the consumers 
    """
    
    """ 
    Copy articles from library into new content theme (themename) and package up (filename).  
    """
    def __init__(self, articlestocopy, themename, filename, package_type, caller=None):
        """
        Grab file's parent directory and create temporary directory structure for content 
        """
        self.currentdir = os.path.split(__file__)[0]
        self.make_directories(themename)
        if package_type == 'xol':
            self.info_file(themename)
        self.index_redirect(themename, package_type)

        self.dita_management(articlestocopy, themename)
        
        self.copy_stylesheets(themename)
        self.create_bundle(themename, filename)
        
        running_on = platform.system()
        if running_on == "Linux" and "olpc" in platform.platform().lower():
            already_exists = self.copy_to_journal(themename)
            if already_exists == True:
                caller.export_message.set_text('A bundle by that name already exists. Please click "Erase" in the Journal. You can click \'Publish\' again afterwards.')
            elif already_exists == False:
                caller.export_message.set_text('Your bundle has been created and will appear in the Journal. You can also create another.')
            else:
                caller.export_message.set_text('We\'re sorry, but something appears to have gone wrong with bundle creation.')

        """ 
        Remove temporary files
        """
        self.remove_directories(themename)
    
    def copy_stylesheets(self, themename):
        """
            Copies the XSL and CSS stylesheets into the slicecontent folder
            @param themename: the name of the theme that is being exported
        """
        themeloc = themename.replace(" ", "_")
        shutil.copyfile('%s/../Stylesheets/ditastylesheet.xsl' % self.currentdir, '%s/%s/slicecontent/ditastylesheet.xsl' % (IO_Manager().workingDir, themeloc))
        shutil.copyfile('%s/../Stylesheets/mapstylesheet.xsl' % self.currentdir, '%s/%s/slicecontent/mapstylesheet.xsl' % (IO_Manager().workingDir, themeloc))
        shutil.copyfile('%s/../Stylesheets/ditastyle.css' % self.currentdir, '%s/%s/slicecontent/ditastyle.css' % (IO_Manager().workingDir, themeloc))
        shutil.copyfile('%s/../Stylesheets/mapstyle.css' % self.currentdir, '%s/%s/slicecontent/mapstyle.css' % (IO_Manager().workingDir, themeloc))

    def create_bundle(self, themename, filename):
        """
            Creates the xol package and writes the files and directories to the zip
            @param themename: the name of the theme that is being exported
        """
        themeloc = themename.replace(" ", "_")
        running_on = platform.system()
        if running_on == "Linux" and "olpc" in platform.platform().lower():
            zip = zipfile.ZipFile('%s/%s.xol' % (IO_Manager().workingDir, themeloc), 'w')
        else:
            zip = zipfile.ZipFile(filename, 'w')
        self.zipdir('%s/library/' % themeloc, zip)
        self.zipdir('%s/slicecontent/' % themeloc, zip)
        zip.write('%s/%s/index.html' % (IO_Manager().workingDir, themeloc), '%s/index.html' % themeloc)
        zip.close()
        
    def copy_to_journal(self, themename):
        """
            Copies the xol package to the journal, which can then be copied to a USB drive, etc. and also makes content visible in the browser
            @param themename: the name of the theme that is being exported
        """
        from sugar.datastore import datastore
        from sugar import activity
#        from sugar.bundle.contentbundle import ContentBundle
        journal_listing = datastore.find({'title':themename, 'mime_type':'application/vnd.olpc-content'})
#        for id in journal_listing[0]:
#            test = ContentBundle('/home/olpc/.sugar/default/data/%s.xol' % id.object_id)
#            test.uninstall()
#            datastore.delete(id.object_id)
        if not journal_listing[0]:
            themeloc = themename.replace(" ", "_")
            journal_entry = datastore.create()
            activityinfo_list = activity.get_registry().find_activity("Browse")
#            for activityinfo in activityinfo_list:
#                if activityinfo.name == "Browse":
#                    bid = activityinfo.bundle_id
            journal_entry.set_file_path('%s/%s.xol' % (IO_Manager().workingDir, themeloc))
            journal_entry.metadata['title'] = '%s' % themename
#            journal_entry.metadata['activity'] = bid
#            journal_entry.metadata['uri'] = 'file:///home/olpc/.library_pages/search/bundle_index.html'
            journal_entry.metadata['mime_type'] = 'application/vnd.olpc-content'
            journal_entry.metadata['description'] = 'This is a bundle containing articles on %s.\nTo view these articles, first open '\
                                                    'the \'Browse\' Activity.\nGo to \'Books\', and select \'%s\'.' % (themename, themename)
            datastore.write(journal_entry)
            journal_entry.destroy()
            return False
        elif journal_listing[0]:
            return True

    def dita_management(self, articlestocopy, themename):
        """
            Creates a DITA map, and copies the requested articles and their associated images into the zipped directories
            @param articlestocopy: a list of articles to copy
            @param themename: the name of the theme that is being exported
        """
        newmap = ['<?xml version=\'1.0\' encoding=\'utf-8\'?>',\
                  '<!DOCTYPE map PUBLIC "-//IBM//DTD DITA IBM Map//EN" "ibm-map.dtd">',\
                  '<?xml-stylesheet type="text/xsl" href="mapstylesheet.xsl"?>',\
                  '<map title="%s">' % themename]
        
        current_dita_map = IO_Manager().load_map(themename)
        themeloc = themename.replace(" ", "_")
        
        for articlename in articlestocopy:
            articletitle = articlename
            articleloc = current_dita_map.find('topicref', attrs={"navtitle":articlename})['href']
            article = IO_Manager().load_raw_page(articlename, themename)
            #Inserted line above, because line below no longer works due to filename changes
            #article = self.open_article(articleloc.lower())
            self.articlecontent = BeautifulStoneSoup(article)
            for image in self.articlecontent.findAll('image'):
                imageloc = image['href'].replace("..", IO_Manager().workingDir)
                imagename = os.path.split(imageloc)[-1]
                imagename = imagename.replace("%","")  
                shutil.copyfile('%s' % (imageloc), '%s/%s/slicecontent/%s' % (IO_Manager().workingDir, themeloc, imagename))
                image['href'] = imagename
            self.articlecontent.insert(1, '<?xml-stylesheet type="text/xsl" href="ditastylesheet.xsl"?>')
            article = open('%s/%s/slicecontent/%s.dita' % (IO_Manager().workingDir, themeloc, IO_Manager().clean_title(articlename)), 'w')
            article.write(self.articlecontent.prettify())
            newmap.append('\t<topicref href="%s.dita" navtitle="%s">' % (IO_Manager().clean_title(articlename), articletitle))
            newmap.append('\t</topicref>')
        newmap.append('</map>')
        ditamap = open('%s/%s/slicecontent/librarymap.ditamap' % (IO_Manager().workingDir, themeloc), 'w')
        ditamap.write("\n".join(newmap))

    def index_redirect(self, themename, package_type):
        """
            Creates the redirecting index.html
            @param themename: the name of the theme that is being exported
            @param package_type: the type of package (e.g. 'zip' or 'xol') that is being created
        """
        themeloc = themename.replace(" ", "_")
        if package_type == 'xol':
            redirect_loc = '/home/olpc/Library/%s/slicecontent/librarymap.ditamap' % themeloc
        elif package_type == 'zip':
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
        
        htmlfile = open('%s/%s/index.html' % (IO_Manager().workingDir, themeloc), 'w')
        htmlfile.write("\n".join(html))

    def info_file(self, themename):
        """
            Creates the library.info file
            @param themename: the name of the theme that is being exported
        """
        themeloc = themename.replace(" ", "_")
        libraryfile = ['[Library]',\
                       'name = %s' % themeloc,\
                       'global_name = info.slice.%s' % themename.lower(),\
                       'long_name = %s' % themename,\
                       'library_version = 1',\
                       'host_version = 1',\
                       'l10n = false',\
                       'locale = en',\
                       'category = books',\
                       'subcategory = slice',\
                       'icon = book.png',\
                       'activity = Web',\
                       'activity_start = index.html']
        
        infofile = open('%s/%s/library/library.info' % (IO_Manager().workingDir, themeloc), 'w')
        infofile.write("\n".join(libraryfile))
        
    def make_directories(self, themename):
        """
            Creates the directories that will be zipped
            @param themename: the name of the theme that is being exported
        """
        themename = themename.replace(" ", "_")
        if os.path.exists("%s/%s" % (IO_Manager().workingDir, themename)):
            shutil.rmtree("%s/%s" % (IO_Manager().workingDir, themename))
        os.mkdir('%s/%s' % (IO_Manager().workingDir, themename))
        os.mkdir('%s/%s/library' % (IO_Manager().workingDir, themename))
        os.mkdir('%s/%s/slicecontent' % (IO_Manager().workingDir, themename))
        
    def open_article(self, articleloc):
        """
            Opens the relevant DITA file and returns it as a string
            @param articleloc: the location of the DITA file to be opened
            @return: a string containing the contents of the DITA file
        """
        file = open('%s' % (articleloc), 'r').read()
        return file
        
    def remove_directories(self, themename):
        """
            Removes the directories created on the filesystem for the zip
            @param themename: the name of the theme that is being exported
        """
        themename = themename.replace(" ", "_")
        shutil.rmtree("%s/%s" % (IO_Manager().workingDir, themename))

    def zipdir(self, path, zip):
        """
            Writes directories and their contents to the zip 
            @param path: the path of the directory that is to be zipped
            @param zip: the variable name of the zip that is to be written to
        """
        fullpath = '%s/%s' % (IO_Manager().workingDir, path)
        for each in os.listdir(fullpath):
            zip.write(fullpath + each, path + each)