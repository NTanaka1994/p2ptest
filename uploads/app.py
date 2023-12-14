from flask import Flask, redirect, render_template, request
import requests
import html
import socket

port = 5012
app = Flask("__main__")

@app.route("/", methods=["GET"])
def route():
    return redirect("home")

@app.route("/home", methods=["GET"])
def home():
    host = socket.gethostname()
    ip = socket.gethostbyname(host)
    if request.args.get("err") is None:
        return render_template("home.html", ip=ip)
    elif request.args.get("err") == "openfile":
        return render_template("home.html", ip=ip, err="ファイルがありません")

@app.route("/upload", methods=["GET"])
def upload():
    path = request.args.get("path")
    address = request.args.get("address")
    url = "http://" + html.escape(address) + "/:" + str(port) + "/download"
    headers = {
        "Content-Type": "multipart/form-data",
    }
    params = {
        "id": 1,
    }
    try:
        target_file = open("uploads/"+path, "r")
    except:
        return redirect("../?err=openfile")
    files = {"file": (target_file.name, target_file.read())}
    response = requests.post(url=url, data=params, files=files, headers=headers)
    print(response.text)
    return redirect("home")

@app.route("/download", methods=["POST"])
def download():
    if "file" not in request.files:
        return "ファイルは送信されていません"
    file = request.files["file"]
    if file.filename == "":
        return "ファイル名が有りません"
    try:
        file.save("downloads/"+file.name)
        return "ファイルが保存されました"
    except:
        return "ファイルの保存に失敗しました"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=port)