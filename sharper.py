#!/usr/bin/python

import urllib2, urllib, re, time, datetime, math, curses, csv
from threading import Thread

def get_symbols():
	list = []
	reader = csv.DictReader(open("sp500.csv"),skipinitialspace=True)
	for row in reader:
		list.append(row["Symbol"])
	return list

def get_sharper(symbol):
	df = datetime.date(2011, 12, 31)
	di = datetime.date(2011, 1, 1)
	url = "http://ichart.finance.yahoo.com/table.csv?s=%s&a=%i&b=%i&c=%i&d=%i&e=%i&f=%i&g=d&ignore=.csv" % (symbol, int(di.strftime("%m")) - 1, int(di.strftime("%d")), int(di.strftime("%Y")), int(df.strftime("%m")) - 1, int(df.strftime("%d")), int(df.strftime("%Y")))
	lines = urllib.urlopen(url).readlines()
	list = []
	list.append(0)
	value = float(lines[1].split(",")[-1])
	data = lines[2:]
	for l in data:
		previous_value = value;
		value = float(l.split(",")[-1])
		list.append(previous_value / value - 1)
	return __sharper_value(list)

def __sharper_value(values=[]):
	count = len(values)
	mean = reduce(lambda x, y: x + y, values, 0) / count
	std_dev = math.sqrt(reduce(lambda x, y: x + (y - mean) ** 2, values, 0) / count)
	return math.sqrt(250) * mean / std_dev

print
s = "AAPL"
for s in get_symbols():
#if 's' in locals():
	try:
		print "Symbol: %s / Sharper: %s" % (s, get_sharper(s))
	except:
		pass

