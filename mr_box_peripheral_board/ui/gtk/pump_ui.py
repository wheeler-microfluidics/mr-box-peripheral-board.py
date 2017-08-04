import threading
import logging; logging.basicConfig(level=logging.DEBUG)
import gobject
import gtk

from pygtkhelpers.delegates import SlaveView

logger = logging.getLogger(__name__)


class PumpControl(SlaveView):
    def __init__(self, proxy, frequency_hz=1000, duration_s=3):
        self.proxy = proxy
        self.duration_s = duration_s
        self.frequency_hz = frequency_hz
        super(PumpControl, self).__init__()

    def create_ui(self):
        def _pump_frequency(adj):
            try:
                self.proxy.pump_frequency_set(adj.value)
            except:
                logger.debug('[_pump_frequency] Error setting pump frequency'
                             ' to %s.', adj.value)

        # value, lower, upper, step_increment, page_increment, page_size
        # Note that the page_size value only makes a difference for
        # scrollbar widgets, and the highest value you'll get is actually
        # (upper - page_size).
        self.frequency_adj = gtk.Adjustment(self.frequency_hz, 1, 1e4 + 10,
                                            0.1, 1.0, 10)
        self.frequency_scale = gtk.HScale(self.frequency_adj)

        self.duration_adj = gtk.Adjustment(self.duration_s, 0, 120 + 10, 0.1,
                                           1.0, 10)
        self.duration_scale = gtk.HScale(self.duration_adj)

        for label_i, scale_i in ((gtk.Label("Frequency (Hz):"),
                                  self.frequency_scale),
                                 (gtk.Label("Duration (s):"),
                                  self.duration_scale)):
            scale_i.set_size_request(200, 50)
            scale_i.set_update_policy(gtk.UPDATE_CONTINUOUS)
            scale_i.set_digits(1)
            scale_i.set_value_pos(gtk.POS_TOP)
            scale_i.set_draw_value(True)
            box_i = gtk.HBox()
            box_i.pack_start(label_i, False, False, 0)
            box_i.pack_start(scale_i, True, True, 0)
            self.widget.pack_start(box_i, False, False, 0)

        self.widget.show_all()

        self.frequency_adj.connect('value_changed', _pump_frequency)

        self.pump_button = gtk.Button('Pump')
        self.pump_button.connect('clicked', lambda *args: self.start())

        self.pump_cancel = gtk.Button('Cancel')
        self.pump_cancel.props.sensitive = False

        self.button_box = gtk.HBox()
        self.widget.pack_start(self.button_box, True, True)
        for widget_i in (self.pump_button, self.pump_cancel):
            self.button_box.pack_start(widget_i, True, True)
        self._enable_widgets()

    def _enable_widgets(self):
        for widget_i in (self.frequency_scale, self.duration_scale,
                         self.pump_button):
            widget_i.props.sensitive = True
        self.pump_cancel.props.sensitive = False

    def _disable_widgets(self):
        for widget_i in [self.duration_scale, self.pump_button]:
            widget_i.props.sensitive = False

    def start(self):
        cancel = threading.Event()

        def _cancel_pump(*args):
            cancel.set()
        gobject.idle_add(self.pump_cancel.connect, 'clicked',
                         _cancel_pump)

        def _pump():
            gobject.idle_add(self._disable_widgets)
            if self.proxy is not None:
                self.proxy.pump_frequency_set(self.frequency_adj.value)
                self.proxy.pump_activate()
            self.pump_cancel.props.sensitive = True
            try:
                if cancel.wait(self.duration_adj.value):
                    logger.warning('Pump action was cancelled.')
                else:
                    logger.info('Pump action completed.')
            finally:
                if self.proxy is not None:
                    self.proxy.pump_deactivate()
                gobject.idle_add(self._enable_widgets)
        thread = threading.Thread(target=_pump)
        thread.daemon = True
        thread.start()
