'''
这个模块主要用来规划如何生成任务
'''
from typing import List
from tasks import Task,GatherTask

class SequentialSchedule:
	'''
	序列规划
	'''
	@staticmethod
	def get_time_intervals(startTime:int,
						   endTime:int,
						   cut_interval : int) -> List:
		'''
		根据interval 将时间区间 [startTime,endTime] 分割成多个间隔为interval的小区间 :
		[startTime,startTime +interval - 1] ,[startTime +interval ,startTime +2*interval - 1] ...
		:return:
		'''
		periods = []

		while True:
			next_time = min(startTime + cut_interval - 1, endTime)
			periods.append((startTime, next_time))
			startTime = next_time + 1
			if startTime > endTime: break

		return periods

	@staticmethod
	def create_tasks_from_period(startTime : int,
								 endTime   : int,
								 cut_interval  : int,
								 task      : Task,
								 ** other_kwargs) -> List[Task]:
		'''
		对某些需要等间隔的tartTime与endTime参数 但其他参数相同的任务实例,按照某个时间段等间隔的生成任务
		:param startTime: 起使时间
		:param endTime:   截止时间
		:param cut_interval: 每个区间间隔
		:param task:      需要生成的任务类。注意,该
		:param other_kwargs: 构造该类实例的时,需要的其他参数
		:return:
		'''
		tasks = []
		intervals = SequentialSchedule.get_time_intervals(startTime = startTime,
													endTime   = endTime,
													cut_interval =  cut_interval)
		for (startTime,endTime) in intervals:
			new_task = task(startTime = startTime,
							 endTime   = endTime,
							 ** other_kwargs)
			tasks.append(new_task)

		return tasks

	@staticmethod
	def tasks2GroupedGatherTasks(num_in_one_group : int,
								 tasks : List[Task]) -> List[GatherTask]:
		'''
		将一个任务列表,等额分组。每组构成一个并发任务。
		:param num_in_one_group: 魅族
		:param tasks:
		:return:
		'''
		num_in_one_group = min(num_in_one_group,len(tasks))
		groupedgathertasks = []
		start_idx = 0
		while True:
			end_idx = min(start_idx + num_in_one_group - 1,len(tasks) - 1)
			groupedgathertasks.append(GatherTask(* tasks[start_idx:end_idx + 1]))
			if end_idx == len(tasks) - 1:
				break
			start_idx = end_idx + 1

		return groupedgathertasks