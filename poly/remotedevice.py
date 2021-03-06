from polyinterface import LOGGER
from polyinterface import Node


class RemoteDevice(Node):

    def __init__(self, controller, primaryDevice, primary, address, driverName,
        deviceName, config, deviceDriver):
        super(RemoteDevice, self).__init__(controller, primary,
            address, deviceName)

        self.id = driverName

        self.driverSetters = {}
        for commandName in config.get('commands', {}).keys():
            self.commands[commandName] = RemoteDevice.execute_command

            polyData = config['poly'].get('commands', {}).get(commandName)
            if polyData and 'driver' in polyData:
                self.drivers.append({
                    'driver': polyData['driver']['name'],
                    'value': 0,
                    'uom': polyData.get('param', {}).get('uom', 25)
                })

                if 'input' in polyData['driver']:
                    self.driverSetters[polyData['driver']['name']] = polyData['driver']['input']

        self.primaryDevice = primaryDevice
        self.deviceDriver = deviceDriver

    def query(self):
        pass

    def execute_command(self, command):
        LOGGER.debug('executing %s', command)
        try:
            self.deviceDriver.executeCommand(command['cmd'], command.get('value'))
            self.refresh_state()
        except:
            LOGGER.exception('Error sending command to ' + self.name)

    def refresh_state(self):
        if self.primaryDevice.connected:
            try:
                for driverName, commandName in self.driverSetters.items():
                    output = self.deviceDriver.getData(commandName)
                    result = output.get('result')
                    if result is not None:
                        self.setDriver(driverName, float(result))
            except:
                LOGGER.exception('Error refreshing ' + self.name + ' device state')
