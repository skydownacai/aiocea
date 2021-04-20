import abc
from typing import Callable,List,Optional,Union
import json
from exceptions import *
import copy
from utils import BinanceRestApi
import asyncio

class ReponseHandler(object):

	@staticmethod
	def MyHandler(handler : Callable):
		'''
		返回一个装饰器,该装饰器用于处理异步网络请求的结果
		:param self:
		:param handler:
		:return:
		'''
		def MyResponse(func : Callable):
			async def handle_responce(* args, ** kwargs):
				response = await func(*args,**kwargs)
				result = handler(response)
				return result
			return handle_responce
		return MyResponse

	@staticmethod
	def JsonResponse():
		'''
		网络请求返回的结果转化为Json格式
		:param func:
		:return:
		'''
		return  ReponseHandler.MyHandler(lambda response : json.loads(response))

class Task(metaclass = abc.ABCMeta):
	'''
	一个独立的异步请求任务
	'''
	default_binance_API = None  #对于某些请求任务,可能需要指定币安多个账户,
	@classmethod
	def set_default_binance_API(cls,val):
		'''
		指定Task类的加密数字货币平台。在指定Binance_API为某个BinanceRestApi实例后,任何新生成的Task实例,都将以这个API进行请求。
		:param val:
		:return:
		'''
		if not isinstance(val,BinanceRestApi):
			raise NotValidPlatform()
		cls.default_binance_API = val
	def __init__(self):
		self._result   = None # 该变量用于保存异步请求最后的结果
		self._binance_API = copy.deepcopy(Task.default_binance_API)
	#统一使用__call__方法来调用异步请求并获得结果
	@abc.abstractmethod
	async def __call__(self, *args, **kwargs): ...
	def __str__(self):
		return "未命名任务"
	@staticmethod
	def assure_tasks_type(tasks : List):
		'''
		用于确保任务列表里面的每个任务都是Task类型的实例
		:param tasks:
		:return:
		'''
		for task in tasks:
			task_classes = [task.__class__]
			for base_class in list(task.__class__.__bases__):
				task_classes.append(base_class)
			if Task not in task_classes and GatherTask not in task_classes and SerialTask not in task_classes:
				raise  NotATask()
	def copy(self):
		'''
		拷贝一份任务
		:return:
		'''
		return copy.deepcopy(self)
	@property
	def result(self) -> Optional:
		return self._result
	@result.setter
	def result(self,val):
		self._result = val
	@property
	def binance_API(self):
		'''
		返回该任务类型所使用的币安APP
		:return:
		'''
		if self._binance_API == None:
			raise BinanceAPINotSetted()

		return self._binance_API
	@binance_API.setter
	def binance_API(self,val):
		if not isinstance(val,BinanceRestApi):
			raise NotValidPlatform()
		self._binance_API = val

class BaseMultiTaskOperate(object):
	'''
	这个类使得对象具有tasks变量,并且可以实现了运算法的重载,可以添加和删除任务,展示当前的任务列表
	'''
	def __init__(self,*args ):
		self.tasks = list(args) # task这个变量保存该实例中的任务

	def add_tasks (self,tasks):
		'''
		添加任务
		:param tasks:
		:return:
		'''
		if not isinstance(tasks,list):
			tasks = [tasks]
		Task.assure_tasks_type(tasks)
		self.tasks += tasks
	def __add__(self, other):
		'''
		添加子任务
		:param other:
		:return:
		'''
		self.add_tasks(other)
		return self
	def __sub__(self, other):
		'''
		删除任务
		:param other:
		:return:
		'''
		if not isinstance(other,list):
			tasks = [other]
		else:
			tasks = other
		for task in tasks:
			try:
				self.tasks.remove(task)
			except:
				pass
		return self
	def show_tasks(self):
		def formatprint(task,head_num : int):
			head = "    "
			if isinstance(task,GatherTask):
				print(head * (head_num - 1)+ "并发任务(%d):" % len(task.tasks))
				for idx,sub_task in enumerate(task.tasks):
					formatprint(sub_task,head_num +1)
			elif isinstance(task,SerialTask):
				print(head * (head_num - 1)+"串行任务(%d):" % len(task.tasks))
				for idx,sub_task in  enumerate(task.tasks):
					formatprint(sub_task,head_num +1)
			else:
				print(head * (head_num - 1)+ str(task))

		if self.__class__ == GatherTask or self.__class__ ==  SerialTask:
			formatprint(self,head_num = 1)
		else:
			print("-------当前任务队列(%d)-------" % len(self.tasks))
			for idx,task in enumerate(self.tasks):
				print("Task %d" % idx)
				formatprint(task,1)
			print("-----------------------")

class MultiTask(BaseMultiTaskOperate):
	'''
	多任务类型
	'''
	def __init__(self, * args):
		'''
		:param args: 单独任务的序列
		'''
		super(MultiTask, self).__init__()
		self._results = None
		tasks = list(args)
		Task.assure_tasks_type(tasks)
		self.tasks += tasks
	@property
	def result(self) -> Optional[List]:
		return self._results
	@result.setter
	def result(self, val):
		if not isinstance(val,list):
			raise NotAList
		self._results = val
	def copy(self):
		'''
		拷贝一份任务
		:return:
		'''
		return copy.deepcopy(self)

class GatherTask(MultiTask):
	'''
	并发任务
	'''
	def __str__(self):
		info = "并发任务(%d):\n" % len(self.tasks)
		for idx,task in enumerate(self.tasks):
			info += "    {:<3d}:%s \n" .format(idx + 1) % str(task)
		return info
	async def __call__(self, *args, **kwargs):
		coros = []
		for subtask in self.tasks:
			coros.append(subtask())
		gathered_future = asyncio.gather(*tuple(coros))
		await gathered_future
		return gathered_future.result()

class SerialTask(MultiTask):
	'''
	多个子任务构成的串行任务
	'''

	def __str__(self):
		info = "串行任务(%d):\n" % len(self.tasks)
		for idx,task in enumerate(self.tasks):
			info += "    {:<3d}:%s \n" .format(idx + 1) % str(task)
		return info

	async def __call__(self, *args, **kwargs):
		results = []
		for task in self.tasks:
			result = await task()
			results.append(result)
		#定义结果
		return results

GenericTask = Union[Task,GatherTask,SerialTask] # 定义泛型类型
