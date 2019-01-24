# xml_modbus
This app  gets an XML from the socket and sends the data from the Pymodbus Asynchronous Server With Updating Thread (using the twisted library as its backend) 

script can works as a daemon.

$ sudo touch /etc/systemd/system/xml_modbus-daemon.service
$ sudo chmod 664 /etc/systemd/system/xml_modbus-daemon.service

Open the file xml_modbus-daemon.service and add the minimum settings.

for example:
[Unit]
Description=manages xml_modbus worker instances as a service
After=multi-user.target

[Service]
PIDFile=/var/run/xml_modbus.pid
WorkingDirectory=/media/smaystr/disk/SCADA/xml_modbus/
ExecStart=/home/smaystr/.pyenv/versions/tools3/bin/python /media/smaystr/disk/SCADA/xml_modbus/main.py
StandardOutput=syslog
StandardError=syslog
Restart=always
TimeoutStartSec=10
RestartSec=10

[Install]
WantedBy=multi-user.target


it can work with pyenv