# Real Debrid Manager

Docker Repo : [https://hub.docker.com/r/hyperbunny77/realdebridmanager](https://hub.docker.com/r/hyperbunny77/realdebridmanager)

This project aims to automate many functions of the Real Debrid Service.
It is intended to slot into your existing workflows. Please see examples below.

### __**Core Functionality :**__

* Detect torrent file in watched folder.
* Submit to Real Debrid for action.
* Watch/manage Real Debrid until file is ready for download.
* Get Real Debrid link to file in torrent.
* Send to local download client (Aria2).
* Move Torrent file to completed/errored Folders

## Core Setup :

Deploy the application via the use of docker. Please use the below docker compose as a template :

```
  realdebridmanager:
    image: hyperbunny77/realdebridmanager:2022.05.22   #Change to the latest release
    container_name: realdebridmanager
    ports:
      - 5000:5000/tcp 	
    volumes:
      - torrent_folder_to_watch:/watch
      - path_for_config_storage:/config
    restart: unless-stopped
```
* Navigate to your devices IP address with the port of "5000" (yourIP:5000)
* The system will ask you to fill out the settings page.
* Please follow the prompts under each setting clearly.
* The application **_will not_** function without Aria2 details and Realdebrid API Key
* Once Setup you will be taken to the main page. Please see "How to Use" section below for more details.


## Sonarr/Radarr Integration :

This application fits great into your workflow with Sonarr/Radarr.
The use of Real Debrid Manager will mean sonarr/radarr can utilise Real Debrid
as a source for downloading new files. This allows you to benefit from the many
advantages that the Real Debrid service provides.

### Setup :

Simply add the "Torrent Blackhole" option as a download client and fill out the following:


![Settings](https://i.ibb.co/PZ4tStj/Sonnar-Settings.png)

* Name -  **"Real Debrid Manager"**
* Enable - **Yes**
* Torrent Folder - **This should be the watch folder**
* Watch Folder - **This is where ARIA2 saves downloaded files**
* Save Magnet Files - **Yes (This is supported)**
* Save Magnet Files - **".magnet"**
* Read Only - **User Preference**

Sonarr/Radarr will now save torrent information in the specified folder which Real Debrid Manager
will then pick up and action. 


## Application Guide 


Once the application is set up you will be taken to the main page.

This is where you can see the progress of all tasks sent to the application.

There are several UI elements to be aware of :

![WebUI](https://i.ibb.co/Gx7C8YK/webui.png)


* Delete Completed - **Removes all downloads from list which have been sent to Aria2.**
* Delete All - **Removes all downloads from list.** 
* Info - **Shows each stage that the application has processed for a particular task**
* Delete - **Deletes the particular task.** 

### End Notes

The application use itself should be fairly self-explanatory!

Feel free to open an issue or comment if you have a feature request or can optmize my code :-)

