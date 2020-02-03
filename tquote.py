#!/usr/bin/python

import urllib, re, time, datetime, math, curses
import xml.etree.ElementTree as et

quote = urllib.urlopen("http://www.bmfbovespa.com.br/cotacoes2000/formCotacoesMobile.asp?codsocemi=PETRD20").read()
root = et.fromstring(quote)
stock = root.find("PAPEL")
print(float(stock.get("VALOR_ULTIMO").replace(",", ".")))

