import sqlite3
import time

def checkexpire():
    while True:
        con = sqlite3.connect("main.db")
        cur = con.cursor()
        cur.execute(f"DELETE FROM `session` WHERE `timestamp` + 259200 < {int(time.time())}")
        con.commit()
        con.close()
        time.sleep(60)


