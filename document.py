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

from gettext import gettext as _

from Processing.Article.Article import Article

source = Article()
working = Article()

def read_file(self, file_path):
    logger.debug("reading the file")
    """ 
    At the moment, the format of a saved file will just be:
    sourcetitle
    edittitle
    edittheme
    currentindex
    """
    
    file = open(file_path, 'r')
    text = file.read()
    file.close()
    lines = text.splitlines()
    if len(lines) < 3:
        return
    sourcetitle = lines[0]
    workingtitle = lines[1]
    workingtheme = lines[2]
    currentindex = int(lines[3])
    
    logger.debug("file read")
    logger.debug("sourcetitle: %s, workingtitle: %s," \
                 "workingtheme: %s, currentindex: %s" %
                 (sourcetitle, workingtitle, workingtheme, currentindex))

    iomanager = IO_Manager()
    if iomanager.page_exists(sourcetitle, "Wikipedia Articles"):
        sourcearticle = iomanager.load_article(sourcetitle, "Wikipedia Articles")
    else:
        sourcearticle = Article()
        sourcearticle.article_title = sourcetitle
        sourcearticle.article_theme = "Wikipedia Articles"
    if iomanager.page_exists(workingtitle, workingtheme):
        workingarticle = iomanager.load_article(workingtitle, workingtheme)
    else:
        workingarticle = Article()
        workingarticle.article_title = workingtitle
        workingarticle.article_theme = workingtheme
    
    self.switch_page(currentindex)
    
    self.currentpane.set_source_article(sourcearticle)
    self.currentpane.set_working_article(workingarticle)

def write_file(self, file_path):
    #article = self.currentpane.get_working_article()
    #IO_Manager().save_article(article)

    logger.debug("writing the file to %s" % file_path)
    sourcearticle = self.currentpane.get_source_article()
    workingarticle = self.currentpane.get_working_article()
    
    sourcetitle = sourcearticle.article_title
    if not sourcetitle:
        sourcetitle = "none"
    workingtitle = workingarticle.article_title
    if not workingtitle:
        workingtitle = "none"
    workingtheme = workingarticle.article_theme
    if not workingtheme:
        workingtheme = "none"
    currentindex = self.currentindex
    
    file = open(file_path, 'w')
    logger.debug("writing source: %s, working: %s, theme: %s" %
            (sourcetitle, workingtitle, workingtheme))
    file.write("%s\n%s\n%s\n%s" % (sourcetitle, workingtitle, workingtheme, str(currentindex)))
    file.close()
    
    
