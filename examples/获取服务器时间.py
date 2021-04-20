from taskoperator import TaskQueue,TaskOperater
from tasklists import *

#设置任务默认的API
Task.set_default_binance_API(
	BinanceRestApi(api_key= "WULDU3TzwOSNR0vRL3zPyumx06ji4O9YKeDM0JpzQA5Gnv6m4RvZMolKK9w8N1qk",
					api_secret="Hc3kKfgi7ZnBgkGCQ3vWmkJEsIsLJwhs8wM5tvL594nH3TvOKCw9V6f97vZLCtF2")
	)

#定义一个任务队列
q = TaskQueue()

#往循环任务队列添加任务
q += CoinMServerTime() #Task 0
#定义一个执行器
op = TaskOperater()
#执行任务队列的任务
op.run()
#获得结果
for task in TaskOperater().\
		 	add_queue(q).\
			fishih_task_generator():
	print(task.result)
