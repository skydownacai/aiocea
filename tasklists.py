from tasks import Task,ReponseHandler
from utils import BinanceRestApi


#首先是币本文合约请求任务
class CoinMPing(Task):
	'''
	测试服务器连通
	'''
	async def __call__(self, *args, **kwargs):
		response = await self.binance_API.\
						 request(method = "GET",
								 url = BinanceRestApi.CoinM_BASE_URL + "/dapi/v1/ping")
		return response
	def __str__(self):
		return  "ping币安币本位服务器"

class CoinMServerTime(Task):
	'''
	获取币本位合约服务器时间
	'''
	@ReponseHandler.JsonResponse()
	async def __call__(self, *args, **kwargs):
		response = await self.binance_API.\
						 request(method = "GET",
								 url = BinanceRestApi.CoinM_BASE_URL + "/dapi/v1/time")
		return response
	def __str__(self):
		return "获取币安币本位服务器时间"

class CoinMSymbolInfo(Task):
	'''
	获取交易规则和交易对
	'''
	@ReponseHandler.JsonResponse()
	async def __call__(self, *args, **kwargs):
		response = await self.binance_API. \
						request(method="GET",
								url=BinanceRestApi.CoinM_BASE_URL + "/dapi/v1/exchangeInfo")
		return response
	def __str__(self):
		return "获取币本位合约交易规则和交易对"

class CoinMDepth(Task):
	'''
	获取深度信息
	'''
	def __init__(self,symbol : str,
				 limit : int = 500):
		super(CoinMDepth, self).__init__()
		self.symbol = symbol
		self.limit  = limit
	@ReponseHandler.JsonResponse()
	async def __call__(self, *args, **kwargs):
		data = {"symbol" : self.symbol,
				"limit"  : self.limit}
		response = await self.binance_API. \
						request(method="GET",
								url=BinanceRestApi.CoinM_BASE_URL + "/dapi/v1/depth",
								data = data)
		return response
	def __str__(self):
		return "获取币本文%s合约深度信息(limit:%d)" % (self.symbol,self.limit)

class CoinMTrades(Task):
	'''
	获取近期成交信息
	'''
	def __init__(self,symbol : str,
				 limit : int = 500):
		super(CoinMTrades, self).__init__()
		self.symbol = symbol
		self.limit  = limit

	@ReponseHandler.JsonResponse()
	async def __call__(self, *args, **kwargs):
		data = {"symbol" : self.symbol,
				"limit"  : self.limit}
		response = await self.binance_API. \
						request(method="GET",
								url=BinanceRestApi.CoinM_BASE_URL + "/dapi/v1/trades",
								data = data)
		return response

	def __str__(self):
		return "获取币本文%s合约近期成交信息(limit:%d)" % (self.symbol,self.limit)

class CoinMHistoricalTrades(Task):
	'''
	查询历史成交
	'''
	def __init__(self,symbol : str,
				 limit : int = 500,
				 fromId: int = None):
		super(CoinMHistoricalTrades, self).__init__()
		self.symbol = symbol
		self.limit  = limit
		self.fromId = fromId

	@ReponseHandler.JsonResponse()
	async def __call__(self, *args, **kwargs):
		data = {"symbol" : self.symbol,
				"limit"  : self.limit}
		if self.fromId != None:
			data ["fromId"] = self.fromId
		response = await self.binance_API. \
						request(method="GET",
								url=BinanceRestApi.CoinM_BASE_URL + "/dapi/v1/historicalTrades",
								data = data)
		return response
	def __str__(self):
		return "获取币本文%s合约历史成交信息(limit:%d)" % (self.symbol,self.limit)

class CoinMBookTicker(Task):
	'''
	获取当前最优挂单
	'''
	@ReponseHandler.JsonResponse()
	async def __call__(self, *args, **kwargs):
		response = await self.binance_API.\
						 request(method = "GET",
							    	url = BinanceRestApi.CoinM_BASE_URL + "/dapi/v1/ticker/bookTicker")
		return response
	def __str__(self):
		return "返回当前最优的挂单"

class CoinMFundingRate(Task):
	'''
	获取查询永续合约资金费率历史

	'''
	def __init__(self,symbol : str,
				 startTime : int = None,
				 endTime   : int = None,
				 limit     : int = 100):
		super(CoinMFundingRate, self).__init__()
		self.symbol = symbol
		self.startTime = startTime
		self.endTime   = endTime
		self.limit     = limit
	@ReponseHandler.JsonResponse()
	async def __call__(self, *args, **kwargs):
		data = {"symbol" : self.symbol,
				"limit"  : self.limit}
		if self.startTime != None:
			data["startTime"] = self.startTime
		if self.endTime != None:
			data["endTime"] = self.endTime
		response = await self.binance_API.\
						 request(method = "GET",
							     url = BinanceRestApi.CoinM_BASE_URL + "/dapi/v1/fundingRate")
		return response
	def __str__(self):
		return "查询币本位%s合约永续合约资金费率历史<%s to %s>(limit %d)" %(self.symbol,self.startTime,self.endTime,self.limit)


class CoinMFetchKline(Task):
	'''
	获取k线
	'''
	def __init__(self,symbol : str,interval : str = "1m",
				 limit 	: int = 1500,
				 startTime : int = None,
				 endTime   : int = None):
		super(CoinMFetchKline, self).__init__()
		self.symbol = symbol
		self.interval = interval
		self.startTime = startTime
		self.endTime = endTime
		self.limit =limit

	@ReponseHandler.JsonResponse()
	async def __call__(self, *args, **kwargs):
		data = {"symbol" : self.symbol,
				"interval": self.interval,
				"limit"   : self.limit}
		if self.startTime != None:
			data["startTime"] = self.startTime
		if self.endTime != None:
			data["endTime"] = self.endTime
		response = await self.binance_API.\
						 request(method = "GET",
								url = BinanceRestApi.CoinM_BASE_URL + "/dapi/v1/klines",
								data = data)
		return response

	def __str__(self):
		return "获取币本位合约:%s %s周期 K线<%s to %s>(limit %d)" % (self.symbol,self.interval,self.startTime,self.endTime,self.limit)

class CoinMFetchTicker(Task):
	'''
	获取Ticker
	'''
	def __init__(self,symbol : str,pair : str):
		super(CoinMFetchTicker, self).__init__()
		self.symbol = symbol
		self.pair   = pair

	@ReponseHandler.JsonResponse()
	async def __call__(self, *args, **kwargs):
		data = {"symbol" : self.symbol}
		response = await self.binance_API.\
						 request(method = "GET",
								url = BinanceRestApi.CoinM_BASE_URL + "/dapi/v1/ticker/price",
								data = data)
		return response
	def __str__(self):
		return "获取币本位合约:%s 实时价格" % self.symbol

class CoinMBasis(Task):
	'''
	获取基差
	'''
	@ReponseHandler.JsonResponse()
	async def __call__(self, *args, **kwargs):
		response = await self.binance_API. \
						request(method="GET",
								url=BinanceRestApi.CoinM_BASE_URL + "/futures/data/basis")
		return response
	def __str__(self):
		return "获取基差"