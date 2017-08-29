import re
import threading

from matplotlib.backends.backend_gtkagg import (FigureCanvasGTKAgg as
                                                FigureCanvas)
from matplotlib.backends.backend_gtkagg import (NavigationToolbar2GTKAgg as
                                                NavigationToolbar)
from pygtkhelpers.delegates import SlaveView
from serial_device.or_event import OrEvent
import gobject
import gtk
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.ticker
import numpy as np
import pandas as pd
import si_prefix as si

s_formatter = mpl.ticker.FuncFormatter(lambda x, *args: '%ss' %
                                       si.si_format(x))


class StreamingPlot(SlaveView):
    '''
    Multi-threaded, streaming data plot.

    Two threads are spawned by :meth:`start()`:

     1. **Plot**: Wait for incoming data and plot as it becomes available.
     2. **Data**: Start provided function to generate data and trigger event
        whenever new data is ready.

    .. versionchanged:: 0.26

        Use scientific notation for y-axis if SI units are not selected.
    '''
    def __init__(self, data_func, data=None, si_units=True):
        if data is not None:
            self.data = data
        else:
            self.data = []
        # If ``True``, format y-axis tick labels using SI units.
        self.si_units = si_units

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

        # Use SI prefix and seconds units for x (i.e., time) axis.
        self.axis.xaxis.set_major_formatter(s_formatter)

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

                    # Extract y-axis name and unit from data series name.
                    #
                    # Supported formats:
                    #
                    #     "<name> (<unit>)"
                    #     "<name>"
                    #     "(<unit>)"
                    match = re.search(r'(?P<name>.*\w)?\s*'
                                      r'(\((?P<unit>[^\)]+)\))?$',
                                      plot_data.name or '')
                    unit = match.group('unit') if match.group('unit') else ''

                    # Infer units (if available) from data.
                    if self.si_units:
                        # Use SI prefix corresponding to each axis tick value
                        # for units.
                        yformat_func = (lambda x, *args: '%s%s' %
                                        (si.si_format(x, 2), unit))
                        y_formatter = mpl.ticker.FuncFormatter(yformat_func)
                        self.axis.yaxis.set_major_formatter(y_formatter)
                    else:
                        # Use scientific notation.
                        def yformat_func(x, *args):
                            return '%.03g' % x
                        y_formatter = mpl.ticker.FuncFormatter(yformat_func)
                        self.axis.yaxis.set_major_formatter(y_formatter)

                    if match.group('name'):
                        ylabel = match.group('name')
                        if not self.si_units and unit:
                            # Since SI prefixes are not selected, include
                            # measurement unit in y-axis label instead of in
                            # individual tick labels.
                            ylabel += ' ({})'.format(unit)
                        self.axis.set_ylabel(ylabel)

                    absolute_times = plot_data.index.to_series()
                    # Compute time relative to time of first measurement.
                    relative_times = ((absolute_times - absolute_times.iloc[0])
                                      .dt.total_seconds())
                    plot_data.index = relative_times
                    if self.line is None:
                        # No data has been plotted yet.  Plot new line to axis.
                        self.line = self.axis.plot(plot_data.index.values,
                                                   plot_data.values)[0]
                    else:
                        # Update existing plot line with new data points.
                        self.line.set_data(plot_data.index.values,
                                           plot_data.values)

                    # Schedule draw to run in main GTK thread.
                    def _draw_i(axis, plot_data):
                        axis.relim()
                        axis.set_xlim(right=plot_data.index[-1])
                        axis.set_ylim(auto=True)
                        axis.autoscale_view(True, True, True)
                        axis.get_figure().canvas.draw()
                    gobject.idle_add(_draw_i, self.axis, plot_data)

                if self.stop_event.is_set():
                    # Stop has been requested.
                    break

            # Schedule UI buttons to update in main GTK thread based on
            # **paused/stopped state**.
            def _button_states():
                self.start_button.set_label('Continue')
                self.start_button.props.sensitive = True
                self.clear_button.props.sensitive = True
                self.stop_button.props.sensitive = False
            gobject.idle_add(_button_states)

        # Schedule UI buttons to update in main GTK thread based on
        # **running/started state**.
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
        '''
        Schedule re-layout of figure in main GTK loop to fit new widget size.
        '''
        def _tight_layout(*args):
            try:
                self.fig.tight_layout()
            except ValueError:
                pass
        gobject.idle_add(_tight_layout)
