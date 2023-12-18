from flask import Flask, redirect, render_template, request, send_file
import pandas as pd
import requests
import socket
import os
import html
import glob

port = 5041
app = Flask("__main__")

@app.route("/", methods=["GET"])
def route():
    return redirect("home")

@app.route("/home", methods=["GET"])
def home():
    host = socket.gethostname()
    ip = socket.gethostbyname(host)
    df = pd.read_csv("node.csv")
    cols = df.columns
    val = df.values
    node = "<table border=\"1\">\n\t<tr>"
    for col in cols:
        node = node + "<th>" + html.escape(col) + "</th>"
    node = node + "</tr>\n"
    for i in range(len(val)):
        node = node + "\t<tr>"
        for j in range(len(val[i])):
            node = node + "<td>" + html.escape(str(val[i][j])) + "</td>"
        node = node + "<tr><td colspan=\"3\">"
        print("http://"+str(val[i][1])+":"+str(val[i][2])+"/files")
        response = requests.get("http://"+str(val[i][1])+":"+str(val[i][2])+"/files").text
        node = node + response
        node = node + "</td></tr>"
        node = node + "\n"
    err = ""
    result = ""
    if request.args.get("err") is not None:
        err = "ファイルがありません"
    if request.args.get("result") is not None:
        result = request.args.get("result")
    return render_template("home.html", ip=ip, err=err, result=result, node=node)

@app.route("/upload", methods=["GET"])
def upload():
    path = request.args.get("path")
    address = request.args.get("address")
    toport = request.args.get("toport")
    url = "http://" + address + ":" + str(toport) + "/download"
    try:
        files = {'file': open("uploads/"+path, "rb")}
    except:
        return redirect("home?err=openfile")
    response = requests.post(url=url, files=files, data={"filename":path})
    if response.status_code == 200:
        return redirect("home?result="+response.text)
    elif response.status_code == 404:
        return redirect("home?result=アドレスが間違っています")
    
@app.route("/download", methods=["POST"])
def download():
    if "file" not in request.files:
        return "ファイルは送信されていません"
    file = request.files["file"]
    if file.filename == "":
        return "ファイル名が有りません"
    try:
        file.save("downloads/"+os.path.basename(request.form["filename"]))
        return "ファイルが保存されました"
    except:
        return "ファイルの保存に失敗しました"

@app.route("/files", methods=["GET"])
def datas():
    host = socket.gethostname()
    ip = socket.gethostbyname(host)
    files = glob.glob("uploads/*")
    res = ""
    for file in files:
        res = res + "<a href=\"http://" + ip + ":" + str(port) + "/file?name=" + os.path.basename(file) + "\">" + os.path.basename(file) + "</a><br>\n"
    return res

@app.route("/file", methods=["GET"])
def data():
    name = request.args.get("name")
    return send_file("uploads/"+name)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=port)
