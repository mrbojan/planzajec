#!/bin/env python3

from plan_zajec.intervals import *
import numpy as np
import sys
import pytest

def wyczyscString(s):
    dozwolone = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz_ĄĘĆŁŃÓŚŻŹąćęłńóśźż0123456789"
    wyczyszczony = "".join([c if c in dozwolone else "" for c in s])
    if wyczyszczony != "":
        return wyczyszczony
    return ""

class Zajecia:
    ileSrednikow = [5, 6]

    def __init__(self, s):
        self.readFromStr(s)

    @staticmethod
    def czytelnaGodz2int(s):
        wart = int(s)
        return 60*(wart // 100) + (wart % 100)

    @staticmethod
    def int2czytelnaGodz(i):
        czytelna = (i//60)*100 + (i%60)
        return str(czytelna)

    @staticmethod
    def int2ladnaGodz(i):
        return f"{i//60}:{i%60:02}"
    
    def rozdziel(self, co):
        if co == "":
            return []
        return co.split(",")
    
    def readFromStr(self, s):
        try:
            dz, godz1, godz2, gr, zaj, naucz, miejsca = s.split(';')
        except ValueError:
            dz, godz1, godz2, gr, zaj, naucz = s.split(';')
            miejsca = "(gdzieś)"
        self.dzien = dz  #["pn", "wt", "śr", "cz", "pt"].index(dz)
        self.godz1 = self.czytelnaGodz2int(godz1)
        self.godz2 = self.czytelnaGodz2int(godz2)
        self.nazwa = self.rozdziel(zaj)
        self.kto = self.rozdziel(naucz)
        self.grupy = self.rozdziel(gr)
        self.miejsca = self.rozdziel(miejsca)

    @staticmethod
    def getSortingDict(s):
        s = s[1:]
        try:
            dz, godz1, godz2, gr, zaj, naucz, miejsca = s.split(';')
        except ValueError:
            dz, godz1, godz2, gr, zaj, naucz = s.split(';')
            miejsca = ""
        def funkcja_sort(sb, lista):
            s = wyczyscString(sb)
            if s in lista:
                return (lista.index(s), s)
            return (len(lista), s)
        def msplit(s):
            if s == "":
                return []
            return [wyczyscString(n) for n in s.split(",")]
        return {"dzien"  : lambda x : funkcja_sort(x, msplit(dz)),
                "nazwa"  : lambda x : funkcja_sort(x, msplit(zaj)),
                "kto"    : lambda x : funkcja_sort(x, msplit(naucz)),
                "miejsca": lambda x : funkcja_sort(x, msplit(miejsca)),
                "grupy"  : lambda x : funkcja_sort(x, msplit(gr))}

    def serialise(self):
        dz = self.dzien   #["pn", "wt", "śr", "cz", "pt"][self.dzien]
        g1 = self.int2czytelnaGodz(self.godz1)
        g2 = self.int2czytelnaGodz(self.godz2)
        n = ','.join(self.nazwa)
        naucz = ','.join(self.kto)
        grupy = ','.join(self.grupy)
        miejsca = ','.join(self.miejsca)
        return ";".join([dz, g1, g2, grupy, n, naucz, miejsca])

    def getValuesOfKey(self, key):
        if isinstance(getattr(self, key), list):
            return getattr(self, key)
        return [getattr(self, key)]

    def getCleanedValuesOfKey(self, key):
        vals = self.getValuesOfKey(key)
        return list(filter(None, [wyczyscString(v) for v in vals]))

    def toHtml(self, dodajDzien):
        if dodajDzien:
            lista_kluczy =  ["nazwa", "kto", "grupy", "dzien", "miejsca"]
        else:
            lista_kluczy =  ["nazwa", "kto", "grupy", "miejsca"]
        linijki = [", ".join(self.getValuesOfKey(k)) for k in lista_kluczy]
        linijki.append(self.int2ladnaGodz(self.godz1) + "--" + self.int2ladnaGodz(self.godz2))
        return "<br>\n".join(linijki)

    def getNames(self):
        return " ".join([wyczyscString(n) for n in self.nazwa])

class Plan:
    def __init__(self, s):
        self.kolory = {}
        self.umowa = {}
        if type(s) == type(" "):
            self.readFromStr(s)
        else:
            self.zajecia = s

    def readFromStr(self, s):
        linie = s.split('\n')
        linia_okreslajaca_sortowanie = "#;;;;;"
        self.zajecia = []
        for (nr, l) in enumerate(linie):
            if l.count(';') in Zajecia.ileSrednikow:
                if l.startswith("#"):
                    linia_okreslajaca_sortowanie = l
                else:
                    try:
                        if " " in l and False:
                            print(f"Ostrzeżenie: spacja w linii nr {nr+1}: {l}; usuwam wszystkie spacje")
                            l = l.replace(" ","")
                        zaj = Zajecia(l)
                        if zaj.godz2 > 17*60 + 30:
                            print(f"Ostrzeżenie: godzina późniejsza niż 17:30, ignoruję linię nr {nr+1}: {l}")
                            continue
                        if zaj.godz2 <= zaj.godz1:
                            print(f"Ostrzeżenie: czas trwania ujemny lub zero, ignoruję linię nr {nr+1}: {l}")
                            continue
                        if zaj.godz1 < 7*60 + 30:
                            print(f"Ostrzeżenie: godzina wcześniejsza niż 7:30, ignoruję linię nr {nr+1}: {l}")
                            continue
                        self.zajecia.append(zaj)
                    except:
                        print("Jakiś błąd w linii: ", l)
            else:
                if l.startswith("#kolor "):
                    try:
                        co, jakiKolor = l[len("#kolor "):].split("=")
                        self.kolory[co] = jakiKolor
                    except:
                        print(f"Jakiś błąd w linii nr {nr+1}: {l}")
                elif l.startswith("#godziny "):
                    try:
                        kogo, ile = l[len("#godziny "):].split("=")
                        self.umowa[kogo] = int(float(ile) * 60)
                    except:
                        self.umowa[kogo] = 0
                        print(f"Jakiś błąd w linii nr {nr+1}, przyjmuję zerową liczbę godzin: {l}")
                elif l.count(';') > 1:
                    print(f"Ostrzeżenie: nieoczekiwana liczba średników w linii nr {nr+1}: {l}")

        print("Sortuje wg: ", linia_okreslajaca_sortowanie)
        self.sortowanie = Zajecia.getSortingDict(linia_okreslajaca_sortowanie)

    def fSortujaca(self, kolumna, s):
        return self.sortowanie[kolumna](s)

    def serialise(self):
        return '\n'.join([z.serialise() for z in self.zajecia])
      
    def getValuesOfKey(self, key):
        v = []
        for z in self.zajecia:
            v.extend(z.getValuesOfKey(key))
        return list(set(v))

    def getCleanedValuesOfKey(self, keyName):
        v = []
        for z in self.zajecia:
            v.extend(z.getCleanedValuesOfKey(keyName))
        if keyName in self.sortowanie:
            return sorted(list(set(v)), key = self.sortowanie[keyName])
        else:
            return sorted(list(set(v)))
    
def constructFrom(zajecia):
    return Zajecia(zajecia.serialise())

def copyOtherThings(plan_nowy, plan):
    plan_nowy.kolory = plan.kolory
    plan_nowy.umowa = plan.umowa
    plan_nowy.sortowanie = plan.sortowanie
    return plan_nowy


def printFirstColumn():
    startTime = 7*60 + 30
    endTime = 17*60 + 30
    resolutionTime = 5
    time2str = lambda t : f"{t//60}:{t%60:02}"
    convertToRow = lambda time : (time - startTime) // resolutionTime
    linie = ["<th></th>"]
    for time in range(startTime, endTime, resolutionTime):
        linie.append("<td style=\"font-size:30%;\">" + time2str(time) + "</td>")
    return linie


def printColumn(plan, condition, column_name, key_name, key_nameX, className = "lewy"):
    try:
        filteredPlan = [constructFrom(z) for z in plan.zajecia if condition(z)]
    except:
        filteredPlan = [constructFrom(z) for z in plan if condition(z)]

    def priority_getter(interval):
        if len(filteredPlan[interval[2]].nazwa) > 0:
            return (2, "")
        if len(filteredPlan[interval[2]].kto) == 0:
            return (1, (100000, ""))
        return (1, max([plan.fSortujaca("kto", k) for k in filteredPlan[interval[2]].kto]))
    width_info = widenIntervals(rearrangeIntervals(assignIntervals(filteredPlan, lambda z: z.godz1, lambda z: z.godz2), priority_getter))

    startTime = 7*60 + 30
    endTime = 17*60 + 30
    resolutionTime = 5
    convertToRow = lambda time : (time - startTime) // resolutionTime
    def findWidthInfo(row, col):
        for el in width_info["intervals"]:
            if el["slot"] == col and convertToRow(el["interval"][0]) == row:
                return (el["lastSlot"] - el["slot"] + 1, convertToRow(el["interval"][1]) - convertToRow(el["interval"][0])    )
        raise IndexError
    
    nRows = convertToRow(endTime)
    cells = - np.ones((width_info["max_slots"], nRows))
    for z in width_info["intervals"]:
        x = z["slot"]
        lastX = z["lastSlot"] + 1
        y = convertToRow(z["interval"][0])
        lastY = convertToRow(z["interval"][1])
        cells[x:lastX, y:lastY] = np.zeros((lastX-x, lastY-y))
        cells[x,y]=1 + z["interval"][2]  # index in filteredPlan
    if width_info["max_slots"] == 1:
        linie = [f"<th class=\"{className}\">{column_name}</th>"]
    else:
        cols = width_info["max_slots"]
        linie = [f'<th colspan="{cols}" class="{className}">{column_name}</th>']
    dodajDzien = key_name != "dzien" and key_nameX != "dzien"
    for row in range(nRows):
        linia = []
        for c in range(width_info["max_slots"]):
            if cells[c, row] == -1:
                if c > 0:
                    linia.append("<td></td>")
                else:
                    linia.append(f'<td class="{className}"></td>')
            elif cells[c, row] == 0:
                continue
            else:
                index = int(cells[c, row]) - 1
                (w, h) = findWidthInfo(row, c)
                if h > 1:
                    rowspan = f' rowspan="{h}"'
                else:
                    rowspan = ''
                if w > 1:
                    colspan = f' colspan="{w}"'
                else:
                    colspan = ''
                nazwy_klas = filteredPlan[index].getNames()
                if nazwy_klas == "":
                    nazwy_klas = "_pusta"
                if c == 0:
                    nazwy_klas += f" {className}"
                linia.append(f'<td{rowspan}{colspan} class="{nazwy_klas}">' + filteredPlan[index].toHtml(dodajDzien) + "</td>")
        linie.append('\n'.join(linia))
    return linie

            
def printTable(plan, condition, column_cond, column_name):
    filteredPlan = Plan([constructFrom(z) for z in plan.zajecia if condition(z)])
    filteredPlan = copyOtherThings(filteredPlan, plan)
    column_names = sorted(filteredPlan.getValuesOfKey(column_name), key = lambda z : plan.fSortujaca(column_name, z))

    cols = [printFirstColumn()]
    for n in column_names:
        cols.append(printColumn(filteredPlan, lambda z: n in z.getValuesOfKey(column_name), n, column_cond, column_name))
    table = ['<table style="border: 1px solid black">']
    for row in range(len(cols[0])):
        linia = ["<tr>"]
        for c in range(len(cols)):
            linia.append(cols[c][row])
        linia.append("</tr>")
        table.append("".join(linia))
    table.append("</table>")
    return "\n".join(table)
    
def printTable78(plan, condition, column_full, column_partial, values):
    filteredPlan = Plan([constructFrom(z) for z in plan.zajecia if condition(z)])
    filteredPlan = copyOtherThings(filteredPlan, plan)
    column_names = sorted(filteredPlan.getValuesOfKey(column_full), key = lambda z : plan.fSortujaca(column_full, z))
    subcolumn_names = sorted(values, key = lambda z : plan.fSortujaca(column_partial, z))

    cols = [printFirstColumn()]
    for n1 in column_names:
        for (i2, n2) in enumerate(subcolumn_names):
            if i2 == 0:
                klasa = "lewy"
            else:
                klasa = "podlewy"
            cols.append(printColumn(filteredPlan, lambda z: n1 in z.getValuesOfKey(column_full) and n2 in z.getValuesOfKey(column_partial), n1 + ", " + n2, column_full, column_partial, klasa))
    table = ['<table style="border: 1px solid black">']
    for row in range(len(cols[0])):
        linia = ["<tr>"]
        for c in range(len(cols)):
            linia.append(cols[c][row])
        linia.append("</tr>")
        table.append("".join(linia))
    table.append("</table>")
    return "\n".join(table)


def dajTabele78(nazwa_pliku, klucz, kluczX, wartosci):
    if klucz not in ["dzien", "kto", "grupy", "nazwa"]:
        raise ValueError
    if kluczX not in ["dzien", "kto", "grupy", "nazwa"]:
        raise ValueError
    if kluczX == "dzien":
        cond = lambda z: getattr(z, kluczX) in wartosci
    else:
        cond = lambda z: len(set(wartosci) & set([wyczyscString(s) for s in getattr(z, kluczX)])) > 0
    plan = Plan(open(nazwa_pliku).read())
    return printTable78(plan, cond, klucz, kluczX, wartosci)


def dajCzysteKlucze(nazwa_pliku, klucz):
    plan = Plan(open(nazwa_pliku).read())
    return plan.getCleanedValuesOfKey(klucz)

def dajTabele(nazwa_pliku, klucz, wartosc, kluczX):
    if klucz not in ["dzien", "kto", "grupy", "nazwa", "miejsca"]:
        raise ValueError
    if klucz == "dzien":
        cond = lambda z: getattr(z, klucz) == wartosc
    else:
        cond = lambda z: wartosc in [wyczyscString(s) for s in getattr(z, klucz)]
    plan = Plan(open(nazwa_pliku).read())
    return printTable(plan, cond, klucz, kluczX)



def dajStyle(nazwa_pliku):
    plan = Plan(open(nazwa_pliku).read())
    nazwy = plan.getCleanedValuesOfKey("nazwa")
    nazwy.append("_pusta")
    nazwy = sorted(nazwy)
    kolory = []
    for i in "edcb":
        for j in "edcb":
            for k in "edcb":
                kolory.append("#" + i + j + k)
    linie = []
    for (ind, n) in enumerate(nazwy):
        if n in plan.kolory:
            kol = plan.kolory[n]
            print("***", n, kol)
        else:
            kol = kolory[ind % len(kolory)]
            print("+++", n, kol)
        linie.append("." + n + " { background-color: " + kol + ";  padding: 5px;}")
    return "\n".join(linie) + "\n"


def znajdzPrzedzialyOWart(zajete, warunek):
    przedzialy = []
    pocz = -1
    for i in range(len(zajete)):
        if pocz == -1 and warunek(zajete[i]):
            pocz = i
        elif pocz >= 0 and not warunek(zajete[i]):
            przedzialy.append((pocz, i))
            pocz = -1
    if pocz >= 0:
        przedzialy.append((pocz, len(zajete)))
    return przedzialy


def dajInfoOGodzinachPracy(zajete):
    zajecia = znajdzPrzedzialyOWart(zajete, lambda w: w>=1)
    if len(zajecia) == 0:
        return ((0,0),[],[])
    przerwy = znajdzPrzedzialyOWart(zajete, lambda w: w == 0)
    if zajecia[0][0] > 0:  # zaczynamy pozniej
        przerwy = przerwy[1:]
    if zajecia[-1][1] < len(zajete):  # konczymy wczesniej
        przerwy = przerwy[:-1]
    bilokacje = znajdzPrzedzialyOWart(zajete, lambda w: w>=2)
    return ((zajecia[0][0], zajecia[-1][1]), przerwy, bilokacje)


def dajRaport(plan, dni, naucz):
    linie = [""]  # wstawione pozniej
    startTime = 7*60 + 30
    endTime = 17*60 + 30
    resolutionTime = 5
    convertToRow = lambda time : (time - startTime) // resolutionTime
    convertToTime = lambda n : n * resolutionTime + startTime
    def dodajZajete(zajete, g1, g2):
        pocz = convertToRow(g1)
        kon = convertToRow(g2)
        for i in range(pocz, kon):
            zajete[i] += 1
        return zajete

    def dajCzasWh(czas_w_min):
        if czas_w_min == 0:
            return "0"
        czas_w_h = czas_w_min // 60
        pozostale_min = czas_w_min % 60
        if czas_w_h == 0:
            return f"{pozostale_min}m"
        if pozostale_min == 0:
            return f"{czas_w_h}h"
        return f"{czas_w_h}h {pozostale_min:02}m"

    def dajPrzedzialy(przedzialy):
        if len(przedzialy) == 0:
            return "brak"
        return ", ".join([Zajecia.int2ladnaGodz(convertToTime(p[0])) + "-" + Zajecia.int2ladnaGodz(convertToTime(p[1])) for p in przedzialy])

    laczny_czas_pracy_min = 0
    for dz in dni:
        zajete = [0] * convertToRow(endTime)
        for z in plan.zajecia:
            if naucz in z.kto and z.dzien == dz:
                zajete = dodajZajete(zajete, z.godz1, z.godz2)
        if sum(zajete) > 0:
            godz_pracy, przerwy, bilokacje = dajInfoOGodzinachPracy(zajete)
            czas_pracy_min = (godz_pracy[1] - godz_pracy[0]) * resolutionTime
            laczny_czas_pracy_min += czas_pracy_min
            linie.append(f"<li><b>{dz}: {dajCzasWh(czas_pracy_min)}</b>: {dajPrzedzialy([godz_pracy])}")
            #linie.append(f"<br>przerwy:  {dajPrzedzialy(przerwy)}")
            okienka = [p for p in przerwy if p[1] - p[0] > 6]
            if okienka:
                linie.append(f'<br><span class="blad">okienka: {dajPrzedzialy(okienka)}</span>')
            if bilokacje:
                linie.append(f'<br><span class="blad">bilokacje: {dajPrzedzialy(bilokacje)}</span>')
            linie.append("</li>")
    linie.append("</ul>")
    wg_umowy = dajCzasWh(plan.umowa.get(naucz, 0))
    linie[0] = f"<h3>{naucz} -- {dajCzasWh(laczny_czas_pracy_min)}, wg umowy: {wg_umowy}</h3><ul>"
    return "\n".join(linie)

def dajRaporty(nazwa_pliku):
    plan = Plan(open(nazwa_pliku).read())
    nauczyciele = sorted(plan.getValuesOfKey("kto"))
    dni = sorted(plan.getValuesOfKey("dzien"), key = lambda z : plan.fSortujaca("dzien", z))
    raporty = []
    for n in nauczyciele:
        raporty.append(dajRaport(plan, dni, n))
    return "\n".join(raporty)


def test_znajdzPrzedzialyOWart():
    prz = znajdzPrzedzialyOWart([0,0,1,1,0, 0,1,0,0,1], lambda w : w==1)
    assert(prz == [(2,4), (6,7), (9,10)])

def test_znajdzPrzedzialyOWart2():
    prz = znajdzPrzedzialyOWart([0,0,1,1,1, 1,1,0,0,0], lambda w : w==1)
    assert(prz == [(2,7)])

def test_znajdzPrzedzialyOWart3():
    prz = znajdzPrzedzialyOWart([0,0,1,1,1, 1,1,0,0,0], lambda w : w==2)
    assert(prz == [])
