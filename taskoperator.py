from tasks import  BaseMultiTaskOperate,Task,GenericTask
from typing import Union,List,Generator
from exceptions import NotATaskQueue,NoTaskQueue
import asyncio
import time

class TaskQueue(BaseMultiTaskOperate):
	'''
	先进先出任务队列
	'''
	def __init__(self):
		super(TaskQueue, self).__init__()
	def __iter__(self):
		return self
	def __next__(self):
		if len(self.tasks) == 0 :
			raise StopIteration
		now_task = self.tasks.pop(0)
		return now_task

class TaskRing(BaseMultiTaskOperate):
	'''
	循环任务任务队列
	'''
	def __init__(self,iter_num : int = 2000000000000000000000000,
				 iter_interval: float= 0):
		'''
		:param iter_num: 循环任务的迭代次数
		:param iter_interval: 迭代间隔
		'''
		super(TaskRing, self).__init__()
		self.iter_num = iter_num
		self.iter_interval = iter_interval
		self.next_iter_tasks = []
		self.left_iter_num = iter_num
	def __iter__(self):
		return self
	def __next__(self):
		if len(self.tasks) == 0:
			if self.left_iter_num == 0 :
				raise StopIteration
			self.left_iter_num -= 1
			self.tasks = self.next_iter_tasks
			self.next_iter_tasks = []
		now_task = self.tasks.pop(0)
		self.next_iter_tasks.append(now_task)
		return now_task
class TaskStack(BaseMultiTaskOperate):
	'''
	先进后出任务栈
	'''
	def __init__(self):
		super().__init__()
		self.tasks = [] # task这个变量保存该实例中的任务
	def __iter__(self):
		return self
	def __next__(self):
		if len(self.tasks) == 0:
				raise StopIteration
		now_task = self.tasks.pop(0)
		return now_task
	def add_tasks (self,tasks):
		'''
		添加任务
		:param tasks:
		:return:
		'''
		if not isinstance(tasks,list):
			tasks = [tasks]
		Task.assure_tasks_type(tasks)
		for task in tasks:
			self.tasks = [task] + self.tasks

GenericTaskQueue = Union[TaskQueue,TaskRing,TaskStack] #定义泛用类型

class TaskOperater(object):
	def __init__(self):
		self._taskqueue = None #任务队列
	@property
	def taskqueue(self):
		return self._taskqueue
	@taskqueue.setter
	def taskqueue(self,val : GenericTaskQueue):
		'''
		:param val: 任务执行器设置的任务队列
		:return:
		'''
		if val.__class__ not in [TaskQueue,TaskRing,TaskStack]:
			raise NotATaskQueue()
		self._taskqueue = val
	def add_queue(self,val : GenericTaskQueue):
		self.taskqueue = val
		return self
	def fishih_task_generator(self,exec_interval : int = 0) -> Generator:
		'''
		返回一个迭代器,这个迭代器可以不断返回当前串行执行的任务对象与他的结果
		:param max_iternum: 最大迭代次数
		:param iter_interval: 每次迭代时间间隔
		:param exec_interval: 每个串行任务之间休息间隔
		:return:
		'''
		loop = asyncio.get_event_loop()
		if self.taskqueue == None:
			raise NoTaskQueue

		#串行执行每个任务
		for task in self.taskqueue:
			future = loop.create_task(task())
			loop.run_until_complete(future)
			task.result = future.result()
			yield task
			time.sleep(exec_interval)
	def run(self):
		'''
		串行执行整个任务队列的任务
		:return:
		'''
		g = self.fishih_task_generator()
		for _ in g: ...
	def runSingleTask(self,task : GenericTask):
		'''
		执行某个任务,等价于生成一个TaskQueue。 并设置为执行器所执行的任务队列
		:param task:
		:return:
		'''
		queue = TaskQueue()
		queue += task
		self.taskqueue = queue
		return self
	def repeatSingleTask(self,task : GenericTask,
						 iter_interval  : int = 0):
		'''
		循环执行某个任务,等价于生成一个TaskRing。并设置为执行器所执行的任务队列
		:param task:
		:return:
		'''
		ring = TaskRing(iter_interval = iter_interval)
		ring += task
		self.taskqueue = ring
		return self