import time

import ipywidgets as ipw


class ZStageUI(object):
    def __init__(self, proxy):
        self.proxy = proxy

        def zstage_move_to(position):
            proxy.zstage.motor_enabled = True
            proxy.zstage.move_to(position)
            proxy.zstage.motor_enabled = False

        # Set initial end-point positions based on positions stored in EEPROM
        # configuration.
        config = proxy.config
        zstage_range = ipw.FloatRangeSlider(min=0, max=11, step=.05,
                                            value=(config.zstage_down_position,
                                                   config.zstage_up_position),
                                            description='position range:')
        def zstage_range_changed(message):
            '''
            Update z-stage position if the respective end location has been
            modified.
            '''
            if message['old'][0] == message['new'][0]:
                # Range **max** has changed.
                if zstage_state.value == 'up':
                    # Magnet is in "up" position.  Move magnet to new range max
                    # position.
                    zstage_move_to(message['new'][1])
            else:
                # Range **min** has changed.
                if zstage_state.value in 'down':
                    # Magnet is in "down" position.  Move magnet to new range
                    # min position.
                    zstage_move_to(message['new'][0])
        zstage_range.observe(zstage_range_changed, names=['value'])

        def _zstage_range_load(*args):
            '''
            Load z-stage end positions from EEPROM configuration.
            '''
            config = proxy.config
            zstage_range.value = (config.zstage_down_position,
                                  config.zstage_up_position)
        zstage_range_load = ipw.Button(description='Load end positions')
        zstage_range_load.on_click(_zstage_range_load)

        def _zstage_range_save(*args):
            '''
            Save z-stage end positions to EEPROM configuration.
            '''
            min_, max_ = zstage_range.value
            proxy.update_config(zstage_down_position=min_,
                                zstage_up_position=max_,)
        zstage_range_save = ipw.Button(description='Save end positions')
        zstage_range_save.on_click(_zstage_range_save)

        def _zstage_home(*args):
            '''
            Home z-stage using end-stop.
            '''
            proxy.zstage.motor_enabled = True
            try:
                proxy.zstage.home()
            finally:
                proxy.zstage.motor_enabled = False
            zstage_state.value = 'down'

        zstage_home = ipw.Button(description='Home')
        zstage_home.on_click(_zstage_home)

        def _zstage_state(message):
            '''
            Toggle z-stage between "up" and "down" states.
            '''
            min_, max_ = zstage_range.value
            if message['new'] == 'up':
                # Engage magnet.
                position = max_
                zstage_state.value = 'up'
            else:
                # Disengage magnet.
                position = min_
                zstage_state.value = 'down'
            zstage_move_to(position)

        zstage_state = ipw.RadioButtons(options=['up', 'down'], value='down')
        zstage_state.observe(_zstage_state, names=['value'])

        # Start with z-stage in **home** position.
        _zstage_home()

        self.widget = ipw.VBox([zstage_home, ipw.HBox([zstage_range,
                                                       zstage_range_save,
                                                       zstage_range_load]),
                                zstage_state])
