#!/usr/bin/env python3

import os
import pathlib
import sqlite3 as sql
import subprocess

from flask import Flask, render_template, request, redirect
from flask import Flask, render_template
from flask_basicauth import BasicAuth

global myversion

databaseinfo = str(os.getenv("dbinfo"))
pathtowatch = str(os.getenv("watchpath"))
connection = sql.connect(":memory:")
connection.set_trace_callback(print)

# Start watching files in the background with pyinotify
watch_process = subprocess.Popen(['python', 'FileWatch.py'])

# Create a flask object
app = Flask(__name__)

# Check for stored credentials in the database
try:
    con = sql.connect(databaseinfo, timeout=20)
    con.row_factory = sql.Row
    cur = con.cursor()
    id = 1
    cur.execute("SELECT * FROM settings where id=?", (id,))
    rows = cur.fetchall()
    loginlist = [rows[0][7], rows[0][8]]

    app.config["BASIC_AUTH_USERNAME"] = loginlist[0]
    app.config["BASIC_AUTH_PASSWORD"] = loginlist[1]
except:
    app.config["BASIC_AUTH_USERNAME"] = "admin"
    app.config["BASIC_AUTH_PASSWORD"] = "admin"

# Trigger basic authentication dialog
basic_auth = BasicAuth(app)

# Define root URL function
@app.route("/")
@basic_auth.required
def list():

    connection = sql.connect(databaseinfo, timeout=20)
    connection.row_factory = sql.Row
    cursor = connection.cursor()
    cursor.execute(
        "select count(*) from sqlite_master where type='table' and name='settings'"
    )

    result = cursor.fetchall()
    result = result[0][0]


    if result == 0:
        pathlib.Path(pathtowatch + "processed").mkdir(mode=0o777, exist_ok=True)
        pathlib.Path(pathtowatch + "errored").mkdir(mode=0o777, exist_ok=True)

        return render_template("firstlogin.html")

    else:
        cursor.execute("DROP TABLE IF EXISTS webuiview")
        cursor.execute("select  * from tasks ORDER BY Timestamp DESC")
        rows = cursor.fetchall()
        knownid = []

        for row in rows:
            downloadid = row[0]

            if downloadid in knownid:
                pass
            else:
                knownid.append(downloadid)
                myid = row[0]
                name = row[1]
                name = name[:50]
                status = row[2]
                progress = row[3]
                attempts = row[4]
                debrid_error = row[5]
                completed = row[6]

                connection = sql.connect(databaseinfo, timeout=20)
                cursor = connection.cursor()
                cursor.execute(
                    """CREATE TABLE IF NOT EXISTS webuiview(
                        id TEXT,
                        filename TEXT,
                        debrid_status TEXT,
                        debrid_dl_progress INTEGER,
                        attemptstogetlink INTEGER,
                        debrid_error TEXT,
                        completed INTEGER ,
                        Timestamp DATETIME DEFAULT CURRENT_TIMESTAMP )"""
                )
                cursor.execute(
                    """INSERT INTO webuiview(
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
                        name,
                        status,
                        progress,
                        attempts,
                        debrid_error,
                        completed,
                    ),
                )
                connection.commit()

            cursor.execute("select  * from webuiview ORDER BY Timestamp DESC")
            rows = cursor.fetchall()
        return render_template(
            "main.html",
            newlist=rows,
        )

@app.route("/info/<id>")
@basic_auth.required
def lihat_profile(id):
    con = sql.connect(databaseinfo, timeout=20)
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute("SELECT * FROM tasks where id=?", (id,))
    rows = cur.fetchall()
    filename = rows[0][1]
    return render_template("info.html", name=filename, newlist=rows)


@app.route("/delete/<id>")
@basic_auth.required
def deleteit(id):
    con = sql.connect(databaseinfo, timeout=20)
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute("delete FROM tasks where id=?", (id,))
    con.commit()
    return redirect("/")


@app.route("/deleteall")
@basic_auth.required
def deleteall():
    con = sql.connect(databaseinfo, timeout=20)
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute("delete FROM tasks")
    con.commit()
    return redirect("/")


@app.route("/deletecompleted")
@basic_auth.required
def deletecompleted():
    con = sql.connect(databaseinfo, timeout=20)
    con.row_factory = sql.Row
    cur = con.cursor()
    debrid_status = "Sent to aria2"
    cur.execute("SELECT * FROM tasks where debrid_status=?", (debrid_status,))
    rows = cur.fetchall()
    todeleteid = []
    for row in rows:
        downloadid = row[0]
        if downloadid in todeleteid:
            pass
        else:
            todeleteid.append(downloadid)
    for i in todeleteid:
        cur.execute("delete FROM tasks where id=?", (i,))
    con.commit()
    return redirect("/")


# Define settings URL function
@app.route("/settings", methods=["GET", "POST"])
@basic_auth.required
def settings():
    if request.method == "GET":
        connection = sql.connect(databaseinfo, timeout=20)
        connection.row_factory = sql.Row
        cursor = connection.cursor()

        # Check if settings table exists in database
        cursor.execute(
            "select count(*) from sqlite_master where type='table' and name='settings'"
        )
        result = cursor.fetchall()
        table_exists = result[0][0]

        if not table_exists:
            cursor.execute(
                """CREATE TABLE IF NOT EXISTS settings (
                    id INTEGER,
                    waitbetween INTEGER,
                    maxattempts INTEGER,
                    aria2host TEXT,
                    aria2secret TEXT,
                    realdebrid_apikey TEXT,
                    alldebrid_apikey TEXT,
                    username TEXT,
                    password TEXT)"""
            )
            connection.commit()
            id = 1
            waitbetween = 300
            maxattempts = 10
            aria2host = "localhost"
            aria2secret = "aria2secret"
            alldebrid_apikey = "alldebrid_apikey"
            realdebrid_apikey = "realdebrid_apikey"
            username = "admin"
            password = "admin"
            cursor.execute(
                """INSERT INTO settings(
                    id,
                    waitbetween,
                    maxattempts,
                    aria2host,
                    aria2secret,
                    realdebrid_apikey,
                    alldebrid_apikey,
                    username,
                    password
                    ) VALUES (?,?,?,?,?,?,?,?,?)""",
                (
                    id,
                    waitbetween,
                    maxattempts,
                    aria2host,
                    aria2secret,
                    realdebrid_apikey,
                    alldebrid_apikey,
                    username,
                    password,
                ),
            )
            connection.commit()
            settings_list = [
                waitbetween,
                maxattempts,
                aria2host,
                aria2secret,
                realdebrid_apikey,
                alldebrid_apikey,
                username,
                password,
            ]
            return render_template("settings.html", list1=settings_list)
        else:
            connection = sql.connect(databaseinfo, timeout=20)
            connection.row_factory = sql.Row
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM settings where id=1")
            rows = cursor.fetchall()
            settings_list = [
                rows[0][1],
                rows[0][2],
                rows[0][3],
                rows[0][4],
                rows[0][5],
                rows[0][6],
                rows[0][7],
                rows[0][8],
            ]
            return render_template("settings.html", list1=settings_list)

    elif request.method == "POST":
        connection = sql.connect(databaseinfo)
        connection.row_factory = sql.Row
        cursor = connection.cursor()
        waitbetween = request.form["waitbetween"]
        maxattempts = request.form["maxattempts"]
        aria2host = request.form["aria2host"]
        aria2secret = request.form["aria2secret"]
        realdebrid_apikey = request.form["realdebrid_apikey"]
        alldebrid_apikey = request.form["alldebrid_apikey"]
        username = request.form["username"]
        password = request.form["password"]
        cursor.execute(
            """UPDATE settings SET
                waitbetween = ?,
                maxattempts=?,
                aria2host=?,
                aria2secret=?,
                realdebrid_apikey=?,
                alldebrid_apikey=?,
                username=?,
                password=?
                WHERE id = 1""",
            (
                waitbetween,
                maxattempts,
                aria2host,
                aria2secret,
                realdebrid_apikey,
                alldebrid_apikey,
                username,
                password,
            ),
        )
        connection.commit()
        settings_list = [
            waitbetween,
            maxattempts,
            aria2host,
            aria2secret,
            realdebrid_apikey,
            alldebrid_apikey,
            username,
            password,
        ]
        return render_template("settingssuccess.html", list1=settings_list)


if __name__ == "__main__":
    app.run(debug=True)
