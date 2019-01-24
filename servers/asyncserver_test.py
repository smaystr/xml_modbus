"""
Pymodbus Server With Updating Thread
--------------------------------------------------------------------------

This is an example of having a background thread updating the
context while the server is operating. This can also be done with
a python thread::

    from threading import Thread

    thread = Thread(target=updating_writer, args=(context,))
    thread.start()
"""
# --------------------------------------------------------------------------- #
# import the modbus libraries we need
# --------------------------------------------------------------------------- #
from pymodbus.server.async import StartTcpServer
from pymodbus.device import ModbusDeviceIdentification
from pymodbus.datastore import ModbusSequentialDataBlock
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext
# from pymodbus.transaction import ModbusRtuFramer, ModbusAsciiFramer

# --------------------------------------------------------------------------- #
# import the twisted libraries we need
# --------------------------------------------------------------------------- #
from twisted.internet.task import LoopingCall

# --------------------------------------------------------------------------- #
# configure the service logging
# --------------------------------------------------------------------------- #
import logging
logging.basicConfig()
log = logging.getLogger()
log.setLevel(logging.DEBUG)

# --------------------------------------------------------------------------- #
# define your callback process
# --------------------------------------------------------------------------- #
def updating_writer(a):
    """ A worker process that runs every so often and
    updates live values of the context. It should be noted
    that there is a race condition for the update.

    :param arguments: The input arguments to the call
    """
    log.debug("updating the context")
    context = a[0]
    register = 1
    slave_id = 0x00
    address = 1000

    values = context[slave_id].getValues(register, address, count=287)
    # values = [v + 1 for v in values]
    values[0] = 1
    values[13] = 1
    log.debug("new values: " + str(values))
    context[slave_id].setValues(register, address, values)


def run_updating_server():
    # ----------------------------------------------------------------------- #
    # initialize your data store
    # ----------------------------------------------------------------------- #

    store = ModbusSlaveContext(
        di=ModbusSequentialDataBlock(1000, [0]*287),
        # co=ModbusSequentialDataBlock(0, [17]*100),
        # hr=ModbusSequentialDataBlock(0, [17]*100),
        # ir=ModbusSequentialDataBlock(0, [17]*100),
    )
    context = ModbusServerContext(slaves=store, single=True)

    # ----------------------------------------------------------------------- #
    # initialize the server information
    # ----------------------------------------------------------------------- #
    identity = ModbusDeviceIdentification()
    identity.VendorName = 'pymodbus'
    identity.ProductCode = 'PM'
    identity.VendorUrl = 'http://github.com/bashwork/pymodbus/'
    identity.ProductName = 'pymodbus Server'
    identity.ModelName = 'pymodbus Server'
    identity.MajorMinorRevision = '1.0'

    # ----------------------------------------------------------------------- #
    # run the server you want
    # ----------------------------------------------------------------------- #
    time = 5  # 5 seconds delay
    loop = LoopingCall(f=updating_writer, a=(context,))
    loop.start(time, now=False) # initially delay by time
    StartTcpServer(context, identity=identity, address=("192.168..1", 5020))


if __name__ == "__main__":
    run_updating_server()