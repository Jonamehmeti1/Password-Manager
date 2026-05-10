# AES Password Manager GUI

Ky projekt është një aplikacion desktop për menaxhimin personal të fjalëkalimeve.

Aplikacioni përdor **Python + Tkinter** për interface grafik dhe **AES-256-GCM** për enkriptimin e të dhënave. Qëllimi i aplikacionit është që përdoruesi t’i ruajë fjalëkalimet e veta në mënyrë më të sigurt në një file të enkriptuar.

## Çka bën aplikacioni

Aplikacioni mundëson:

- Krijimin e një vault-i të enkriptuar
- Login me Master Password
- Ruajtjen e kredencialeve:
  - Website/App
  - Username/Email
  - Password
  - Category
- Shfaqjen e kredencialeve në tabelë
- Gjenerimin e fjalëkalimeve të forta
- Kërkimin e kredencialeve
- Filtrimin sipas kategorisë
- Përditësimin e kredencialeve ekzistuese
- Fshirjen e kredencialeve
- Export/Import të vault-it të enkriptuar për backup ose përdorim në pajisje tjetër

## Instalimi

Hape terminalin në folderin e projektit dhe instalo librarinë `cryptography`:

```bash
pip install cryptography
```

Nëse komanda `pip` nuk punon, provo:

```bash
python -m pip install cryptography
```

Në Windows, mund të provosh edhe:

```bash
py -m pip install cryptography
```

## Startimi i aplikacionit

Pasi të instalohet libraria `cryptography`, startoje aplikacionin me komandën:

```bash
python main.py
```

Në Windows, nëse komanda `python` nuk punon, provo:

```bash
py main.py
```

## Si funksionon aplikacioni

Kur hapet aplikacioni, shfaqet dritarja për Master Password.

Nëse aplikacioni hapet për herë të parë dhe nuk ekziston ende file-i `vault.enc`, përdoruesi shkruan një Master Password dhe klikon:

```text
Create New Vault
```

Kjo krijon një vault të ri të enkriptuar ku do të ruhen kredencialet.

Herëve të tjera, përdoruesi shkruan të njëjtin Master Password dhe klikon:

```text
Login
```

Nëse Master Password është i saktë, hapet dashboard-i kryesor i aplikacionit.

Në dashboard përdoruesi mund të shtojë kredenciale duke plotësuar fushat:

```text
Website/App
Username/Email
Password
Category
```

Pastaj klikon:

```text
Save New
```

Të dhënat ruhen në file-in:

```text
vault.enc
```

Ky file nuk i ruan passwordat si tekst të thjeshtë. Të dhënat ruhen të enkriptuara me **AES-256-GCM**.

Kur përdoruesi klikon një rresht në tabelë, të dhënat shfaqen në formë dhe mund të përditësohen ose të fshihen.

Butoni:

```text
Generate Strong Password
```

krijon automatikisht një fjalëkalim të fortë.

Butoni:

```text
Export Encrypted Vault
```

krijon një kopje të vault-it të enkriptuar për backup ose për bartje në pajisje tjetër.

Butoni:

```text
Import Encrypted Vault
```

e zëvendëson vault-in aktual me një vault tjetër të enkriptuar.

## Shënim sigurie

Master Password nuk ruhet direkt në file.

Ai përdoret për të krijuar çelësin kriptografik përmes **PBKDF2HMAC-SHA256**. Pastaj ky çelës përdoret për enkriptimin dhe dekriptimin e vault-it me **AES-256-GCM**.

Pa Master Password-in e saktë, të dhënat në `vault.enc` nuk mund të dekriptohen.
