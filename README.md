# MR-Box peripheral board firmware #

Firmware for MR-Box controller board for various peripherals (e.g., motorized magnet, LED panels, micro pump, temperature/humidity sensor)

-------------------------------------------------------------------------------

Install
-------

The latest [`mr-box-peripheral-board` release][3] is available as a
[Conda][2] package from the [`wheeler-microfluidics`][4] channel.

To install `mr-box-peripheral-board` in an **activated Conda environment**, run:

    conda install -c wheeler-microfluidics -c conda-forge mr-box-peripheral-board

-------------------------------------------------------------------------------

## Upload firmware ##

To upload the pre-compiled firmware included in the Python package, from an
**activated Conda environment** run the following command:

    python -m mr_box_peripheral_board.bin.upload

-------------------------------------------------------------------------------

Conda package contents
----------------------

The `mr-box-peripheral-board` Conda package includes:

 - `mr_box_peripheral_board.SerialProxy` **Python class** providing a high-level interface to
   the `mr-box-peripheral-board` hardware.
 - **Compiled firmware binary** for the `mr-box-peripheral-board` hardware.

The installed components (relative to the root of the Conda environment) are
shown below:

    ├───Lib
    │   └───site-packages
    │       └───mr_box_peripheral_board (Python package)
    │
    └───Library
        └───bin
            └───platformio
                └───mr-box-peripheral-board (compiled firmware binaries)
                    │   platformio.ini   (PlatformIO environment information)
                    │
                    └───default
                        firmware.hex

-------------------------------------------------------------------------------

## Usage ##

After uploading the firmware to the board, the
`mr_box_peripheral_board.Proxy` class can be used to interact with
the Arduino device.

See the session log below for example usage.

### Example interactive session ###

    >>> import mr_box_peripheral_board

Connect to mr-box-peripheral-board:

    >>> proxy = mr_box_peripheral_board.SerialProxy()

Query the number of bytes free in device RAM.

    >>> proxy.ram_free()
    409

Query descriptive properties of device.

    >>> proxy.properties
    base_node_software_version                               0.9.post8.dev141722557
    name                                                                    mr-box-peripheral-board
    manufacturer                                                           Wheeler Microfluidics Lab
    url                                                                  http://...
    software_version                                                            0.1
    dtype: object

Use Arduino API methods interactively.

    >>> # Set pin 13 as output
    >>> proxy.pin_mode(13, 1)
    >>> # Turn led on
    >>> proxy.digital_write(13, 1)
    >>> # Turn led off
    >>> proxy.digital_write(13, 0)


-------------------------------------------------------------------------------

Develop
-------

**The firmware C++ code** is located in the `src` directory.  The **key
functionality** is **defined in the `mr_box_peripheral_board::Node` class in the file
`Node.h`**.


### Adding new remote procedure call (RPC) methods ###

New methods may be added to the Python API by adding new methods to the
`mr_box_peripheral_board::Node` C++ class in the file `Node.h`.


### Set up development environment (within a Conda environment) ###

 1. **Clone `mr-box-peripheral-board`** source code from [GitHub repository][5].
 2. Create the `.pioenvs` directory if it doesn't already exist.
 3. Run the following command within the root of the cloned repository to
    **install run-time dependencies** and link working copy of firmware
    binaries and Python package for run-time use:

        paver develop_link

 4. **Restart terminal and reactivate Conda environment (e.g., `activate` if
    Conda was installed with default settings).**

Step **4** is necessary since at least one of the installed dependencies sets
environment variables, which are only initialized on subsequent activations of
the Conda environment (i.e., they do not take effect immediately within the
running environment).


### Build firmware ###

Run the following command within the root of the cloned repository to **build
the firmware**:

    paver build_firmware

The compiled firmware binary is available under the `.pioenvs` directory, as
shown below:

    └───.pioenvs
        └───default
                firmware.hex


### Flash/upload firmware ###

To flash/upload a compiled firmware to the hardware, run the following command
from the root of the repository:

    pio run --target upload --target nobuild


### Unlink development working copy ###

Run the following command within the root of the cloned repository to unlink
working copy of firmware binaries and Python package:

    paver develop_unlink

This will allow, for example, installation of a main-line release of the
`mr-box-peripheral-board` Conda package.

-------------------------------------------------------------------------------

License
-------

This project is licensed under the terms of the [MIT License](/LICENSE)

-------------------------------------------------------------------------------

Contributors
------------

 - Christian Fobel ([@wheeler-microfluidics](https://github.com/wheeler-microfluidics))


[1]: https://www.arduino.cc/en/Reference/HomePage
[2]: http://www.scons.org/
[3]: https://github.com/wheeler-microfluidics/mr-box-peripheral-board
