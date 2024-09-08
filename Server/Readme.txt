This code host a webserver to receive bticino alerts.
Alerts can provide battery info that is stored in battery.txt.
The server can have 3 states (ON/OFF/STANDBY).

Endpoints
    /alert?battery=4.123
    Handle alert with optional battery info

    /status
    Returns current status (ON/OFF/STANDBY)

    /battery
    Returns the content of battery.txt


!!!! IMPORTANT !!!!
To write to the battery file, the code needs write access to storage.
Either the code or the volume mount can have read access so by default usb will be readonly.
To get readwrite access via usb, do the following;

- open a serial connection to the controller
- in the REPL, run the following commands;
    - import os
    - os.listdir()          > list file in current dir (root)
    - os.remove('boot.py')  > remove the boot.py file
    - os.listdir()          > validate the file is gone
- disconnect/reconnect power

The drive will be mounted with readwrite access.
To reenable readwrite for the code, do the following;

- create file boot.py in root.
- add following content in the file
    import storage
    storage.remount("/", False)
- disconnect/reconnect power