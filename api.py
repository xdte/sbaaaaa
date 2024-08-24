import random
import datetime, time
from flask import *
import sqlite3
import hashlib
from flask_cors import CORS, cross_origin
app = Flask(__name__)
cors = CORS(app, origins='*')
import threading
from sendemail import mail
from checkexpire import checkexpire

app.config['CORS_HEADERS'] = 'Content-Type'


def validate_sid(sid):
    con = sqlite3.connect("main.db")
    cur = con.cursor()
    result = cur.execute("SELECT EXISTS (SELECT 1 FROM `session` WHERE `sid` = ?)", (sid, )).fetchall()
    con.close()
    return True if 1 in result[0] else False





def getuid(sid):
    con = sqlite3.connect("main.db")
    cur = con.cursor()
    result = cur.execute("SELECT uid FROM session WHERE sid = ?", (sid, )).fetchone()
    con.close()
    return result[0]





@app.route('/register/', methods=['GET'])
@cross_origin()
def register():
    try:
        uname = request.args.get("username")
        pw = request.args.get("password")
        email = request.args.get("email")
        code = request.args.get("code")
        con = sqlite3.connect("main.db")
        cur = con.cursor()
        check = cur.execute("SELECT EXISTS (SELECT 1 FROM `verify` WHERE `email` = ? AND `code` = ?)", (email, code, )).fetchone()
        if 1 in check:
            timestamp = cur.execute("SELECT `timestamp` FROM `verify` WHERE `code` = ?", (code, )).fetchone()[0]
            if timestamp + (60*15) > int(time.time()):
                cur.execute("INSERT INTO `user` (`username`, `password`, `email`) VALUES (?, ?, ?)", (uname, pw, email, ))
                con.commit()
                con.close()
                return jsonify({"message": "success"}), 200
            else:
                return jsonify({"message": "Code expired"}), 401
        else:
            return jsonify({"message": "Code invalid"}), 200
        
    except sqlite3.Error as e:
        print(e)
        con.rollback()
        return jsonify({"message": f"Error: {e}"}), 500





@app.route('/login/', methods=['GET'])
@cross_origin()
def login():
    try:
        con = sqlite3.connect("main.db")
        cur = con.cursor()
        uname = request.args.get("username")
        pw = request.args.get("password")
        print(request.args)
        
        result = cur.execute("SELECT EXISTS (SELECT 1 FROM `user` WHERE `username` = ? AND `password` = ?)", (uname, pw,)).fetchall()
        print(result)
        if 1 in result[0]:
            uid = cur.execute("SELECT `id` FROM `user` WHERE `username` = ?", (uname,)).fetchall()[0][0]
            print(uid)
            curtime = int(time.time())
            t = str(uid)+str(curtime)
            sid = hashlib.sha256(t.encode("utf-8")).hexdigest()
            cur.execute("INSERT INTO `session` (`sid`, `uid`, `timestamp`) VALUES (?, (SELECT `id` FROM `user` WHERE `username` = ?), ?)", (sid, uname, curtime,))
            con.commit()
            return jsonify({"message": "success", "sid": sid}), 200
        else:
            return jsonify({"message": "User does not exist"}), 404
        
    except sqlite3.Error as e:
        print(e)
        return jsonify({"message": f"Error: {e}"}), 500



@app.route('/userget/', methods=['GET'])
@cross_origin()
def userget():
    print("userget request received")
    try:
        sid = request.args.get("sid")
        if validate_sid(sid):
            con = sqlite3.connect("main.db")
            cur = con.cursor()
            result = cur.execute("SELECT `username`, `email` FROM `user` WHERE `id` = ?", (getuid(sid),)).fetchone()
            return jsonify({"message": "success", "user": result}), 200
        else:
            return jsonify({"message": "sessionid not found"}), 401 
    except sqlite3.Error as e:
        print(e)
        return jsonify({"message": f"Error: {e}"}), 500





@app.route('/manage/', methods=['GET'])
@cross_origin()
def manage():
    print("manage request received")
    try:
        sid = request.args.get("sid")
        action = request.args.get("action")
        if validate_sid(sid):
            con = sqlite3.connect("main.db")
            cur = con.cursor()
            arg = request.args.get("arg")
            if action == "password":
                cur.execute(f"UPDATE `user` SET `password` = {arg} WHERE `uid` = {getuid(sid)}")
                return jsonify({"message": "success"}), 200     
            elif action == "username":
                if 1 not in cur.execute(f"SELECT EXISTS (SELECT 1 FROM `user` WHERE `username` = '{arg}')").fetchone():
                    cur.execute(f"UPDATE `user` SET `username` = {arg} WHERE `uid` = {getuid(sid)}")
                    return jsonify({"message": "success"}), 200
                else:
                    return jsonify({"message": "Username already exists"}), 501
            elif action == "email":
                if 1 not in cur.execute(f"SELECT EXISTS (SELECT 1 FROM `user` WHERE `email` = '{arg}')").fetchone():
                    cur.execute(f"UPDATE `user` SET `email` = {arg} WHERE `uid` = {getuid(sid)}")
                    return jsonify({"message": "success"}), 200
                else:
                    return jsonify({"message": "Email already exists"}), 501
        else:
            return jsonify({"message": "sessionid not found"}), 401
    except sqlite3.Error as e:
        print(e)
        con.rollback()
        con.close()
        return jsonify({"message": f"Error: {e}"}), 500




@app.route('/logout/', methods=['GET'])
@cross_origin()
def logout():
    print("logout request received")
    try:
        sid = request.args.get("sid")
        if validate_sid(sid):
            con = sqlite3.connect("main.db")
            cur = con.cursor()
            cur.execute("DELETE FROM `session` WHERE `sid` = ?", (sid,))
            con.commit()
            con.close()
            return jsonify({"message": "success"}), 200
        else:
            return jsonify({"message": "sessionid not found"}), 401
        
    except sqlite3.Error as e:
        print(e)
        return jsonify({"message": f"Error: {e}"}), 500





@app.route('/reset/', methods=['GET'])
@cross_origin()
def reset():
    print("reset request received")
    try:
        con = sqlite3.connect("main.db")
        cur = con.cursor()
        email = request.args.get("email")
        code = request.args.get("code")
        password = request.args.get("password")
        check1 = cur.execute("SELECT EXISTS (SELECT 1 FROM `user` WHERE `email` = ?)", (email,)).fetchone()
        if 1 in check1:
            print("check1 pass")
            check2 = cur.execute("SELECT EXISTS (SELECT 1 FROM `verify` WHERE `email` = ? AND `code` = ?)", (email, code,)).fetchone()
            if 1 in check2:
                print("check2 pass")
                timestamp = cur.execute(f"SELECT `timestamp` FROM `verify` WHERE `code` = ?", (code,)).fetchone()[0]
                if timestamp + (60*15) > int(time.time()):    
                    cur.execute("UPDATE `user` SET `password` = ? WHERE `email` = ?", (password, email,))
                    cur.execute("DELETE FROM `verify` WHERE `code` = ?", (code,))
                    con.commit()
                    con.close()
                    return jsonify({"message": "success"}), 200
                else:
                    con.close()
                    return jsonify({"message": "Code has expired"}), 401
            else: 
                con.close()
                return jsonify({"message": "Code is invalid"}), 401
        else:
            con.close()
            return jsonify({"message": "User not found"}), 404
    except sqlite3.Error as e:
        print(e)
        return jsonify({"message": f"Error: {e}"}), 500
    



@app.route('/code/', methods=['GET'])
@cross_origin()
def code():
    print("gencode request received")
    email = request.args.get("email")
    try:
        if email != None:
            con = sqlite3.connect("main.db")
            cur = con.cursor()
            code = random.randint(100000, 999999)
            timestamp = int(time.time())
            cur.execute("DELETE FROM `verify` WHERE `email` = ?", (email,))
            con.commit()
            cur.execute("INSERT INTO `verify` (`email`, `code`, `timestamp`) VALUES (?, ?, ?)", (email, code, timestamp,))
            con.commit()
            con.close()            
            mail(email, str(code))
            return jsonify({"message": "success"}), 200
        else:
            return jsonify({"message": "Invalid email"}), 0
    except sqlite3.Error as e:
        print(e)
        return jsonify({"message": f"Error: {e}"}), 500




@app.route('/get/', methods=['GET'])
@cross_origin()
def gettask():
    print("get task request received")
    try:
        sid = request.args.get("sid")
        if validate_sid(sid):
            con = sqlite3.connect("main.db")
            cur = con.cursor()
            uncompleted = request.args.get("uncompleted")
            completed = request.args.get("completed")
            if uncompleted == "1":
                result = cur.execute("SELECT id, title, description, category, due, completed FROM `tasks` WHERE `uid` = ? AND `completed` = 0 ORDER BY `due`", (getuid(sid), )).fetchall()
            elif completed == "1":
                result = cur.execute("SELECT id, title, description, category, due, completed FROM `tasks` WHERE `uid` = ? AND `completed` = 1 ORDER BY `due`", (getuid(sid), )).fetchall()
            else:
                result = cur.execute("SELECT id, title, description, category, due, completed FROM `tasks` WHERE `uid` = ? ORDER BY `completed` ASC, `due` ASC", (getuid(sid), )).fetchall()
            cur.execute("UPDATE `session` SET `lastused` = ? WHERE `uid` = ?", (int(time.time()), getuid(sid), )).fetchall()
            con.commit()
            return jsonify({"message": "success", "tasks": result}), 200
        else:
            return jsonify({"message": "sessionid invalid"}), 401
        
    except sqlite3.Error as e:
        print(e)
        return jsonify({"message": f"Error: {e}"}), 500





@app.route('/add/', methods=['GET'])
@cross_origin()
def addtask():
    print("add task request received")
    try:
        title = request.args.get("title")   
        print(title)
        desc = request.args.get("desc")
        category = request.args.get("category")
        due  = request.args.get("due")
        sid = request.args.get("sid")
        if validate_sid(sid):
            if int(time.time()) < int(due)+(3600*8):
                con = sqlite3.connect("main.db")
                cur = con.cursor()
                cur.execute("INSERT INTO `tasks` (`title`, `description`, `category`, `due`, `uid`) VALUES (?, ?, ?, ?, ?)", (title, desc, category, due, getuid(sid), ))
                cur.execute("UPDATE `session` SET `lastused` = ? WHERE `uid` = ?", (int(time.time()), getuid(sid), )).fetchall()
                con.commit()
                return jsonify({"message": "success"}), 200
            else:
                return jsonify({"message": "due invalid"}), 500
                
        else:
            return jsonify({"message": "sessionid invalid"}), 401
        
    except sqlite3.Error as e:
        print(e)
        con.rollback()
        con.close()
        return jsonify({"message": f"Error: {e}"}), 500





@app.route('/edit/', methods=['GET'])
@cross_origin()
def edittask():
    print("edit task request received")
    try:
        setcomplete = request.args.get("setcomplete")
        sid = request.args.get("sid")
        taskid = request.args.get("id")
        if validate_sid(sid):
            con = sqlite3.connect("main.db")
            cur = con.cursor()
            if setcomplete == "1":
                if cur.execute("SELECT `uid` FROM `tasks` WHERE `id` = ?", (taskid, )).fetchall()[0][0] == getuid(sid):
                    cur.execute("UPDATE `tasks` SET `completed` = 1 WHERE `id` = ?", (taskid, ))
            else:
                if cur.execute("SELECT `uid` FROM `tasks` WHERE `id` = ?", (taskid, )).fetchall()[0][0] == getuid(sid):
                    title = request.args.get("title")
                    desc = request.args.get("desc")
                    category = request.args.get("category")
                    due  = request.args.get("due")
                    if int(time.time()) < int(due)+(3600*8):
                        cur.execute("UPDATE `tasks` SET `title` = ?, `description` = ?, `category` = ?, `due` = ? WHERE `id` = ? AND `uid` = ?", (title, desc, category, due, taskid, getuid(sid), ))
                    else:
                        return jsonify({"message": "due invalid"}), 500
            con.commit()
            con.close()
            return jsonify({"message": "success"}), 200      
        else:
            return jsonify({"message": "sessionid invalid"}), 401
        
    except sqlite3.Error as e:
        print(e)
        con.rollback()
        con.close()
        return jsonify({"message": f"Error: {e}"}), 500





@app.route('/delete/', methods=['GET'])
@cross_origin()
def deletetask():
    print("delete task request received")
    try:
        sid = request.args.get("sid")
        taskid = request.args.get("id")
        completed = request.args.get("completed")
        if validate_sid(sid):
            con = sqlite3.connect("main.db")
            cur = con.cursor()
            if completed == "1":
                cur.execute("DELETE FROM `tasks` WHERE `uid` = ? AND `completed` = 1", (getuid(sid), ))
                con.commit()
                con.close()
                return jsonify({"message": "success"}), 200
                
            else:
                if cur.execute("SELECT `uid` FROM `tasks` WHERE `id` = ?", (taskid, )).fetchall()[0][0] == getuid(sid):
                    cur.execute("DELETE FROM `tasks` WHERE `id` = ?", (taskid, ))
                    con.commit()
                    con.close()
                    return jsonify({"message": "success"}), 200
                else:
                    return jsonify({"message": "taskid error"}), 401
        else:
            return jsonify({"message": "sessionid invalid"}), 401
    except sqlite3.Error as e:
        print(e)
        con.rollback()
        con.close()
        return jsonify({"message": f"Error: {e}"}), 500
    except TypeError:
        return jsonify({"message": "success, no task to delete"}), 200

@app.route('/test/', methods=['POST', 'GET'])
@cross_origin()
def test():
    print(request.get_json())
    print(request.get_json())
    return "hi"
    


threading.Thread(target=checkexpire).start()
app.run(port=5050, host="0.0.0.0", debug=True)


