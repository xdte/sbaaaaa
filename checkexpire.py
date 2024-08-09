import sqlite3
import time

def checkexpire():
    con = sqlite3.connect("main.db")
    cur = con.cursor()
    while True:
        cur.execute(f"DELETE FROM `session` WHERE `timestamp` + 5 < {time.time()}")
        con.commit()
        time.sleep(60)


