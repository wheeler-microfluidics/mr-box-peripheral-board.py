import ipywidgets as ipw
import si_prefix as si


class PmtUI(object):
    def __init__(self, proxy):
        self.proxy = proxy

        pmt_pot = ipw.IntSlider(min=0, max=255, value=230,
                                description='Potentiometer:')

        def format_voltage(value):
            '''
            Format voltage value using SI prefixes.
            '''
            return '{}V'.format(si.si_format(value))

        def _pmt_pot(message):
            '''
            Set digital potentiometer according to slider value.
            '''
            voltage = proxy.pmt_set_pot(message['new'])
            reference_voltage.value = format_voltage(voltage)

        pmt_pot.observe(_pmt_pot, names=['value'])

        reference_voltage_label = ipw.Label(value='Reference:')
        reference_voltage = ipw.Label(value=
                                      format_voltage(proxy
                                                     .pmt_reference_voltage()))
        pmt_shutter = ipw.RadioButtons(description='Shutter:',
                                    options=['closed', 'open'])
        def _pmt_shutter(message):
            '''
            Open/close the shutter according to selected radio button.
            '''
            if message['new'] == 'open':
                proxy.pmt_open_shutter()
            else:
                proxy.pmt_close_shutter()
        pmt_pot.observe(_pmt_shutter, names=['value'])

        self.widget = ipw.VBox([pmt_pot, ipw.HBox([reference_voltage_label,
                                                   reference_voltage]),
                                pmt_shutter])
