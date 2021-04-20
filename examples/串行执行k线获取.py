from taskoperator import TaskQueue,TaskOperater
from tasklists import CoinMFetchKline
from utils import *
from tasks import Task,SerialTask,G
import time

#设置任务默认的API
Task.set_default_binance_API(
	BinanceRestApi(api_key= "WULDU3TzwOSNR0vRL3zPyumx06ji4O9YKeDM0JpzQA5Gnv6m4RvZMolKK9w8N1qk",
					api_secret="Hc3kKfgi7ZnBgkGCQ3vWmkJEsIsLJwhs8wM5tvL594nH3TvOKCw9V6f97vZLCtF2")
	)

#定义一个任务队列
q = TaskQueue()

#获取两个币中的两个周期的k线的并发执行

q += CoinMFetchKline(symbol = "BTCUSD_PERP",
					  interval="1m",
					  limit  = 1,
					  endTime = int(time.time()) * 1000)
q += CoinMFetchKline(symbol = "BTCUSD_PERP",
					  interval="1m",
					  limit  = 1,
					  endTime = (int(time.time()) - 60) * 1000)

q.show_tasks()

for task in TaskOperater().add_queue(q).fishih_task_generator():
	print(task,"finish!")
	print(task.result)
