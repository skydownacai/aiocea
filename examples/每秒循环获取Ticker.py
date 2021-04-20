from taskoperator import TaskRing,TaskOperater
from tasklists import *

#设置任务默认的API
Task.set_default_binance_API(
	BinanceRestApi(api_key= "WULDU3TzwOSNR0vRL3zPyumx06ji4O9YKeDM0JpzQA5Gnv6m4RvZMolKK9w8N1qk",
					api_secret="Hc3kKfgi7ZnBgkGCQ3vWmkJEsIsLJwhs8wM5tvL594nH3TvOKCw9V6f97vZLCtF2")
	)
#定义一个任务
task = CoinMFetchTicker(symbol = "BTCUSD_PERP",pair = "BTCUSD")

#定义一个循环任务队列
q = TaskRing(iter_interval = 1) #循环间隔为1秒

#往任务队列添加任务
q += task #Task 0

#展示任务队列
q.show_tasks()

#定义一个执行器并添加任务队列
op = TaskOperater().add_queue(q)

#执行任务队列的任务
for task in op.fishih_task_generator():
	print(task.result)
