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
import logging
import telepathy
from gobject import property, SIGNAL_RUN_FIRST, TYPE_PYOBJECT

from sugar.activity.activity import Activity
from sugar.presence.sugartubeconn import SugarTubeConnection
from sugar.graphics.alert import ConfirmationAlert, NotifyAlert

logger = logging.getLogger('infoslicer')

INSTANCED       = 0
NEW_INSTANCE    = 1
RESUME_INSTANCE = 2

class CanvasActivity(Activity):
    def new_instance(self):
        # stub
        pass
        
    def resume_instance(self, filepath):
        # stub
        pass
    
    def save_instance(self, filepath):
        # stub
        raise NotImplementedError

    def share_instance(self, connection, is_initiator):
        # stub
        pass

    def __init__(self, canvas, handle):
        Activity.__init__(self, handle)

        self.__state = handle.object_id is None \
                and NEW_INSTANCE or RESUME_INSTANCE
        self.__resume_filename = None
        self.__postponed_share = []

        # XXX do it after(possible) read_file() invoking
        # have to rely on calling read_file() from map_cb in sugar-toolkit
        canvas.connect_after('map', self._map_canvasactivity_cb)
        self.set_canvas(canvas)


    def __instance(self, cb, *args):
        for i in self.__postponed_share:
            self.share_instance(i, self._initiating)
        self.__postponed_share = []
        cb(*args)

    def read_file(self, filepath):
        if self.__state != INSTANCED:
            self.__resume_filename = filepath
            self.__state = INSTANCED
        else:
            self.__instance(self.resume_instance, filepath);

    def _map_canvasactivity_cb(self, widget):
        if self.__state == NEW_INSTANCE:
            self.__instance(self.new_instance)
        elif self.__state != INSTANCED:
            self.__state = INSTANCED
        else:
            self.__instance(self.resume_instance, self.__resume_filename);
        return False

    def write_file(self, filepath):
        self.save_instance(filepath)

    def notify_alert(self, title, msg):
        alert = NotifyAlert(title=title, msg=msg)

        def response(alert, response_id, self):
            self.remove_alert(alert)

        alert.connect('response', response, self)
        alert.show_all()
        self.add_alert(alert)

    def confirmation_alert(self, title, msg, cb, *cb_args):
        alert = ConfirmationAlert(title=title, msg=msg)

        def response(alert, response_id, self, cb, *cb_args):
            self.remove_alert(alert)
            if response_id is gtk.RESPONSE_OK:
                cb(*cb_args)

        alert.connect('response', response, self, cb, *cb_args)
        alert.show_all()
        self.add_alert(alert)

class SharedActivity(CanvasActivity):
    def share_instance(self, connection, is_initiator):
        # stub
        pass

    def __init__(self, canvas, service, *args):
        CanvasActivity.__init__(self, canvas, *args)

        self.service = service

        self.connect('shared', self._shared_cb)

        # Owner.props.key
        if self._shared_activity:
            # We are joining the activity
            self.connect('joined', self._joined_cb)
            if self.get_shared():
                # We've already joined
                self._joined_cb()

    def _shared_cb(self, activity):
        logger.debug('My activity was shared')
        self._initiating = True
        self._sharing_setup()

        logger.debug('This is my activity: making a tube...')
        id = self._tubes_chan[telepathy.CHANNEL_TYPE_TUBES].OfferDBusTube(
            self.service, {})

    def _joined_cb(self, activity):
        if not self._shared_activity:
            return

        logger.debug('Joined an existing shared activity')

        self._initiating = False
        self._sharing_setup()
        
        logger.debug('This is not my activity: waiting for a tube...')
        self._tubes_chan[telepathy.CHANNEL_TYPE_TUBES].ListTubes(
            reply_handler=self._list_tubes_reply_cb, 
            error_handler=self._list_tubes_error_cb)

    def _sharing_setup(self):
        if self._shared_activity is None:
            logger.error('Failed to share or join activity')
            return
        self._conn = self._shared_activity.telepathy_conn
        self._tubes_chan = self._shared_activity.telepathy_tubes_chan
        self._text_chan = self._shared_activity.telepathy_text_chan
        
        self._tubes_chan[telepathy.CHANNEL_TYPE_TUBES].connect_to_signal('NewTube', self._new_tube_cb)
        
    def _list_tubes_reply_cb(self, tubes):
        for tube_info in tubes:
            self._new_tube_cb(*tube_info)

    def _list_tubes_error_cb(self, e):
        logger.error('ListTubes() failed: %s', e)

    def _new_tube_cb(self, id, initiator, type, service, params, state):
        logger.debug('New tube: ID=%d initator=%d type=%d service=%s '
                     'params=%r state=%d', id, initiator, type, service, 
                     params, state)

        if (type == telepathy.TUBE_TYPE_DBUS and
                service == self.service):
            if state == telepathy.TUBE_STATE_LOCAL_PENDING:
                self._tubes_chan[telepathy.CHANNEL_TYPE_TUBES].AcceptDBusTube(id)

            tube_conn = SugarTubeConnection(self._conn, 
                self._tubes_chan[telepathy.CHANNEL_TYPE_TUBES], 
                id, group_iface=self._text_chan[telepathy.CHANNEL_INTERFACE_GROUP])
            
            if self.__state == INSTANCED:
                self.share_instance(tube_conn, self._initiating)
            else:
                self.__postponed_share.append(tube_conn)
