import aiohttp
from exceptions import *

async def _request(method : str, url : str, ** kwargs):
	'''
	统一的异步请求方法
	:param method:
	:param url:
	:param kwargs:
	:return:
	'''
	method = method.lower()
	if method not in ["get","post","delete","put","options","patch","head"]:
		raise NoSuchRequestMethod(method_name = method)

	#设置默认的请求参数
	kwargs.setdefault("timeout",30)

	#请求指定页面
	async with aiohttp.ClientSession() as session:
		async with getattr(session,method)(url, ** kwargs) as rep:
			response = await rep.text()
			return response


class BinanceRestApi:

	API_KEY    = None
	API_SECRET = None
	SPOT_API_URL = 'https://api.binance.com'
	USDM_BASE_URL  = 'https://fapi.binance.com'
	CoinM_BASE_URL = 'https://dapi.binance.com'

	def __init__(self,api_key : str,api_secret: str):
		self.api_key = api_key
		self.api_secret =  api_secret
		#默认的请求头
		self.default_header = {'Accept': 'application/json',
							   'User-Agent': 'binance/python',
							   'X-MBX-APIKEY': self.api_key}

	async def request(self, method : str,url : str,** kwargs):

		#如歌没有设置header,那么使用默认的header
		headers = kwargs.get("headers",self.default_header)

		#如果header没有设置 "X-MBX-APIKEY",那么使用默认的api_key
		if "X-MBX-APIKEY" not in headers:
			headers["X-MBX-APIKEY"] = self.api_key
		kwargs.update({"headers": headers})

		#如果有data参数,转化成querystring
		data = kwargs.get("data",None)
		if data:
			kwargs["params"] = '&'.join('%s=%s' % (key, data[key]) for key in data)
			del kwargs["data"]

		rep = await  _request(method,url, ** kwargs)
		return rep


