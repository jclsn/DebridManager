import requests
import time
import os
import aria2p
import sqlite3
import random

databaseinfo = str(os.getenv("dbinfo"))
connection = sqlite3.connect(databaseinfo, timeout=20)
cursor = connection.cursor()
cursor.execute(
    """CREATE TABLE IF NOT EXISTS tasks (
        id TEXT,
        filename TEXT,
        debrid_status TEXT,
        debrid_dl_progress INTEGER,
        attemptstogetlink INTEGER,
        debrid_error TEXT ,
        completed TEXT ,
        Timestamp DATETIME DEFAULT CURRENT_TIMESTAMP )"""
)

cursor.execute("SELECT * FROM settings where id=1")
result = cursor.fetchall()
waitbetween = result[0][1]
maxattempts = result[0][2]
aria2host = result[0][3]
secretkey = result[0][4]
realdebrid_apikey = result[0][5]
alldebrid_apikey = result[0][6]


def moveprocessed(pathname, error):
    pathname = originalmagnet
    head, tail = os.path.split(pathname)
    if error == 0:
        newlocaton = head + "/processed/" + tail
        os.rename(pathname, newlocaton)
    else:
        newlocaton = head + "/errored/" + tail + ".MAGNET"
        os.rename(pathname, newlocaton)


def realdebridtorrent(magnet):
    global completed
    addmagneturl = (
        "https://api.real-debrid.com/rest/1.0/torrents/addMagnet?auth_token="
        + realdebrid_apikey
    )
    magnetaddjson = {"magnet": magnet}
    response = requests.post(addmagneturl, data=magnetaddjson)
    debrid_response = response.json()
    myid = debrid_response["id"]
    head, tail = os.path.split(magnet)
    filename = tail
    debrid_status = "Submitted to RealDebrid"
    attemptstogetlink = 0
    debrid_error = " "
    completedtask = "No"
    cursor.execute(
        """INSERT INTO tasks(
            id,
            filename,
            debrid_status,
            attemptstogetlink,
            debrid_error,
            completed)
            VALUES (?,?,?,?,?,?)""",
        (
            myid,
            filename,
            debrid_status,
            attemptstogetlink,
            debrid_error,
            completedtask
        ),
    )

    connection.commit()
    time.sleep(2)
    selectfiles = (
        "https://api.real-debrid.com/rest/1.0/torrents/selectFiles/"
        + myid
        + "?auth_token="
        + realdebrid_apikey
    )
    allfiles = {"files": "all"}
    response = requests.post(selectfiles, data=allfiles)

    selecttorrentinfo = (
        "https://api.real-debrid.com/rest/1.0/torrents/info/"
        + myid
        + "?auth_token="
        + realdebrid_apikey
    )
    response = requests.get(selecttorrentinfo)
    debrid_response = response.json()
    status = debrid_response["status"]

    match status:
        case "downloaded":
            completed = 1
        case "queued":
            completed = 0
        case "magnet_error":
            debrid_status = "Magnet Error"
            cursor.execute(
                """INSERT INTO tasks(
                    id,
                    filename,
                    debrid_status,
                    debrid_dl_progress,
                    attemptstogetlink,
                    debrid_error,
                    completed)
                    VALUES (?,?,?,?,?,?,?)""",
                (
                    myid,
                    filename,
                    debrid_status,
                    debrid_dl_progress,
                    attemptstogetlink,
                    debrid_error,
                    completedtask,
                ),
            )
            connection.commit()
            completed = 1
            global error
            error = 1
            moveprocessed(magnet, error)
        case "error":
            debrid_status = "General Error"
            cursor.execute(
                """INSERT INTO tasks(
                    id,
                    filename,
                    debrid_status,
                    debrid_dl_progress,
                    attemptstogetlink,
                    debrid_error,
                    completed)
                    VALUES (?,?,?,?,?,?,?)""",
                (
                    myid,
                    filename,
                    debrid_status,
                    debrid_dl_progress,
                    attemptstogetlink,
                    debrid_error,
                    completedtask,
                ),
            )
            connection.commit()
            completed = 1
            error = 1
            moveprocessed(magnet, error)
        case "magnet_conversion":
            debrid_status = "Stuck Magnet Conversion"
            cursor.execute(
                """INSERT INTO tasks(
                    id,
                    filename,
                    debrid_status,
                    debrid_dl_progress,
                    attemptstogetlink,
                    debrid_error,
                    completed)
                    VALUES (?,?,?,?,?,?,?)""",
                (
                    myid,
                    filename,
                    debrid_status,
                    debrid_dl_progress,
                    attemptstogetlink,
                    debrid_error,
                    completedtask,
                ),
            )
            connection.commit()
            completed = 1
            error = 1
            moveprocessed(magnet, error)
        case "virus":
            debrid_status = "File is Virus"
            cursor.execute(
                """INSERT INTO tasks(
                    id,
                    filename,
                    debrid_status,
                    debrid_dl_progress,
                    attemptstogetlink,
                    debrid_error,
                    completed)
                    VALUES (?,?,?,?,?,?,?)""",
                (
                    myid,
                    filename,
                    debrid_status,
                    debrid_dl_progress,
                    attemptstogetlink,
                    debrid_error,
                    completedtask,
                ),
            )
            connection.commit()
            completed = 1
            error = 1
            moveprocessed(magnet, error)
        case "dead":
            debrid_status = "Link is Dead"
            cursor.execute(
                """INSERT INTO tasks(
                    id,
                    filename,
                    debrid_status,
                    debrid_dl_progress,
                    attemptstogetlink,
                    debrid_error,
                    completed)
                    VALUES (?,?,?,?,?,?,?)""",
                (
                    myid,
                    filename,
                    debrid_status,
                    debrid_dl_progress,
                    attemptstogetlink,
                    debrid_error,
                    completedtask,
                ),
            )
            connection.commit()
            completed = 1
            error = 1
            moveprocessed(magnet, error)
        case _:
            completed = 0

    while completed == 0:
        selecttorrentinfo = (
            "https://api.real-debrid.com/rest/1.0/torrents/info/"
            + myid
            + "?auth_token="
            + realdebrid_apikey
        )
        response = requests.get(selecttorrentinfo)
        debrid_response = response.json()
        if debrid_response["status"] == "downloaded":
            completed = 1
        else:
            completed = 0
        debrid_status = "Downloading"
        attemptstogetlink = attemptstogetlink + 1
        debrid_dl_progress = debrid_response["progress"]
        completedtask = "No"
        debrid_error = "No error"
        cursor.execute(
            """INSERT INTO tasks(
                id,
                filename,
                debrid_status,
                debrid_dl_progress,
                attemptstogetlink,
                debrid_error,
                completed)
                VALUES (?,?,?,?,?,?,?)""",
            (
                myid,
                filename,
                debrid_status,
                debrid_dl_progress,
                attemptstogetlink,
                debrid_error,
                completedtask,
            ),
        )
        connection.commit()
        if attemptstogetlink >= maxattempts:
            completed = 2
        else:
            time.sleep(waitbetween)

    if completed == 1:
        debrid_status = "Downloaded to RD"
        attemptstogetlink = attemptstogetlink
        debrid_error = "none"
        completedtask = "Yes"
        debrid_dl_progress = 100
        cursor.execute(
            """INSERT INTO tasks(
                id,
                filename,
                debrid_status,
                attemptstogetlink,
                debrid_error,d
                ebrid_dl_progress,
                completed)
                VALUES (?,?,?,?,?,?,?)""",
            (
                myid,
                filename,
                debrid_status,
                attemptstogetlink,
                debrid_error,
                debrid_dl_progress,
                completedtask,
            ),
        )
        connection.commit()
        aria2 = aria2p.API(aria2p.Client(host=aria2host, port=6800, secret=secretkey))
        error = 0
        links = debrid_response["links"]
        for i in range(len(links)):
            getdownloadlinkurl = (
                "https://api.real-debrid.com/rest/1.0/unrestrict/link?auth_token="
                + realdebrid_apikey
            )
            filetoselect = {"link": links[i]}
            response = requests.post(getdownloadlinkurl, data=filetoselect)
            debrid_response = response.json()
            mylink = debrid_response["download"]
            try:
                download = aria2.add(mylink)
            except:
                print("Error Connecting To Your ARIA2 Instance")
        moveprocessed(magnet, error)
        time.sleep(1)
        debrid_status = "Sent to aria2"
        cursor.execute(
            """INSERT INTO tasks(
                id,
                filename,
                debrid_status,
                attemptstogetlink,
                debrid_error,d
                ebrid_dl_progress,
                completed)
                VALUES (?,?,?,?,?,?,?)""",
            (
                myid,
                filename,
                debrid_status,
                attemptstogetlink,
                debrid_error,
                debrid_dl_progress,
                completedtask,
            ),
        )
        connection.commit()

    elif completed == 2:
        time.sleep(1)
        deletetorrentfromdebrid = (
            "https://api.real-debrid.com/rest/1.0/torrents/delete/"
            + myid
            + "?auth_token="
            + realdebrid_apikey
        )
        response = requests.delete(deletetorrentfromdebrid)
        error = 1
        debrid_status = "Max Timeout Reached"
        attemptstogetlink = attemptstogetlink
        debrid_error = "Max Time"
        completedtask = "No"
        cursor.execute(
            """INSERT INTO tasks(
                id,
                filename,
                debrid_status,
                attemptstogetlink,
                debrid_error,d
                ebrid_dl_progress,
                completed)
                VALUES (?,?,?,?,?,?,?)""",
            (
                myid,
                filename,
                debrid_status,
                attemptstogetlink,
                debrid_error,
                debrid_dl_progress,
                completedtask,
            ),
        )
        connection.commit()
        moveprocessed(magnet, error)


def alldebridtorrent(magnet):

    global completed
    global error

    # Defaults
    debrid_error = " "
    completedtask = "No"
    attemptstogetlink = 0
    error_response = False
    attempt_limit_reached = False

    # Send magnet link to AllDebrid
    try:
        response = requests.post(
            "https://api.alldebrid.com/v4/magnet/upload?agent=Debridmanager&apikey="
            + alldebrid_apikey,
            data={"magnet": magnet},
        ).json()
    except:
        print("Couldn't communicate with AllDebrid")
        return

    myid = response["id"]
    head, tail = os.path.split(magnet)
    filename = tail
    debrid_status = "Submitted to AllDebrid"

    try:
        cursor.execute(
            """INSERT INTO tasks(
                id,
                filename,
                debrid_status,
                attemptstogetlink,
                debrid_error,
                completed)
                VALUES (?,?,?,?,?,?)""",
            (
                myid,
                filename,
                debrid_status,
                attemptstogetlink,
                debrid_error,
                completedtask,
            ),
        )
        connection.commit()
    except:
        print("Couldn't update database")
        return

    time.sleep(2)

    # Query download status from AllDebrid
    try:
        response = requests.get(
            "https://api.alldebrid.com/v4/magnet/status?agent=Debridmanager&apikey="
            + alldebrid_apikey,
            data={"id": myid},
        ).json()
    except:
        print("Couldn't communicate with AllDebrid")
        return

    match response["statusCode"]:
        case 0:  # In queue
            completed = False
        case 4:  # Ready
            completed = True
        case 5:
            debrid_status = "Upload failure"
            error_response = True
        case 6:
            debrid_status = "Internal error while unpacking"
            error_response = True
        case 7:
            debrid_status = "Not downloaded in 20 min"
            error_response = True
        case 8:
            debrid_status = "File too big"
            error_response = True
        case 9:
            debrid_status = "Internal error"
            error_response = True
        case 10:
            debrid_status = "Download took more than 72h"
            error_response = True
        case 11:
            debrid_status = "Deleted on the hoster website"
            error_response = True
        case _:
            completed = False

    if error_response:  # Update database in case of an error
        try:
            cursor.execute(
                """INSERT INTO tasks(
                    id,
                    filename,
                    debrid_status,
                    debrid_dl_progress,
                    attemptstogetlink,
                    debrid_error,
                    completed)
                    VALUES (?,?,?,?,?,?,?)""",
                (
                    myid,
                    filename,
                    debrid_status,
                    debrid_dl_progress,
                    attemptstogetlink,
                    debrid_error,
                    completedtask,
                ),
            )
            connection.commit()
            completed = True
            error = 1
            moveprocessed(magnet, error)
            return
        except:
            print("Couldn't update database")
            return

    """
    If the download is not instantly available, monitor the download status
    using the AllDebrid LiveMode

    https://docs.alldebrid.com/?shell#status-live-mode
    """
    session_id = random.randint(0, 1000)

    while not completed or not attempt_limit_reached:
        try:
            response = requests.get(
                "https://api.alldebrid.com/v4/magnet/status?agent=Debridmanager&apikey="
                + alldebrid_apikey
                + "&session="
                + session_id
                + "&counter="
                + attemptstogetlink,
                data={"id": myid},
            ).json()
        except:
            print("Couldn't communicate with AllDebrid")
            return

        debrid_status = "Downloading"
        attemptstogetlink += 1
        debrid_dl_progress = int(response["downloaded"] / response["size"] * 100)
        completedtask = "No"
        debrid_error = "No error"

        try:
            cursor.execute(
                """INSERT INTO tasks(
                    id,
                    filename,
                    debrid_status,
                    debrid_dl_progress,
                    attemptstogetlink,
                    debrid_error,
                    completed)
                    VALUES (?,?,?,?,?,?,?)""",
                (
                    myid,
                    filename,
                    debrid_status,
                    debrid_dl_progress,
                    attemptstogetlink,
                    debrid_error,
                    completedtask,
                ),
            )
            connection.commit()
        except:
            print("Couldn't update database")
            return

        if attemptstogetlink >= maxattempts:
            attempt_limit_reached = True
        else:
            time.sleep(waitbetween)

        if response["statusCode"] == 4:  # Ready
            completed = True

    if completed:
        debrid_status = "Downloaded to AllDebrid"
        debrid_error = "none"
        completedtask = "Yes"
        debrid_dl_progress = 100

        try:
            cursor.execute(
                """INSERT INTO tasks(
                    id,
                    filename,
                    debrid_status,
                    attemptstogetlink,
                    debrid_error,
                    debrid_dl_progress,
                    completed)
                    VALUES (?,?,?,?,?,?,?)""",
                (
                    myid,
                    filename,
                    debrid_status,
                    attemptstogetlink,
                    debrid_error,
                    debrid_dl_progress,
                    completedtask,
                ),
            )
            connection.commit()
        except:
            print("Couldn't update database")
            return

        aria2 = aria2p.API(aria2p.Client(host=aria2host, port=6800, secret=secretkey))
        error = 0

        for link in response["links"]:
            try:
                response = requests.post(
                    "https://api.alldebrid.com/v4/link/unlock?agent=Debridmanager&apikey="
                    + alldebrid_apikey,
                    data={"link": link},
                ).json()
            except:
                print("Couldn't communicate with AllDebrid")
                return

            try:
                aria2.add(response["link"])
            except:
                print("Error Connecting To Your ARIA2 Instance")

        moveprocessed(magnet, error)
        time.sleep(1)
        debrid_status = "Sent to aria2"
        cursor.execute(
            """INSERT INTO tasks(
                id,
                filename,
                debrid_status,
                attemptstogetlink,
                debrid_error,
                debrid_dl_progress,
                completed)
                VALUES (?,?,?,?,?,?,?)""",
            (
                myid,
                filename,
                debrid_status,
                attemptstogetlink,
                debrid_error,
                debrid_dl_progress,
                completedtask,
            ),
        )
        connection.commit()

    if attempt_limit_reached:
        time.sleep(1)

        # Delete magnet from AllDebrid
        try:
            response = requests.delete(
                "https://api.alldebrid.com/v4/link/delete?agent=Debridmanager&apikey="
                + alldebrid_apikey,
                data={"id": myid},
            ).json()
        except:
            print("Couldn't communicate with AllDebrid")
            return

        error = 1
        debrid_status = "Max Timeout Reached"
        debrid_error = "Max Time"
        completedtask = "No"

        try:
            cursor.execute(
                """INSERT INTO tasks(
                    id,
                    filename,
                    debrid_status,
                    attemptstogetlink,
                    debrid_error,
                    debrid_dl_progress,
                    completed)
                    VALUES (?,?,?,?,?,?,?)""",
                (
                    myid,
                    filename,
                    debrid_status,
                    attemptstogetlink,
                    debrid_error,
                    debrid_dl_progress,
                    completedtask,
                ),
            )
            connection.commit()
        except:
            print("Couldn't update database")
            return

        moveprocessed(magnet, error)


import sys

originalmagnet = sys.argv[1]
print("Starting script on received magnet link")
with open(originalmagnet, "r") as f:
    magnetlink = f.readlines()
magnetlink = magnetlink[0]

if realdebrid_apikey:
    realdebridtorrent(magnetlink)
elif alldebrid_apikey:
    alldebridtorrent(magnetlink)

