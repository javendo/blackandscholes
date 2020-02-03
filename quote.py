#!/usr/bin/python2

import urllib2, urllib, re, time, datetime, math, curses, collections
import xml.etree.ElementTree as et
from threading import Thread
from blackandscholes import BlackAndScholes

class Quote():
	cache_cetip_tax = [datetime.datetime.now() - datetime.timedelta(days=1), 0]
	cache_stock_trade = {}

	def __init__(self, symbol):
		self.symbol = symbol
		sufix = {"VALE": "5", "PETR": "4"}
		self.main_symbol = self.symbol[0:4] + sufix[self.symbol[0:4]]
		
	def __get_quote(self, symbol, save_in_cache=True):
		quote = urllib2.urlopen("http://www.bolsafinanceira.com/cotacoes/get_datafeed?codigo=%s" % symbol).read()
                values = quote.split(',')
		stock = values[0]
		if save_in_cache:
			Quote.cache_stock_trade[symbol] = int(values[11])
		return float(values[9])
		
	def get_quote(self):
		return self.__get_quote(self.symbol)

	def get_bosi(self, extrinsic_value):
		return extrinsic_value * Quote.cache_stock_trade[self.symbol] * 100.0 / sum(Quote.cache_stock_trade.values())

	def get_main_quote(self):
		return self.__get_quote(self.main_symbol, False)

        def __month_delta(self, date, delta):
                m, y = (date.month+delta) % 12, date.year + ((date.month)+delta-1) // 12
                if not m: m = 12
                d = min(date.day, [31, 29 if y % 4 == 0 and not y % 400 == 0 else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][m-1])
                return date.replace(day=d, month=m, year=y)
        
        def __third_monday(self, year, month, months_ahead):
                first_day = self.__month_delta(datetime.datetime.strptime(year + month + '01', '%Y%m%d'), months_ahead)
                return (first_day + datetime.timedelta(days = (7 - first_day.weekday()) % 7 + 14))
        
        def get_options(self):
                url = 'http://bvmf.bmfbovespa.com.br/opcoes/opcoes.aspx?idioma=pt-br'
                params = {
                        '__EVENTTARGET': '',
                        '__EVENTARGUMENT': '',
                        '__LASTFOCUS=': '',
                        'ctl00$contentPlaceHolderConteudo$posicoesAbertoEmp$':'rbTodos',
                        'ctl00$contentPlaceHolderConteudo$posicoesAbertoEmp$cmbVcto':'0',
                        'ctl00$contentPlaceHolderConteudo$posicoesAbertoEmp$txtConsultaData':'16/01/2017',
                        'ctl00$contentPlaceHolderConteudo$posicoesAbertoEmp$txtConsultaEmpresa':'',
                        'ctl00$contentPlaceHolderConteudo$posicoesAbertoEmp$txtConsultaDataDownload':'16/01/2017',
                        'ctl00$contentPlaceHolderConteudo$posicoesAbertoEmp$btnBuscarArquivos':'buscar',
                        'ctl00$contentPlaceHolderConteudo$mpgOpcoes_Selected':'0'
                }
                data = urllib.urlencode(params)
                lines = urllib2.urlopen(url, data).readlines()
                now = datetime.datetime.now()
                second_due_date = self.__third_monday(now.strftime("%Y"), now.strftime("%m"), -10)
                if self.__third_monday(now.strftime("%Y"), now.strftime("%m"), 0) > now:
                        first_due_date = self.__third_monday(now.strftime("%Y"), now.strftime("%m"), 0)
                        """
                        second_due_date = self.__third_monday(now.strftime("%Y"), now.strftime("%m"), 1)
                        """
                else:
                        first_due_date = self.__third_monday(now.strftime("%Y"), now.strftime("%m"), 1)
                        """
                        second_due_date = self.__third_monday(now.strftime("%Y"), now.strftime("%m"), 2)
                        """
                stocks = {}
                for l in lines[1:-1]:
                        emitter = l[2:14].strip()
                        stock_spec = l[14:22].strip()
                        market_type = l[39:42].strip()
                        due_date = datetime.datetime.strptime(l[24:32].strip(), '%Y%m%d')
                        if emitter == self.symbol[0:4] and stock_spec == 'PN' and market_type == '070' and (due_date == first_due_date or due_date == second_due_date):
                                stock = l[42:54].strip()
                                price = float(l[62:75].strip())/100
                                stocks[stock] = price
                return collections.OrderedDict(sorted(stocks.iteritems(), key=lambda (k,v): (k[0:5], v)))

	def get_volatility(self, ndays, ydays):
		df = datetime.datetime.now()
		di = df - datetime.timedelta(days=ndays)
		url = "http://ichart.finance.yahoo.com/table.csv?s=%s.SA&a=%i&b=%i&c=%i&d=%i&e=%i&f=%i&g=d&ignore=.csv" % (self.main_symbol, int(di.strftime("%m")) - 1, int(di.strftime("%d")), int(di.strftime("%Y")), int(df.strftime("%m")) - 1, int(df.strftime("%d")), int(df.strftime("%Y")))
		lines = urllib.urlopen(url).readlines()
		list = []
		for l in lines[1:]:
			temp = l.split(",")
			list.append(float(temp[-1]))
		return self.__standard_deviation([math.log(c/n) for c, n in zip(list, list[1:])]) * math.sqrt(ydays) * 100.

	def get_cetip_tax(self) :
		now = datetime.datetime.now()
		if (now - Quote.cache_cetip_tax[0] > datetime.timedelta(days=1)):
			for i in range(0, 6):
				url = "ftp://ftp.cetip.com.br/MediaCDI/%s.txt" % (now - datetime.timedelta(days=i)).strftime("%Y%m%d")
				try:
					req = urllib2.Request(url)
					response = urllib2.urlopen(req)
					self.__class__.cache_cetip_tax[0] = datetime.datetime.now()
					self.__class__.cache_cetip_tax[1] = float(response.read()) / 100
					break
				except:
					pass
		return self.__class__.cache_cetip_tax[1]

	def __standard_deviation(self, values=[]):
		count = len(values)
		mean = reduce(lambda x, y: x + y, values, 0) / count
		return math.sqrt(reduce(lambda x, y: x + (y - mean) ** 2, values, 0) / count)

class Display(Thread):
	keepgoing = True

	def __init__(self, symbol, price, days_of_year, days_of_volatility, screen, pos_x, pos_y):
		Thread.__init__ (self)
		self.symbol = symbol
		self.price = price
		self.days_of_year = days_of_year
		self.days_of_volatility = days_of_volatility
		self.days_to_maturity = self.__days_to_maturity(symbol)
		self.screen = screen
		self.pos_x = pos_x
		self.pos_y = pos_y
		
	def calc_days_to_matyrity(self):
		now = datetime.datetime.now()

	def run(self):
		q = Quote(self.symbol)
		spot_price = q.get_main_quote()
		volatility = q.get_volatility(self.days_of_volatility, self.days_of_year)
		bs = BlackAndScholes(spot_price, self.price, volatility / 100, q.get_cetip_tax() / 100, self.days_to_maturity / self.days_of_year)

		stdscr.nodelay(1)
		while Display.keepgoing:
			try:
				spot_price = q.get_main_quote()
				quote_price = q.get_quote()
				extrinsic_value = spot_price - self.price
				extrinsic_value = quote_price if extrinsic_value <= 0.0 else quote_price - extrinsic_value
				extrinsic_value = extrinsic_value if extrinsic_value > 0.0 else 0.0
				bosi = q.get_bosi(extrinsic_value)
				bs.set_spot_price(spot_price)
				self.screen.addstr(self.pos_x, self.pos_y, "%s\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f\t%.2f" % (self.symbol, self.price, bs.delta(), bs.gamma(), bs.theta() / self.days_of_year, bs.vega(), bs.rho(), quote_price, bs.price_bs(), volatility, bs.implied_volatility(quote_price) * 100, bs.probability() * 100, extrinsic_value, bosi, spot_price), curses.A_BLINK)
				self.screen.refresh()
				time.sleep(2)
			except:
				pass
			curses.noecho()
			Display.keepgoing = (stdscr.getch() != ord('q') if Display.keepgoing else Display.keepgoing)
			curses.echo()
		curses.endwin()
		
	def stop(self):
		Display.keepgoing = False
		
	def __maturity_date(self, symbol):
		now = datetime.date.today()
		maturity_month = ord(symbol[4]) - 64
		maturity_date = datetime.date(now.year, maturity_month, 15)
		while int(maturity_date.strftime("%w")) != 1:
			maturity_date = maturity_date + datetime.timedelta(days=1)
		if maturity_date < now:
			maturity_date = datetime.date(maturity_date.year + 1, maturity_month, 15)
			while (int((maturity_date).strftime("%w")) != 1):
				maturity_date = maturity_date + datetime.timedelta(days=1)
		return maturity_date

	def __days_to_maturity(self, symbol):
		now = datetime.date.today()
		ndays = 0
		maturity_date = self.__maturity_date(symbol)
		if now < maturity_date:
			while (now != maturity_date):
				now = now + datetime.timedelta(days=1)
				ndays = ndays + (0 if int((now).strftime("%w")) % 6 == 0 else 1)
		return ndays



q = Quote("PETR4")
stocks = q.get_options()
days_of_year = 252.0
days_of_volatility = 63
stdscr = curses.initscr()
stdscr.addstr(0, 0, "SYMB\tEXERC\tDELTA\tGAMMA\tTHETA\tVEGA\tRHO\tPRECO\tPRECOBS\tVH\tVI\tPROB.\tVE\tBOSI\tMAIN", curses.A_BLINK)

i = 0
for (k, v) in stocks.items():
	i += 1
	dp = Display(k, v, days_of_year, days_of_volatility, stdscr, i, 0)
	dp.start()
