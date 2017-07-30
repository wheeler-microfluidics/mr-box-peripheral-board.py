from base_node_rpc.proxy import ConfigMixinBase, StateMixinBase


try:
    # XXX The `node` module containing the `Proxy` class definition is
    # generated from the `mr_box_peripheral_board::Node` class in
    # the C++ file `src/Node.hpp`.
    from .node import (Proxy as _Proxy, I2cProxy as _I2cProxy,
                       SerialProxy as _SerialProxy)
    # XXX The `config` module containing the `Config` class definition is
    # generated from the Protocol Buffer file `src/config.proto`.
    from .config import Config
    # XXX The `state` module containing the `State` class definition is
    # generated from the Protocol Buffer file `src/state.proto`.
    from .state import State

    class ConfigMixin(ConfigMixinBase):
        @property
        def config_class(self):
            return Config


    class StateMixin(StateMixinBase):
        @property
        def state_class(self):
            return State


    class ProxyMixin(ConfigMixin, StateMixin):
        '''
        Mixin class to add convenience wrappers around methods of the generated
        `node.Proxy` class.
        '''
        host_package_name = 'mr-box-peripheral-board'

        def __init__(self, *args, **kwargs):
            super(ProxyMixin, self).__init__(*args, **kwargs)

        def __del__(self):
            super(ProxyMixin, self).__del__()

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
