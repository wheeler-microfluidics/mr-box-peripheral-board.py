import datetime as dt
import threading

from serial_device.or_event import OrEvent
import numpy as np
import pandas as pd
import gobject
import gtk
import matplotlib as mpl

from streaming_plot import StreamingPlot
from ...max11210_adc_ui import MAX11210_read
import logging

def _generate_data(stop_event, data_ready, data):
    '''
    Generate random data to emulate, e.g., reading data from ADC.

    The function is an example implementation of a ``f_data`` function
    suitable for use with the :func:`measure_dialog` function.

    Example usage
    -------------

    The following launches a measurement dialog which plots 5 points every
    0.5 seconds, runs for 5 seconds, after which the dialog closes
    automatically:

        >>> data = measure_dialog(_generate_data, duration_s=5000, auto_close=True)

    Parameters
    ----------
    stop_event : threading.Event
        Function returns when :data:`stop_event` is set.
    data_ready : threading.Event
        Function sets :data:`data_ready` whenever new data is available.
    data : list
        Function appends new data to :data:`data` before setting
        :data:`data_ready`.
    '''
    delta_t = dt.timedelta(seconds=.1)
    samples_per_plot = 5

    while True:
        time_0 = dt.datetime.now()
        values_i = np.random.rand(samples_per_plot)
        absolute_times_i = pd.Series([time_0 + i * delta_t
                                      for i in xrange(len(values_i))])
        data_i = pd.Series(values_i, index=absolute_times_i)
        data.append(data_i)
        data_ready.set()
        if stop_event.wait(samples_per_plot *
                           delta_t.total_seconds()):
            break


def measure_dialog(f_data, duration_s=None, auto_start=True,
                   auto_close=True, **kwargs):
    '''
    Launch a GTK dialog and plot data

    Parameters
    ----------
    f_data : function(stop_event, data_ready, data)
        Function to run to generate data, e.g., read data from ADC.

        The function is run in its own thread and is provided the following
        parameters:

         - :data:`stop_event` : threading.Event
         - :data:`data_ready` : threading.Event
         - :data:`data` : list

        The function **MUST**:

         - Return when the :data:`stop_event` is set.
         - Set :data:`data_ready` event whenever new data is available.
    duration_s : float, optional
        Length of time to measure for (in seconds).

        If duration is not specified, measure until window is closed or
        ``Pause`` button is pressed.
    auto_start : bool, optional
        Automatically start measuring when the dialog is launched.

        Default is ``True``.
    auto_close : bool, optional
        If ``duration_s`` is specified, automatically close window once the
        measurement duration has passed (unless the ``Pause`` button has been
        pressed.

        Default is ``True``.
    **kwargs : dict
        Additional keyword arguments are passed to the construction of the
        :class:`streaming_plot.StreamingPlot` view.
    '''
    # `StreamingPlot` class uses threads.  Need to initialize GTK to use
    # threads. See [here][1] for more information.
    #
    # [1]: http://faq.pygtk.org/index.py?req=show&file=faq20.001.htp
    gtk.gdk.threads_init()

    with mpl.style.context('seaborn',
                           {'image.cmap': 'gray',
                            'image.interpolation' : 'none'}):
        # Create dialog window to wrap PMT measurement view widget.
        dialog = gtk.Dialog()
        dialog.set_default_size(800, 600)
        view = StreamingPlot(data_func=f_data, **kwargs)
        dialog.get_content_area().pack_start(view.widget, True, True)
        dialog.connect('check-resize', lambda *args: view.on_resize())
        dialog.set_position(gtk.WIN_POS_MOUSE)
        dialog.show_all()
        view.fig.tight_layout()
        if auto_start:
            gobject.idle_add(view.start)

        def _auto_close(*args):
            if not view.stop_event.is_set():
                # User did not explicitly pause the measurement.  Automatically
                # close the measurement and continue.
                dialog.destroy()

        measurement_complete = threading.Event()

        view.widget.connect('destroy', lambda *args: measurement_complete.set())

        if duration_s is not None:
            def _schedule_stop(*args):
                event = OrEvent(view.stop_event, view.started,
                                measurement_complete)
                event.wait()
                if view.started.is_set():
                    stop_func = _auto_close if auto_close else view.pause
                    gobject.timeout_add(duration_s * 1000, stop_func)
            stop_schedule_thread = threading.Thread(target=_schedule_stop)
            stop_schedule_thread.daemon = True
            stop_schedule_thread.start()

        dialog.run()
        dialog.destroy()

        measurement_complete.wait()
        if view.data:
            return pd.concat(view.data)
        else:
            return None
        return False


def adc_data_func_factory(proxy, delta_t=dt.timedelta(seconds=1), adc_dgain=1, adc_rate=1 ):
    '''
    Parameters
    ----------
    proxy : mr_box_peripheral_board.SerialProxy
    delta_t : datetime.timedelta
        Time between ADC measurements.

    Returns
    -------
    function
        Function suitable for use with the :func:`measure_dialog` function.
    '''
    #set the adc digital gain
    proxy.MAX11210_setGain(adc_dgain)
    #Set the pmt shutter pin to output
    proxy.pin_mode(9, 1)

    logger = logging.getLogger(__name__)
    def _read_adc(stop_event, data_ready, data):
        '''
        Parameters
        ----------
        stop_event : threading.Event
            Function returns when :data:`stop_event` is set.
        data_ready : threading.Event
            Function sets :data:`data_ready` whenever new data is available.
        data : list
            Function appends new data to :data:`data` before setting
            :data:`data_ready`.
            delta_t = dt.timedelta(seconds=.1)
        '''
        
        #Start the ADC
        try:
            proxy.pmt_open_shutter()
            logger.info('PMT Shutter Opened')
            while True:
                data_i = MAX11210_read(proxy, rate=adc_rate,
                                       duration_s=delta_t.total_seconds())
                #Convert data to Voltage, 24bit ADC with Vref = 3.0 V
                data_i /=  ((2 ** 24 - 1)/(3.0/adc_dgain))
                #Convert Voltage to Current, 30kOhm Resistor
                data_i /= 30e3
                # Set name to display units.
                data_i.name = 'Current (A)'
                data.append(data_i)
                data_ready.set()
                if stop_event.is_set():
                    break
        finally:
            proxy.pmt_close_shutter()
            logger.info('PMT Shutter Closed')
    return _read_adc
