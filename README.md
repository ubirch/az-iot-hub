# Example for Accessing Azure IoT Hub w/ Pycom Device

- Checkout out the project
  ```
  $ git checkout https://github.com/ubirch/az-iot-hub.git
  ```
- Install [Visual Studio Code](https://code.visualstudio.com/download) or [Atom](https://atom.io) and open the project
- Install pymakr plugin
- Setup an [Azure](https://portal.azure.com) account and create an IoT hub
- Open your IoT hub in Azure Portal and go to `Shared access policies`. 
Select the `device` policy and set an additional check mark for `Registry write`, then copy the `Primary key`.
- Edit `azure.json` and fill in the required details
- Add `config.json` with your WIFI SSID and password
- Upload project to device and run

- optional: 
    - in Visual Studio Code install Azure IoT Hub Toolkit plugin
    - select your device under Azure IoT Hub - Devices and right click to `Start Monitoring Built-in Event Endpoint`
