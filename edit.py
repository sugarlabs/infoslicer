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

from GUI_Components.Edit_Pane import Edit_Pane
from GUI_Components.Format_Pane import Format_Pane
from GUI_Components.Image_Pane import Image_Pane

class View(gtk.EventBox):
    def __init__(self):
        gtk.EventBox.__init__(self)

        self.pane = Edit_Pane()
        self.pane.panel.show()
        self.add(self.pane.panel)

class Toolbar(gtk.Toolbar):
    def __init__(self, edit):
        gtk.Toolbar.__init__(self)
        self.edit = edit
