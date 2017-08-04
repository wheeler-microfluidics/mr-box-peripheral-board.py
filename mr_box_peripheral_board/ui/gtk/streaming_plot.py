import gobject
import gtk

from matplotlib.backends.backend_gtkagg import FigureCanvasGTKAgg as FigureCanvas
from matplotlib.backends.backend_gtkagg import NavigationToolbar2GTKAgg as NavigationToolbar
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import threading
from pygtkhelpers.delegates import SlaveView
from serial_device.or_event import OrEvent

import matplotlib as mpl
import matplotlib.ticker
import si_prefix as si

A_formatter = mpl.ticker.FuncFormatter(lambda x, *args: '%sA' %
                                       si.si_format(x, 2))
s_formatter = mpl.ticker.FuncFormatter(lambda x, *args: '%ss' %
                                       si.si_format(x))


class StreamingPlot(SlaveView):
    '''
    Multi-threaded, streaming data plot.

    Two threads are spawned by :meth:`start()`:

     1. **Plot**: Wait for incoming data and plot as it becomes available.
     2. **Data**: Start provided function to generate data and trigger event
        whenever new data is ready.
    '''
    def __init__(self, data_func, data=None):
        if data is not None:
            self.data = data
        else:
            self.data = []

        self.data_ready = threading.Event()
        self.stop_event = threading.Event()
        self.started = threading.Event()

        self.line = None
        self.axis = None
        self.data_func = data_func
        super(StreamingPlot, self).__init__()

    def create_ui(self):
        def _destroy(*args):
            self.stop_event.set()

        self.widget.connect('destroy', _destroy)

        vbox = gtk.VBox()
        self.widget.add(vbox)

        self.fig, self.axis = plt.subplots()

        canvas = FigureCanvas(self.fig)  # a gtk.DrawingArea
        vbox.pack_start(canvas)
        toolbar = NavigationToolbar(canvas, self.widget)
        vbox.pack_start(toolbar, False, False)
        self.stop_event.clear()
        np.random.seed(0)
        self.axis.xaxis.set_major_formatter(s_formatter)
        self.axis.yaxis.set_major_formatter(A_formatter)

        self.start_button = gtk.Button('Start')
        self.start_button.connect("clicked", lambda *args: self.start())

        self.stop_button = gtk.Button('Pause')
        self.stop_button.connect("clicked", lambda *args:
                                 self.stop_event.set())
        self.stop_button.props.sensitive = False

        self.clear_button = gtk.Button('Reset')
        self.clear_button.connect("clicked", lambda *args: self.reset())
        self.clear_button.props.sensitive = False

        button_box = gtk.HBox()
        for widget_i in (self.start_button, self.stop_button,
                         self.clear_button):
            button_box.pack_start(widget_i, False, False)
        vbox.pack_start(button_box, False, False)

        self.axis.set_ylabel('Current')
        self.axis.set_xlabel('Time')

    def pause(self):
        self.stop_event.set()
        self.started.clear()

    def reset(self):
        self.line = None
        for i in xrange(len(self.data)):
            self.data.pop()

        if self.axis is None:
            return

        for line_i in self.axis.get_lines():
            line_i.remove()
        def _reset_ui(*args):
            self.data_ready.clear()
            self.started.clear()
            self.start_button.set_label('Start')
            self.clear_button.props.sensitive = False
            self.fig.canvas.draw()
        gobject.idle_add(_reset_ui)

    def start(self):
        def _draw():
            self.stop_event.clear()
            wait_event = OrEvent(self.stop_event, self.data_ready)
            while True:
                wait_event.wait()
                if self.data_ready.is_set():
                    self.data_ready.clear()
                    plot_data = pd.concat(self.data)
                    absolute_times = plot_data.index.to_series()
                    relative_times = ((absolute_times - absolute_times.iloc[0])
                                      .dt.total_seconds())
                    plot_data.index = relative_times
                    if self.line is None:
                        self.line = self.axis.plot(plot_data.index.values,
                                                   plot_data.values)[0]
                    else:
                        self.line.set_data(plot_data.index.values,
                                           plot_data.values)

                    def _draw_i(axis, plot_data):
                        axis.relim()
                        axis.set_xlim(right=plot_data.index[-1])
                        axis.set_ylim(auto=True)
                        axis.autoscale_view(True, True, True)
                        axis.get_figure().canvas.draw()
                    gobject.idle_add(_draw_i, self.axis, plot_data)
                if self.stop_event.is_set():
                    break

            def _button_states():
                self.start_button.set_label('Continue')
                self.start_button.props.sensitive = True
                self.clear_button.props.sensitive = True
                self.stop_button.props.sensitive = False
            gobject.idle_add(_button_states)

        def _button_states():
            self.start_button.props.sensitive = False
            self.clear_button.props.sensitive = False
            self.stop_button.props.sensitive = True
        gobject.idle_add(_button_states)

        # Start thread to wait for data and plot it when available.  Also
        # listen for `self.stop_event` and stop thread when it is set.
        thread = threading.Thread(target=_draw)
        thread.daemon = True
        thread.start()

        # Start thread to generate data and set `self.data_ready` event
        # whenever new data is available.
        # Also Listen for `self.stop_event` and stop thread when it is set.
        data_thread = threading.Thread(target=self.data_func,
                                       args=(self.stop_event,
                                             self.data_ready, self.data))
        data_thread.daemon = True
        data_thread.start()
        self.started.set()


    def on_resize(self):
        def _tight_layout(*args):
            try:
                self.fig.tight_layout()
            except ValueError:
                pass
        gobject.idle_add(_tight_layout)
