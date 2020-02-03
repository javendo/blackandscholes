#!/usr/bin/python

import time, datetime
#semana vai de 0 a 6, onde segunda eh 1

s = "PETRD40"


def __maturity_date(symbol):
	now = datetime.date.today()
	maturity_month = ord(symbol[4]) - 64
	maturity_date = datetime.date(now.year, maturity_month, 15)
	while (int((maturity_date).strftime("%w")) <> 1):
		maturity_date = maturity_date + datetime.timedelta(days=1)
	if maturity_date < now:
		maturity_date = datetime.date(maturity_date.year + 1, maturity_month, 15)
		while (int((maturity_date).strftime("%w")) <> 1):
			maturity_date = maturity_date + datetime.timedelta(days=1)
	return maturity_date

def days_to_maturity(symbol):
	now = datetime.date.today()
	ndays = 0
	maturity_date = __maturity_date(symbol)
	if now < maturity_date:
		while (now <> maturity_date):
			now = now + datetime.timedelta(days=1)
			ndays = ndays + (0 if int((now).strftime("%w")) % 6 == 0 else 1)
	return ndays
	
print days_to_maturity(s)
