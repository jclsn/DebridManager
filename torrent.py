import requests
import time
import os
import aria2p
import sqlite3

databaseinfo = os.getenv("dbinfo")
connection = sqlite3.connect(databaseinfo, timeout=20)
cursor = connection.cursor()
cursor.execute(
    "CREATE TABLE IF NOT EXISTS tasks (id TEXT, filename TEXT, debrid_status TEXT, debrid_dl_progress INTEGER, attemptstogetlink INTEGER, debrid_error TEXT , completed TEXT , Timestamp DATETIME DEFAULT CURRENT_TIMESTAMP )"
)

cursor.execute("SELECT * FROM settings where id=1")
result = cursor.fetchall()
waitbetween = result[0][1]
maxattempts = result[0][2]
aria2host = result[0][3]
secretkey = result[0][4]
realdebrid_apikey = result[0][5]


def moveprocessed(pathname, error):
    head, tail = os.path.split(pathname)
    if error == 0:
        newlocaton = head + "/processed/" + tail
        os.rename(pathname, newlocaton)
    else:
        newlocaton = head + "/errored/" + tail
        os.rename(pathname, newlocaton)


def realdebridtorrent(torrent):
    global completed
    addtorrenturl = (
        "https://api.real-debrid.com/rest/1.0/torrents/addTorrent?auth_token="
        + realdebrid_apikey
    )
    with open(torrent, "rb") as finput:
        response = requests.put(addtorrenturl, data=finput.read())
    debrid_response = response.json()
    myid = debrid_response["id"]
    head, tail = os.path.split(torrent)
    filename = tail
    debrid_status = "Submitted to RD"
    attemptstogetlink = 0
    debrid_error = " "
    completedtask = "No"
    cursor.execute(
        """INSERT INTO tasks(id, filename, debrid_status, attemptstogetlink, debrid_error,completed) VALUES (?,?,?,?,?,?)""",
        (myid, filename, debrid_status, attemptstogetlink, debrid_error, completedtask),
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
                """INSERT INTO tasks(id, filename, debrid_status, debrid_dl_progress, attemptstogetlink, debrid_error,completed) VALUES (?,?,?,?,?,?,?)""",
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
            moveprocessed(torrent, error)
        case "error":
            debrid_status = "General Error"
            cursor.execute(
                """INSERT INTO tasks(id, filename, debrid_status, debrid_dl_progress, attemptstogetlink, debrid_error,completed) VALUES (?,?,?,?,?,?,?)""",
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
            moveprocessed(torrent, error)
        case "magnet_conversion":
            debrid_status = "Stuck Magnet Conversion"
            cursor.execute(
                """INSERT INTO tasks(id, filename, debrid_status, debrid_dl_progress, attemptstogetlink, debrid_error,completed) VALUES (?,?,?,?,?,?,?)""",
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
            moveprocessed(torrent, error)
        case "virus":
            debrid_status = "File is Virus"
            cursor.execute(
                """INSERT INTO tasks(id, filename, debrid_status, debrid_dl_progress, attemptstogetlink, debrid_error,completed) VALUES (?,?,?,?,?,?,?)""",
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
            moveprocessed(torrent, error)
        case "dead":
            debrid_status = "Link is Dead"
            cursor.execute(
                """INSERT INTO tasks(id, filename, debrid_status, debrid_dl_progress, attemptstogetlink, debrid_error,completed) VALUES (?,?,?,?,?,?,?)""",
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
            moveprocessed(torrent, error)
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
            """INSERT INTO tasks(id, filename, debrid_status, debrid_dl_progress, attemptstogetlink, debrid_error,completed) VALUES (?,?,?,?,?,?,?)""",
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
            """INSERT INTO tasks(id, filename, debrid_status, attemptstogetlink, debrid_error,debrid_dl_progress,completed) VALUES (?,?,?,?,?,?,?)""",
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
        moveprocessed(torrent, error)
        time.sleep(1)
        debrid_status = "Sent to aria2"
        cursor.execute(
            """INSERT INTO tasks(id, filename, debrid_status, attemptstogetlink, debrid_error,debrid_dl_progress,completed) VALUES (?,?,?,?,?,?,?)""",
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
            """INSERT INTO tasks(id, filename, debrid_status, attemptstogetlink, debrid_error,debrid_dl_progress,completed) VALUES (?,?,?,?,?,?,?)""",
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
        moveprocessed(torrent, error)


import sys

torrent = sys.argv[1]
print("Starting Worker on Received Torrent")
realdebridtorrent(torrent)
