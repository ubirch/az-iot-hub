# Example for Accessing IBM Cloud w/ Pycom Device

#### Prerequisites
- Editor ([Visual Studio Code](https://code.visualstudio.com/download) or [Atom](https://atom.io)) with pymakr plugin installed

#### How to send sensor data to IBM Cloud
- Setup an [IBM Cloud account](https://cloud.ibm.com/registration) and create a Watson IoT Platform instance.
    > You can choose the *Lite service plan*
- Register your device. Follow Step 1 of [this tutorial](https://cloud.ibm.com/docs/services/IoT?topic=iot-platform-getting-started#step1)
- Fill out `ibm_cloud.json` in this project with the organization ID, device type, device ID, and authentication token
- Add `config.json` with your WIFI SSID and password
- Upload project to device using pymakr and run

> You can find a tutorial on how to visualize your sensor data in the Watson IoT Platform [here](https://cloud.ibm.com/docs/tutorials?topic=solution-tutorials-gather-visualize-analyze-iot-data#createcards).