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

import gtk
from gettext import gettext as _

from sugar.graphics.toolbutton import ToolButton
from sugar.graphics.toggletoolbutton import ToggleToolButton
from sugar.activity.activity import ActivityToolbox

from GUI_Components.Library_Pane import Library_Pane

class View(gtk.EventBox):
    def __init__(self):
        gtk.EventBox.__init__(self)

        self.pane = Library_Pane()
        self.pane.panel.show()
        self.add(self.pane.panel)

        """
        # Set up dummy library if appropriate
        IO_Manager().install_library()

        themes = IO_Manager().get_themes()
        if "Wikipedia Articles" in themes:
            i = themes.index("Wikipedia Articles")
            del themes[i]
            
        wikiarticles = IO_Manager().get_pages_in_theme("Wikipedia Articles")
        for theme in themes:
            articles = IO_Manager().get_pages_in_theme(theme)
            for article in articles:
                if ignore == True:
                    break
                for wikiarticle in wikiarticles:
                    if article in wikiarticle:
                        self.source = IO_Manager().load_article(wikiarticle, "Wikipedia Articles")
                        self.working = IO_Manager().load_article(article, theme) 
                        logger.debug("loading source %s from %s" %
                                (wikiarticle, "Wikipedia Articles"))
                        logger.debug("loading edit %s from %s" %
                                (article, theme))
                        ignore = True
        """

class Toolbar(gtk.Toolbar):
    def __init__(self, library):
        gtk.Toolbar.__init__(self)
        self.library = library
