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
import gobject

from sugar.graphics.icon import Icon
import sugar.graphics.style as style

class WidgetItem(gtk.ToolItem):
    def __init__(self, widget):
        gtk.ToolItem.__init__(self)
        self.add(widget)
        widget.show()

class ButtonItem(gtk.ToolButton):
    def __init__(self, icon_name, size=gtk.ICON_SIZE_SMALL_TOOLBAR, **kwargs):
        gobject.GObject.__init__(self, **kwargs)

        icon = Icon(icon_name=icon_name, icon_size=size)
        # The alignment is a hack to work around gtk.ToolButton code
        # that sets the icon_size when the icon_widget is a gtk.Image
        alignment = gtk.Alignment(0.5, 0.5)
        alignment.add(icon)
        self.set_icon_widget(alignment)

        if size == gtk.ICON_SIZE_SMALL_TOOLBAR:
            button_size = style.SMALL_ICON_SIZE + 8
            self.set_size_request(button_size, button_size)
