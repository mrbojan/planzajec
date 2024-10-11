#!/bin/env python3

from http.server import BaseHTTPRequestHandler, HTTPServer
import time
from plan_zajec.tabela import dajTabele, dajTabele78, dajStyle, dajCzysteKlucze, dajRaporty
import urllib
import sys
import threading
import re
from zipfile import ZipFile


#plikZPlanem = "planzajec.txt"

def dajPlik(pl):
    return open(pl).read()

def dajHtmlKon():
    return '<div style="height:10%; padding:10%;">&nbsp;</div><div style="height:10%;">&nbsp;</div></body></html>\n'

def zrobKodHtmlZLinkami(linki):
    linie = ["<p>"]
    linie.extend([f'<a href="{link}">{nazwa}</a> &nbsp;' for (link,nazwa) in linki])
    linie.append("</p>")
    return "\n".join(linie)

def dajLinkiDlaNauczycieli():
    nauczyciele = dajCzysteKlucze(plikZPlanem, "kto")
    return [(f'/tabela____kto___{n}___dzien.html', n) for n in nauczyciele]

def dajLinkiDlaUczniow():
    grupy = dajCzysteKlucze(plikZPlanem, "grupy")
    return [(f'/tabela____grupy___{g}___dzien.html', g) for g in grupy]

def dajCheckboxyDlaUczniow():
    grupy = dajCzysteKlucze(plikZPlanem, "grupy")
    def dajCheckbox(ident):
        klasa = "linku"
        return f'<input type="checkbox" class="{klasa}" id="i{ident}" onchange="zrobLink();">{ident} &nbsp;\n'
    return "".join([dajCheckbox(ident) for ident in grupy])

def dajLinkiDlaPrzedmiotow():
    przedmioty = dajCzysteKlucze(plikZPlanem, "nazwa")
    return [(f'/tabela____nazwa___{n}___dzien.html', n) for n in przedmioty]

def dajLinkiDlaMiejsc():
    miejsca = dajCzysteKlucze(plikZPlanem, "miejsca")
    return [(f'/tabela____miejsca___{n}___dzien.html', n) for n in miejsca]
        
def dajNaglowek(klucz, wartosc):
    if klucz == "dzien":
        wartosc = {"pn":"poniedziałek", "wt":"wtorek", "śr":"środa", "cz":"czwartek", "pt":"piątek"}[wartosc]
    return "<h1>" + klucz + " = " + wartosc + "</h1>"

def dajNaglowekX(kluczX, wartosci):
    if kluczX == "dzien":
        slownik = {"pn":"poniedziałek", "wt":"wtorek", "śr":"środa", "cz":"czwartek", "pt":"piątek"}
        wartosci = [slownik[w] for w in wartosci]
    return "<h1>" + kluczX + " = " + ", ".join(wartosci) + "</h1>"

def getResponseFor(co, plik):
    global plikZPlanem
    plikZPlanem = plik
    print("***", co)
    print("to jest to", co)
    headerHtml = "text/html; charset=utf-8"
    if co == "/index.html" or co == "/" or co == "":
        html =  open("plan_zajec/ind.html").read()
        return (headerHtml,
                html.replace("NNN", zrobKodHtmlZLinkami(dajLinkiDlaNauczycieli())).replace("UUU", zrobKodHtmlZLinkami(dajLinkiDlaUczniow())).replace("PPP", zrobKodHtmlZLinkami(dajLinkiDlaPrzedmiotow())).replace("MMM", zrobKodHtmlZLinkami(dajLinkiDlaMiejsc())).replace("PLIKZRODLOWY", plikZPlanem).replace("CHECKBOXYUCZNIOW", dajCheckboxyDlaUczniow()))
    elif co.startswith("/tabela"):
        jaka = co[len("/tabela____"):]
        jaka = jaka[:jaka.index(".")]
        klucz, wartosc, kluczX = jaka.split("___")
        klucz = urllib.parse.unquote(klucz)
        wartosc = urllib.parse.unquote(wartosc)
        kluczX = urllib.parse.unquote(kluczX)

        if klucz == "dzien" and wartosc == "sr":
            wartosc = "śr"
        # return dajPlik("htmlhead.html") +  dajStyle(plikZPlanem) + dajPlik("htmlpocz.html") + dajTabele(plikZPlanem) + dajOknoDialogowe() + dajHtmlKon()
        html = open("plan_zajec/planwzor.html").read()
        return (headerHtml,
                html.replace("STYL", dajStyle(plikZPlanem)).replace("BODY", dajNaglowek(klucz,wartosc) + dajTabele(plikZPlanem, klucz, wartosc, kluczX)))
    elif co.startswith("/78tabela"):
        jaka = co[len("/78tabela____"):]
        jaka = jaka[:jaka.index(".")]
        try:
            klucz, kluczX, wartosci = jaka.split("___", 2)
        except:
            return (headerHtml,
                    "puste wartosci albo inny blad?")
        wartosci = wartosci.split("___")

        klucz = urllib.parse.unquote(klucz)
        kluczX = urllib.parse.unquote(kluczX)
        wartosci = [urllib.parse.unquote(w) for w in wartosci]

        if kluczX == "dzien":
            zamien = lambda x: "śr" if x == "sr" else x
            wartosci = [zamien(w) for w in wartosci]

        html = open("plan_zajec/planwzor.html").read()
        return (headerHtml,
                html.replace("STYL", dajStyle(plikZPlanem)).replace("BODY", dajNaglowekX(kluczX, wartosci) + dajTabele78(plikZPlanem, klucz, kluczX, wartosci)))
    elif co.startswith("/raport"):
        html = open("plan_zajec/planwzor.html").read()
        return (headerHtml,
                html.replace("STYL", "").replace("BODY", dajRaporty(plikZPlanem)))
    elif co.startswith("/plan_zajec.zip"):
        nazwa = zrobZipa()
        return ("application/zip", open(nazwa, "rb").read())
    return (headerHtml, "Ups...")

class MyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        header, html = getResponseFor(self.path)
        self.send_header("Content-type", header)
        self.end_headers()
#        self.wfile.write(bytes("<html><head><title>Title goes here.</title></head>", "utf-8"))
#        self.wfile.write(bytes("<body><p>This is a test.</p>", "utf-8"))
#        self.wfile.write(bytes("<p>You accessed path: %s</p>" % self.path, "utf-8"))
#        self.wfile.write(bytes("</body></html>", "utf-8"))
        #zrobZipa()
        if header.startswith("text"):
            self.wfile.write(bytes(html, "utf-8"))
        else:
            self.wfile.write(bytes(html))

def dajLinki(html):
    return re.findall('href="(.*.html)"', html)

def dajWszystkieLinkiNaGlownejStronie():
    linki = dajLinki(open("plan_zajec/ind.html").read())
    for funkcja in [dajLinkiDlaNauczycieli, dajLinkiDlaUczniow, dajLinkiDlaPrzedmiotow, dajLinkiDlaMiejsc]:
        linkiZNazwami = funkcja()
        linki.extend([link for (link, nazwa) in linkiZNazwami])
    return linki

def poprawLinkiUsuwajacSlasha(html):
    return html.replace('a href="/', 'a href="')

def zrobZipa():
    linki = ["/index.html"]
    linki.extend(dajWszystkieLinkiNaGlownejStronie())
    nazwa = "static/plan_zajec.zip"
    with ZipFile(nazwa, "w") as zip_file:
        for link in linki:
            if ".zip" in link:
                continue
            try:
                _, zawartosc = getResponseFor(link, plikZPlanem)
                zawartosc = poprawLinkiUsuwajacSlasha(zawartosc)
                linkBezSlasha = link[1:]
                zip_file.writestr(linkBezSlasha, zawartosc)
            except:
                pass
    return nazwa

