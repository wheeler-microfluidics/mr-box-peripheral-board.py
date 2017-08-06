from collections import OrderedDict

from base_node_rpc.proxy import ConfigMixinBase
import pandas as pd


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

        class ZStage(object):
            def __init__(self, parent):
                self.parent = parent

            @property
            def position(self):
                return self.parent.zstage_position()

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
                return self.parent.zstage_motor_enabled()

            @motor_enabled.setter
            def motor_enabled(self, value):
                self.update_state(motor_enabled=value)

            @property
            def micro_stepping(self):
                return self.parent.zstage_micro_stepping()

            @micro_stepping.setter
            def micro_stepping(self, value):
                self.update_state(micro_stepping=value)

            @property
            def RPM(self):
                return self.parent.zstage_RPM()

            @RPM.setter
            def RPM(self, value):
                self.update_state(RPM=value)

            @property
            def home_stop_enabled(self):
                return self.parent.zstage_home_stop_enabled()

            @home_stop_enabled.setter
            def home_stop_enabled(self, value):
                self.update_state(home_stop_enabled=value)

            def engage(self):
                self.parent.zstage_move_to(
                    self.parent.config['zstage_up_position'])

            def home(self):
                self.parent.zstage_home()

            @property
            def engaged(self):
                # TODO: if the engaged_stop is enabled, use it
                # This functionality could also be pushed into the firmware
                return self.state['position'] == self.parent.config['zstage_up_position']

            @property
            def engaged_stop_enabled(self):
                return self.parent.zstage_engaged_stop_enabled()

            @engaged_stop_enabled.setter
            def engaged_stop_enabled(self, value):
                self.update_state(engaged_stop_enabled=value)

            @property
            def state(self):
                state = OrderedDict([('engaged_stop_enabled',
                                      self.parent.zstage_engaged_stop_enabled()),
                                     ('home_stop_enabled',
                                      self.parent.zstage_home_stop_enabled()),
                                     ('micro_stepping',
                                      self.parent.zstage_micro_stepping()),
                                     ('motor_enabled',
                                      self.parent.zstage_motor_enabled()),
                                     ('position', self.parent.zstage_position()),
                                     ('RPM', self.parent.zstage_RPM())])
                return pd.Series(state, dtype=object)

            def update_state(self, **kwargs):
                bool_fields = ('engaged_stop_enabled', 'home_stop_enabled',
                            'motor_enabled', 'micro_stepping')
                for key_i, value_i in kwargs.iteritems():
                    if key_i in bool_fields:
                        action = 'enable' if value_i else 'disable'
                        getattr(self.parent, 'zstage_{action}_{0}'
                                .format(key_i.replace('_enabled', ''),
                                        action=action))()
                    else:
                        getattr(self.parent,
                                'zstage_set_{0}'.format(key_i))(value_i)

            def move_to(self, position):
                self.parent.zstage_move_to(position)

        def __init__(self, *args, **kwargs):
            super(ProxyMixin, self).__init__(*args, **kwargs)
            self.zstage = self.ZStage(self)

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
        @property
        def port(self):
            return self.serial_thread.protocol.port



except (ImportError, TypeError):
    Proxy = None
    I2cProxy = None
    SerialProxy = None
