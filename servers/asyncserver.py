"""
Pymodbus Asynchronous Server Example
--------------------------------------------------------------------------

The asynchronous server is a high performance implementation using the
twisted library as its backend.  This allows it to scale to many thousands
of nodes which can be helpful for testing monitoring software.
"""
# --------------------------------------------------------------------------- #
# import the various server implementations
# --------------------------------------------------------------------------- #
from pymodbus.server.async import StartTcpServer
# from pymodbus.server.async import StartUdpServer
# from pymodbus.server.async import StartSerialServer

from pymodbus.device import ModbusDeviceIdentification
from pymodbus.datastore import ModbusSequentialDataBlock
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext
# from pymodbus.transaction import (ModbusRtuFramer,
#                                   ModbusAsciiFramer,
#                                   ModbusBinaryFramer)

# --------------------------------------------------------------------------- #
# import the twisted libraries we need
# --------------------------------------------------------------------------- #
from twisted.internet.task import LoopingCall

# --------------------------------------------------------------------------- #
# import the XML client
# --------------------------------------------------------------------------- #
from clients.xmlclient import SocketClientThread, q
from clients.signoflife import client_run
from concurrent.futures import ThreadPoolExecutor
# --------------------------------------------------------------------------- #
# configure the service logging
# --------------------------------------------------------------------------- #
import logging
FORMAT = ('%(asctime)-15s %(threadName)-15s'
          ' %(levelname)-8s %(module)-15s:%(lineno)-8s %(message)s')
logging.basicConfig(format=FORMAT)
log = logging.getLogger()
log.setLevel(logging.DEBUG)

# --------------------------------------------------------------------------- #
# define callback process
# --------------------------------------------------------------------------- #
def updating_sgnol():
    with ThreadPoolExecutor(max_workers=3) as pool:
        pool.submit(client_run)


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

    with ThreadPoolExecutor(max_workers=3) as pool:
        pool.submit(SocketClientThread().start())

    echo = ['0']*10
    results = q.get()
    if results:
        echo = results
    # print(echo)

    values = context[slave_id].getValues(register, address, count=287)

    if echo[1] == 'Camera':
        value = (int(echo[4]) - 1) * 13
        if echo[3] == 'OK':
            values[value] = 1
        else:
            for i in range(13):
                values[value+i] = 0
    elif echo[1] == 'StopF':
        value = (int(echo[4]) - 1) * 13 + 1
        values[value] = 1
    elif echo[1] == 'StopC':
        value = (int(echo[4]) - 1) * 13 + 2
        values[value] = 1
    elif echo[1] == 'SlowVeh':
        value = (int(echo[4]) - 1) * 13 + 3
        values[value] = 1
    elif echo[1] == 'Pedestrian':
        value = (int(echo[4]) - 1) * 13 + 4
        values[value] = 1
    elif echo[1] == 'WrongWay':
        value = (int(echo[4]) - 1) * 13 + 5
        values[value] = 1
    elif echo[1] == 'Visibility':
        value = (int(echo[4]) - 1) * 13 + 6
        values[value] = 1
    elif echo[1] == 'Debris':
        value = (int(echo[4]) - 1) * 13 + 7
        values[value] = 1
    elif echo[1] == 'SlowDown':
        value = (int(echo[4]) - 1) * 13 + 8
        values[value] = 1
    elif echo[1] == 'Intrusion':
        value = (int(echo[4]) - 1) * 13 + 9
        values[value] = 1
    elif echo[1] == 'StopV':
        value = (int(echo[4]) - 1) * 13 + 10
        values[value] = 1
    elif echo[1] == 'User':
        value = (int(echo[4]) - 1) * 13 + 11
        values[value] = 1
    elif echo[1] == 'User24H':
        value = (int(echo[4]) - 1) * 13 + 12
        values[value] = 1

    context[slave_id].setValues(register, address, values)

    log.debug("new values: " + str(values))


def run_updating_server():
    # ----------------------------------------------------------------------- #
    # initialize your data store
    # ----------------------------------------------------------------------- #
    # The datastores only respond to the addresses that they are initialized to
    # Therefore, if you initialize a DataBlock to addresses from 0x00 to 0xFF,
    # a request to 0x100 will respond with an invalid address exception.
    # This is because many devices exhibit this kind of behavior (but not all)
    #
    #     block = ModbusSequentialDataBlock(0x00, [0]*0xff)
    #
    # Continuing, you can choose to use a sequential or a sparse DataBlock in
    # your data context.  The difference is that the sequential has no gaps in
    # the data while the sparse can. Once again, there are devices that exhibit
    # both forms of behavior::
    #
    #     block = ModbusSparseDataBlock({0x00: 0, 0x05: 1})
    #     block = ModbusSequentialDataBlock(0x00, [0]*5)
    #
    # Alternately, you can use the factory methods to initialize the DataBlocks
    # or simply do not pass them to have them initialized to 0x00 on the full
    # address range::
    #
    #     store = ModbusSlaveContext(di = ModbusSequentialDataBlock.create())
    #     store = ModbusSlaveContext()
    #
    # Finally, you are allowed to use the same DataBlock reference for every
    # table or you you may use a seperate DataBlock for each table.
    # This depends if you would like functions to be able to access and modify
    # the same data or not::
    #
    #     block = ModbusSequentialDataBlock(0x00, [0]*0xff)
    #     store = ModbusSlaveContext(di=block, co=block, hr=block, ir=block)
    #
    # The server then makes use of a server context that allows the server to
    # respond with different slave contexts for different unit ids. By default
    # it will return the same context for every unit id supplied (broadcast
    # mode).
    # However, this can be overloaded by setting the single flag to False
    # and then supplying a dictionary of unit id to context mapping::
    #
    #     slaves  = {
    #         0x01: ModbusSlaveContext(...),
    #         0x02: ModbusSlaveContext(...),
    #         0x03: ModbusSlaveContext(...),
    #     }
    #     context = ModbusServerContext(slaves=slaves, single=False)
    #
    # The slave context can also be initialized in zero_mode which means that a
    # request to address(0-7) will map to the address (0-7). The default is
    # False which is based on section 4.4 of the specification, so address(0-7)
    # will map to (1-8)::
    #
    #     store = ModbusSlaveContext(..., zero_mode=True)
    # '''
    # __fx_mapper = {2: 'd', 4: 'i'}
    # __fx_mapper.update([(i, 'h') for i in [3, 6, 16, 22, 23]])
    # __fx_mapper.update([(i, 'c') for i in [1, 5, 15]])
    # '''
    # ----------------------------------------------------------------------- #
    store = ModbusSlaveContext(
        # di=ModbusSequentialDataBlock(1000, [1]*287),
        co=ModbusSequentialDataBlock(1000, [0]*287),
        # hr=ModbusSequentialDataBlock(0, [17] * 100),
        # ir=ModbusSequentialDataBlock(0, [17] * 100),
    )
    context = ModbusServerContext(slaves=store, single=True)

    # ----------------------------------------------------------------------- #
    # initialize the server information
    # ----------------------------------------------------------------------- #
    # If you don't set this or any fields, they are defaulted to empty strings.
    # ----------------------------------------------------------------------- #
    identity = ModbusDeviceIdentification()
    identity.VendorName = 'Pymodbus'
    identity.ProductCode = 'PM'
    identity.VendorUrl = 'http://github.com/bashwork/pymodbus/'
    identity.ProductName = 'Pymodbus Server'
    identity.ModelName = 'Pymodbus Server'
    identity.MajorMinorRevision = '1.5'

    # ----------------------------------------------------------------------- #
    # run the server you want
    # ----------------------------------------------------------------------- #

    # TCP Serverq

    # StartXMLClient
    # StartTcpServer
    time = 5  # 1 seconds delay
    modbus_addr = "0.0.0.0", 5020

    loop = LoopingCall(f=updating_writer, a=(context,))
    loop.start(time, now=False)  # initially delay by time

    updating_sgnol()

    StartTcpServer(context, identity=identity, address=modbus_addr)

    # TCP Server with deferred reactor run

    # from twisted.internet import reactor
    # StartTcpServer(context, identity=identity, address=("localhost", 5020),
    #                defer_reactor_run=True)
    # reactor.run()

    # Server with RTU framer
    # StartTcpServer(context, identity=identity, address=("localhost", 5020),
    #                framer=ModbusRtuFramer)

    # UDP Server
    # StartUdpServer(context, identity=identity, address=("127.0.0.1", 5020))

    # RTU Server
    # StartSerialServer(context, identity=identity,
    #                   port='/dev/ttyp0', framer=ModbusRtuFramer)

    # ASCII Server
    # StartSerialServer(context, identity=identity,
    #                   port='/dev/ttyp0', framer=ModbusAsciiFramer)

    # Binary Server
    # StartSerialServer(context, identity=identity,
    #                   port='/dev/ttyp0', framer=ModbusBinaryFramer)


if __name__ == "__main__":
    run_updating_server()
