# **Cisco 2960 Flask Web GUI**

A simple Web GUI for Cisco 2960 Switches
It provides a way to visualize the environment status and real-time updates of port activities. 
Obviously in the real world you would use syslog for this but its a fun project

## **Features**
Port Activity: Real-time updates on which ports are up and down.

## **Preview**

![simplescreenrecorder-2024-04-26_19 01 26-ezgif com-video-to-gif-converter](https://github.com/JA-Marshall/Cisco2960-Flask-Web-GUI-/assets/9871373/8f10a8c4-86c1-46d1-8978-1bd602697d62)

![simplescreenrecorder-2024-04-26_19 06 00-ezgif com-video-to-gif-converter](https://github.com/JA-Marshall/Cisco2960-Flask-Web-GUI-/assets/9871373/69841b63-ee2e-4cf8-9d33-1b9ef596eb9c)



## **Prerequisites**

To use this GUI, you will need:

A physical Cisco 2960 switch with either SSH or Serial access.

## **Configuration**

Set Up Credentials: Navigate to app/data/ and update the switch_device_credentials.json file with your switch's IP address, username, and password.Example of JSON format:
```json
{
    "device_type" : "cisco_ios"
    "ip": "192.168.1.1",
    "username": "admin",
    "password": "password123"
}
```

## **Usage**

Run the Application: Execute app.py by running the following command:

```bash
pip install requirements.txt
python app.py
```
Access the GUI: Open your web browser and go to http://127.0.0.1:5000. 
