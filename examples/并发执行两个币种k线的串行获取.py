from taskoperator import TaskQueue,TaskOperater
from tasklists import CoinMFetchKline
from utils import *
from tasks import Task,SerialTask,GatherTask
import time

#设置任务默认的API
Task.set_default_binance_API(
	BinanceRestApi(api_key= "WULDU3TzwOSNR0vRL3zPyumx06ji4O9YKeDM0JpzQA5Gnv6m4RvZMolKK9w8N1qk",
					api_secret="Hc3kKfgi7ZnBgkGCQ3vWmkJEsIsLJwhs8wM5tvL594nH3TvOKCw9V6f97vZLCtF2")
	)

#定义一个任务队列
q = TaskQueue()

#获取两个币中的两个周期的k线的并发执行

q += GatherTask(
	#第一个币种的两个k线任务
	SerialTask(CoinMFetchKline(symbol = "BTCUSD_PERP",
					  interval="1m",
					  limit  = 1,
					  endTime = int(time.time()) * 1000),
			   CoinMFetchKline(symbol="BTCUSD_PERP",
							   interval="1m",
							   limit=1,
							   endTime=int(time.time()) * 1000)
			   )
	,
	SerialTask(CoinMFetchKline(symbol="ETHUSD_PERP",
							   interval="1m",
							   limit=1,
							   endTime=int(time.time()) * 1000),
			   CoinMFetchKline(symbol="ETHUSD_PERP",
							   interval="1m",
							   limit=1,
							   endTime=int(time.time()) * 1000)
			   )
	)

q.show_tasks()

for task in TaskOperater().add_queue(q).fishih_task_generator():
	print("finish")
	BTC_Kline1 = task.result[0][0]
	BTC_Kline2 = task.result[0][1]
	ETH_Kline1 = task.result[1][0]
	ETH_Kline2 = task.result[1][1]
	print(BTC_Kline1)
	print(BTC_Kline2)
	print(ETH_Kline1)
	print(ETH_Kline2)

