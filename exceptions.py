class NoSuchRequestMethod(Exception):
	def __init__(self,method_name : str):
		super().__init__(self)
		self.method_name = method_name

	def __str__(self):
		return '无效请求方法"%s",合理的请求方法为: "get","post","delete","put","options","patch","head".' % self.method_name

class NotATask(Exception):
	def __init__(self):
		super().__init__(self)
	def __str__(self):
		return '所添加任务必须是Class: Task 实例'

class NotAList(Exception):
	def __init__(self):
		super().__init__(self)
	def __str__(self):
		return '多任务(MultiTask)实例 results属性必须为列表类型'

class NotATaskQueue(Exception):
	def __init__(self):
		super().__init__(self)
	def __str__(self):
		return '错误的任务队列'

class NoTaskQueue(Exception):
	def __init__(self):
		super().__init__(self)
	def __str__(self):
		return '任务执行器尚未添加任务队列,请尝试TaskOperator().add_queue()'

class BinanceAPINotSetted(Exception):
	def __init__(self):
		super().__init__(self)
	def __str__(self):
		return '尚未设置使用的币安API,请尝试: Task.Set_Binance_API'
