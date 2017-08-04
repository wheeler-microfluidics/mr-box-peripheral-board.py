import logging
import threading

import ipywidgets as ipw


logger = logging.getLogger(__name__)


class PumpUI(object):
    def __init__(self, proxy):
        self.proxy = proxy

        def _pump_frequency(message):
            proxy.pump_frequency_set(message['new'])

        pump_frequency = ipw.FloatSlider(description='Frequency (Hz):', min=1,
                                         max=1e4, value=1e3)
        pump_frequency.observe(_pump_frequency, names=['value'])

        pump_duration = ipw.FloatSlider(description='Duration (s):', min=0,
                                        max=120., value=3.)

        def _pump_trigger(*args):
            cancel = threading.Event()

            def _cancel_pump(*args):
                cancel.set()
            pump_cancel.on_click(_cancel_pump)

            def _pump():
                _disable_widgets()
                proxy.pump_activate()
                try:
                    if cancel.wait(pump_duration.value):
                        logger.warning('Pump action was cancelled.')
                    else:
                        logger.info('Pump action completed.')
                finally:
                    proxy.pump_deactivate()
                    _enable_widgets()
            thread = threading.Thread(target=_pump)
            thread.daemon = True
            thread.start()

        pump_trigger = ipw.Button(description='Pump')
        pump_trigger.on_click(_pump_trigger)

        pump_cancel = ipw.Button(description='Cancel')

        widget = ipw.VBox([pump_frequency, pump_duration, pump_trigger,
                           pump_cancel])
        def _enable_widgets():
            for widget_i in widget.children:
                widget_i.disabled = False
        def _disable_widgets():
            for widget_i in [pump_duration, pump_trigger]:
                widget_i.disabled = True
        self.widget = widget
