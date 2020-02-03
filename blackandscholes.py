#!/usr/bin/python

#spot_price -> PrecoAtivo
#price -> PrecoExercicio
#volatility -> Volatilidade
#interest_rate -> TaxaJuros
#time_to_maturity -> Tempo

import math

class BlackAndScholes():
	def __init__(self, spot_price, price, volatility, interest_rate, time_to_maturity):
		self.spot_price = spot_price
		self.price = price
		self.volatility = volatility
		self.interest_rate = interest_rate
		self.time_to_maturity = time_to_maturity
		self.p1 = (math.log(self.spot_price / self.price) + (self.interest_rate + (self.volatility ** 2 / 2)) * self.time_to_maturity) / (self.volatility * math.sqrt(self.time_to_maturity))
		self.p2 = self.p1 - self.volatility * math.sqrt(self.time_to_maturity)

	def set_spot_price(self, spot_price):
		self.spot_price = spot_price
		self.p1 = (math.log(self.spot_price / self.price) + (self.interest_rate + (self.volatility ** 2 / 2)) * self.time_to_maturity) / (self.volatility * math.sqrt(self.time_to_maturity))
		self.p2 = self.p1 - self.volatility * math.sqrt(self.time_to_maturity)

	def delta(self):
		return BlackAndScholes.ncd(self.p1)
	
	def gamma(self):
		return (1 / math.sqrt(2 * math.pi) * math.exp(-self.p1 ** 2 / 2)) / (self.spot_price * self.volatility * math.sqrt(self.time_to_maturity))
	
	def theta(self):
		return (-self.spot_price * (1 / math.sqrt(2 * math.pi) * math.exp(-self.p1 ** 2 / 2)) * self.volatility / (2 * math.sqrt(self.time_to_maturity))) + (-self.interest_rate * self.price * math.exp(-self.interest_rate * self.time_to_maturity) * BlackAndScholes.ncd(self.p2))
	
	def vega(self):
		return self.spot_price * math.sqrt(self.time_to_maturity) * (1 / math.sqrt(2 * math.pi) * math.exp(-self.p1 ** 2 / 2))
	
	def rho(self):
		return self.price * self.time_to_maturity * math.exp(-self.interest_rate * self.time_to_maturity) * BlackAndScholes.ncd(self.p2)
	
	def implied_volatility(self, actual_price):
		a, b, eps, n = 0.0, 2.0, 10.0 ** (-5), 1
		volatility = (a + b) / 2
		diff = actual_price - self.__price_bs(volatility)
		while abs(diff) > eps and n <= 100:
			if diff > 0.0:
				a = volatility
			else:
				b = volatility
			volatility = (a + b) / 2.0
			diff = actual_price - self.__price_bs(volatility)
			n = n + 1
		return 0 if n > 100 else volatility
	
	def price_bs(self):
		return self.spot_price * self.delta() - self.price * math.exp(-self.interest_rate * self.time_to_maturity) * BlackAndScholes.ncd(self.p2)

	def probability(self):
		return 1 - BlackAndScholes.ncd((math.log(self.price / self.spot_price) - (math.log(1 - self.interest_rate) - (self.volatility ** 2 / 2)) * self.time_to_maturity) / (self.volatility * math.sqrt(self.time_to_maturity)))

	def __price_bs(self, volatility):
		p1 = (math.log(self.spot_price / self.price) + (self.interest_rate + (volatility ** 2 / 2)) * self.time_to_maturity) / (volatility * math.sqrt(self.time_to_maturity))
		p2 = p1 - volatility * math.sqrt(self.time_to_maturity)
		return self.spot_price * BlackAndScholes.ncd(p1) - self.price * math.exp(-self.interest_rate * self.time_to_maturity) * BlackAndScholes.ncd(p2)

	@staticmethod
	def ncd(x):
		b1 = 0.319381530
		b2 = -0.356563782
		b3 = 1.781477937
		b4 = -1.821255978
		b5 = 1.330274429
		p = 0.2316419
		c = 0.39894228
		factor = 1 if x >= 0 else -1
		t = 1.0 / (1.0 + factor * p * x)
		return factor * ((factor + 1) / 2 - c * math.exp(-x * x / 2.0) * t * (t * (t * (t * (t * b5 + b4) + b3) + b2) + b1))
		
	@staticmethod
	def ncdinv(x):
		a = [-3.969683028665376E1, 2.209460984245205E2, -2.759285104469687E2, 1.383577518672690E2, -3.066479806614716E1, 2.506628277459239]
		b = [-5.447609879822406E1, 1.615858368580409E2, -1.556989798598866E2, 6.680131188771972E1, -1.328068155288572E1]
		c = [-7.784894002430293E-3, -3.223964580411365E-1, -2.400758277161838, -2.549732539343734, 4.374664141464968, 2.938163982698783]
		d = [7.784695709041462E-3, 3.224671290700398E-1, 2.445134137142996, 3.754408661907416]
		xlow = 0.02425
		xhigh = 1 - xlow
		
		if (x < xlow):
			q = math.sqrt(-2 * math.log(x))
			return -(((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) / ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1)
		elif (x > xhigh):
			q  = math.sqrt(-2 * math.log(1 - x))
			return -(((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) / ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1)
		else:
			q = x - 0.5
			r = q * q
			return  (((((a[0] * r + a[1]) * r + a[2]) * r + a[3]) * r + a[4]) * r + a[5]) * q / (((((b[0] * r + b[1]) * r + b[2]) * r + b[3]) * r + b[4]) * r + 1)

