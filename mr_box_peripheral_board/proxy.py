from collections import OrderedDict
import time

from base_node_rpc.proxy import ConfigMixinBase
import pandas as pd

from .bin.upload import upload


try:
    # XXX The `node` module containing the `Proxy` class definition is
    # generated from the `mr_box_peripheral_board::Node` class in
    # the C++ file `src/Node.hpp`.
    from .node import (Proxy as _Proxy, I2cProxy as _I2cProxy,
                       SerialProxy as _SerialProxy)
    # XXX The `config` module containing the `Config` class definition is
    # generated from the Protocol Buffer file `src/config.proto`.
    from .config import Config


    class ConfigMixin(ConfigMixinBase):
        @property
        def config_class(self):
            return Config


    class ProxyMixin(ConfigMixin):
        '''
        Mixin class to add convenience wrappers around methods of the generated
        `node.Proxy` class.
        '''
        host_package_name = 'mr-box-peripheral-board'

        def get_adc_calibration(self):
            calibration_settings = \
            pd.Series(OrderedDict([('Self-Calibration_Gain', self.MAX11210_getSelfCalGain()),
                                   ('Self-Calibration_Offset', self.MAX11210_getSelfCalOffset()),
                                   ('System_Gain', self.MAX11210_getSysGainCal()),
                                   ('System_Offset', self.MAX11210_getSysOffsetCal())]))
            return calibration_settings


        class LED(object):
            def __init__(self, parent, pin):
                self._parent = parent
                self._pin = pin
                self._brightness = 0
                self._on = False

                # initialize brightness to 10%
                self.on = False
                self.brightness = 0.1

                # set LED pin as an output
                parent.pin_mode(pin, 1)

            @property
            def brightness(self):
                return self._brightness

            @brightness.setter
            def brightness(self, value):
                if 0 <= value <= 1:
                    self._brightness = value
                else:
                    raise ValueError('Value must be between 0 and 1.')
                if self._on:
                    self._parent.analog_write(self._pin,
                                              self._brightness * 255.0)

            @property
            def on(self):
                return self._on

            @on.setter
            def on(self, value):
                if value:
                    brightness = self._brightness
                else:
                    brightness = 0
                self._on = value
                self._parent.analog_write(self._pin, brightness * 255.0)


        class ZStage(object):
            def __init__(self, parent):
                self._parent = parent

            @property
            def position(self):
                return self._parent._zstage_position()

            @position.setter
            def position(self, value):
                '''
                Move z-stage to specified position.

                **Note** Unlike the other properties, this does not directly
                modify the member variable on the device.  Instead, this relies
                on the ``position`` variable being updated by the device once
                the actual movement is complete.
                '''
                self.move_to(value)

            @property
            def motor_enabled(self):
                return self._parent._zstage_motor_enabled()

            @motor_enabled.setter
            def motor_enabled(self, value):
                self.update_state(motor_enabled=value)

            @property
            def micro_stepping(self):
                return self._parent._zstage_micro_stepping()

            @micro_stepping.setter
            def micro_stepping(self, value):
                self.update_state(micro_stepping=value)

            @property
            def RPM(self):
                return self._parent._zstage_RPM()

            @RPM.setter
            def RPM(self, value):
                self.update_state(RPM=value)

            @property
            def home_stop_enabled(self):
                return self._parent._zstage_home_stop_enabled()

            @home_stop_enabled.setter
            def home_stop_enabled(self, value):
                self.update_state(home_stop_enabled=value)

            @property
            def is_up(self):
                # TODO: if the engaged_stop is enabled, use it
                # This functionality could also be pushed into the firmware
                return (self.state['position'] ==
                        self._parent.config['zstage_up_position'])

            def up(self):
                if not self.is_up:
                    self._parent._zstage_move_to(
                        self._parent.config['zstage_up_position'])
                    time.sleep(1)

            @property
            def is_down(self):
                return (self.state['position'] ==
                        self._parent.config['zstage_down_position'])

            def down(self):
                if not self.is_down:
                    self._parent._zstage_move_to(
                        self._parent.config['zstage_down_position'])

            def home(self):
                self._parent._zstage_home()

            @property
            def engaged_stop_enabled(self):
                return self._parent._zstage_engaged_stop_enabled()

            @engaged_stop_enabled.setter
            def engaged_stop_enabled(self, value):
                self.update_state(engaged_stop_enabled=value)

            @property
            def state(self):
                state = OrderedDict([('engaged_stop_enabled',
                                      self._parent._zstage_engaged_stop_enabled()),
                                     ('home_stop_enabled',
                                      self._parent._zstage_home_stop_enabled()),
                                     ('micro_stepping',
                                      self._parent._zstage_micro_stepping()),
                                     ('motor_enabled',
                                      self._parent._zstage_motor_enabled()),
                                     ('position', self._parent._zstage_position()),
                                     ('RPM', self._parent._zstage_RPM())])
                return pd.Series(state, dtype=object)

            def update_state(self, **kwargs):
                bool_fields = ('engaged_stop_enabled', 'home_stop_enabled',
                            'motor_enabled', 'micro_stepping')
                for key_i, value_i in kwargs.iteritems():
                    if key_i in bool_fields:
                        action = 'enable' if value_i else 'disable'
                        getattr(self._parent, '_zstage_{action}_{0}'
                                .format(key_i.replace('_enabled', ''),
                                        action=action))()
                    else:
                        getattr(self._parent,
                                '_zstage_set_{0}'.format(key_i))(value_i)

            def move_to(self, position):
                self._parent._zstage_move_to(position)

        def __init__(self, *args, **kwargs):
            super(ProxyMixin, self).__init__(*args, **kwargs)
            self.zstage = self.ZStage(self)
            self.led1 = self.LED(self, 5)
            self.led2 = self.LED(self, 6)

        def close(self):
            self.terminate()

        @property
        def id(self):
            return self.config['id']

        @id.setter
        def id(self, id):
            return self.set_id(id)


    class Proxy(ProxyMixin, _Proxy):
        pass

    class I2cProxy(ProxyMixin, _I2cProxy):
        pass

    class SerialProxy(ProxyMixin, _SerialProxy):
        def __init__(self, *args, **kwargs):
            if not 'baudrate' in kwargs:
                kwargs['baudrate'] = 57600
            if not 'settling_time_s' in kwargs:
                kwargs['settling_time_s'] = 2.5
            super(SerialProxy, self).__init__(*args, **kwargs)

        def flash_firmware(self):
            # currently, we're ignoring the hardware version, but eventually,
            # we will want to pass it to upload()
            self.terminate()
            upload()
            time.sleep(0.5)
            self._connect()


except (ImportError, TypeError):
    Proxy = None
    I2cProxy = None
    SerialProxy = None
