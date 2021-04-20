# aioca  异步数字货币交易所接口框架

aioca是 基于asynico 与aiohttp的数字货币交易所接口整合框架。该框架封装了币安交易所的API(未来将支持更多交易所), 实现了串行,并发, 串行与并发混合执行的 网络请求任务。 该框架逻辑清晰，

## Getting Started : 快速理解框架与逻辑

一个异步网络请求称之为一个任务(Task), 整个框架的调用是任务驱动型的，且具有标准的流程。但框架的设计仍然提供了足够多的灵活性。完成任何一个特定的加密数字货币接口请求任务都要经过以下几个步骤: 

### 1. 实例交易所API

aioca 在utils.py 中封装了交易所Restful API请求方法(目前仅支持币安)。其中, 币安交易所为类`BinanceRestApi` ，它封装了请求币安交易所Restful API时的请求方法。传入你的API_KEY与API_SERECT即可完成一个交易所API请求实例。如下代码:

```python
from utils import BinanceRestApi
API = BinanceRestApi(api_key= "your api key here",
					 api_secret="your api secret here")
```

`BinanceRestApi` 中定义了request方法。调用该方法请求某个网址将会在请求头与querystring中添加币安交易所需要特定的参数，从而实现数据的获取。

### 2. 定义任务

在aico中,`Task`子类,  `GatherTask` 类, `SerialTask` 类， 都是框架所认可 任务类型。我们统称为任务泛型`GenericTask`。下面我们将逐个阐述。所有`GenericTask` 类对象都具有**result**属性，方便在完成任务后调取结果。

#### `Task `及其子类

在tasks.py中定义了`Task`类。任何一个继承自`Task`类, 且在 async def \__call__(self, *args, **kwargs) 方法中定义了异步请求结果的类，都称之为某个特定任务类。如请求币安币本位合约服务器ping: 

```python
class CoinMPing(Task):
	'''
	测试服务器连通
	'''
	async def __call__(self, *args, **kwargs):
		response = await self.binance_API.\
		request(method = "GET",url = BinanceRestApi.CoinM_BASE_URL + "/dapi/v1/ping")
		return response
    
	def __str__(self):
		return  "ping服务器"
```

`Task`类是一个抽象类, 他是整个框架执行任务的最小单元。它要求每个子类实现async def \__call__(self, *args, **kwargs) 方法，定义异步请求的结果，并使用return返回, 从而完成对某个特定任务的定义。

任何继承自`Task`的子类对象都有以下属性和方法:

1. **result :**  

   该属性保存该任务在异步请求成功后的返回结果即async def \__call__()中的return值 。**用户不可手动设置,由框架维护。**

2. **binance_API :**  

   **该属性的设置是为了实现不同的API_KEY,API_SECRET同时获取数据**，它是`BinanceRestApi` 的实例, 因此用户在定义`Task`子类时候可以调用该属性的`request`方法，实现特定API下的网络请求。该属性的默认值将继承自类变量 `Task.default_binance_API` 。因此你可以通过`Task.set_default_binance_API()`方法来设置类变量，那么在之后创建的 `Task`子类实例的**binance_API**属性都将继承这个值。下面的代码例子展示了如何通过设置类变量的方法实现不同`Task`子类在初始化时拥有不同的**binance_API**属性。

   ```python
   from tasks import Task
   from utils import  BinanceRestApi
   from tasklists import CoinMPing
   
   
   #定义两个不同的API请求接口
   API1 = BinanceRestApi(api_key   = "key_1",
   					  api_secret= "screte_1")
   
   API2 = BinanceRestApi(api_key   = "key_2",
   					  api_secret= "screte_2")
   
   #设置Task子类实例默认使用的binanceRestApi
   
   Task.set_default_binance_API(API1)
   
   task1 = CoinMPing() # CoinMPing是预定义好的Task子类,
   
   print("task1:", task1.binance_API.api_key) # output: key_1
   
   #更换Task子类实例默认使用的binanceRestApi
   Task.set_default_binance_API(API2)
   
   task2 = CoinMPing() # CoinMPing是预定义好的Task子类,
   
   print("task2:", task2.binance_API.api_key) # output: key_2
   ```

3. \__str__ : 该方法用于命名这个特定的任务。如若没有实现，将继承自父类`Task`中的方法 

**aioca在tasklists.py 里已经定义了常用的币安数据请求任务，在大多数场景下,直接导入使用即可。返回数据均为原始返回数据json处理后的结果。**



#### `GatherTask`  并发任务类

`GatherTask` 用于将多个`GenericTask` 实例对象包装成一个并发任务类。使得在执行的时候可以并发执行。注意,`GenericTask` 是三种任务类型的统称，因此我们实际上不仅可以将多个单独任务包装成一个并行任务，也可以将多个串行任务包装成一个并发任务。实例化一个`GatherTask` 非常简单。只需要在构造时,传入多个`GenericTask` 实例对象即可。如下例子:

```python
from tasks import GatherTask
from tasklists import CoinMPing,CoinMServerTime

#ping服务器与获取服务器时间并发执行
gathertask = GatherTask(CoinMPing(),
                  CoinMServerTime())
#展示任务
gathertask.show_tasks()
# output:
# 并发任务(2):
#     ping币安币本位服务器
#     获取币安币本位服务器时间

```

我们可以通过show_tasks()方法展示当前并发任务的任务队列。

`GatherTask` 具有**result**属性，他是传入的所有`GenericTask` 实例对象对应的**result**属性构成的列表。



#### `SerialTask`  串行任务类

与`GatherTask`类型类似。`SerialTask`  用于将多个`GenericTask` 实例对象包装成一个串行任务类。使得在执行的时候保证是同步执行。实例化一个`SerialTask`  非常简单。只需要在构造时,传入多个`GenericTask` 实例对象即可。如下例子:

```python
from tasks import SerialTask
from tasklists import CoinMPing,CoinMServerTime

#ping服务器与获取服务器时间不同执行
serialtask = SerialTask(CoinMPing(),
                     CoinMServerTime())
#展示任务
serialtask.show_tasks()
# output:
# 串行任务(2):
#     ping币安币本位服务器
#     获取币安币本位服务器时间
```

我们也可以通过show_tasks()方法展示当前并发任务的任务队列。

`SerialTask` 具有**result**属性，他是传入的所有`GenericTask` 实例对象对应的**result**属性构成的列表。



### 3. 定义任务队列

在aioca中, 执行任务是以队列模型为执行的。执行器将根据不同的任务队列实现不同形式的任务执行顺序。任务队列中的任务

aioca在taskoperator.py中已经预定义了以下三种任务队列模型:

- `TaskQueue` 先进先出任务队列
- `TaskStack` 先进后出任务栈
- `TaskRing`   先进先出循环任务队列。刚对象的生成接受两个参数`iter_num` 与`iter_interval`分别表示任务队列循环次数与每次循环后的sleep时间。

这三种类型统称为: 泛型任务队列`GenericTaskQueue`。

`GenericTaskQueue` 与 `SerialTask`  ,`GatherTask`  类都继承自 `BaseMultiTaskOperate` 这个类，这个类重载了\__add__ 与 _\_ sub__方法，使得我们能够使用加号与减号添加或删减任务。并且都具有`add_tasks` 方法用于添加任务，`show_tasks`方法用于打印当前任务。

下面的列子展示了如何生成一个任务队列。

```python
from tasks import GatherTask,SerialTask
from taskoperator import TaskRing
from tasklists import *

#定义一个循环任务队列
ring = TaskRing()

#往循环任务队列添加任务
ring += CoinMPing() #Task 0
ring += GatherTask(SerialTask(CoinMServerTime(),CoinMFetchTicker(symbol = "BTCUSD_PERP",
                                                 pair   = "BTCUSD")),
               SerialTask(CoinMServerTime(), CoinMFetchTicker(symbol="ETHUSD_PERP",
                                                  pair="ETHUSD")))  #Task1
#展示当前任务
ring.show_tasks()
# output:
# -------当前任务队列(2)-------
# Task 0
# ping币安币本位服务器
# Task 1
# 并发任务(2):
#    串行任务(2):
#        获取币安币本位服务器时间
#        获取币本位合约:BTCUSD_PERP 实时价格
#    串行任务(2):
#        获取币安币本位服务器时间
#        获取币本位合约:ETHUSD_PERP 实时价格
#-----------------------
```

### 4. 创建任务执行器,添加任务队列, 获得执行结果

在aioca中, 执行队列中的任务。都需要任务执行器来执行，它是定义在taskoperator.py中`TaskOperater`类的对象。

任务执行器将同步执行所添加任务队列中的任务，每执行完一个任务，该任务的**result**属性将从**None** 变为对应的异步请求的结果。

任务执行器的整个执行过程的步骤如下所示:

1. 给执行器添加执行任务队列q
2. 循环调用q中\__next__方法，获得当前要执行的任务task
3. 在事件循环loop中执行该任务异步回调方法并获得结果, 并将task.result设置为该结果。
4. 如若任务队列raise StopIteration。停止执行, 否则重复步骤2。

在`TaskOperater` 对象具有以下方法或属性:

1. **taskqueue**属性。 即执行器的 执行任务队列

2. `add_queue` 方法。用于添加一个执行任务队列。传入值必须为泛型任务队列`GenericTaskQueue`对象，并设置为**taskqueue**属性。该方法返回执行器自身,即self。

3. `run` 方法。 执行整个运行步骤。 完成时任务队列中的所有result属性均为返回结果。

4. `fishih_task_generator` 方法 :  

   该方法接受一个参数`exec_interval` 表示每个任务队列中每个任务执行后，sleep时间。

   该方法返回一个生成器，在执行步骤3完成时, yield 该任务对象。

5. `runSingleTask` 方法。 传入一个 泛型任务`GenericTask` 对象。在方法内生成一个`TaskQueue` 对象作为执行器的执行任务队列，并在任务队列中添加传入的任务对象。该方法返回执行器自身，即self。

6. `repeatSingleTask` 方法。 传入一个 泛型任务`GenericTask` 对象。在方法内生成一个`TaskRing` 对象作为执行器的执行任务队列，并在任务队列中添加传入的任务对象。该方法返回执行器自身，即self。



以上便是整个框架的基础逻辑和方法。更多的使用与方法请参考后续的API文档。该框架实际上实际上可以还完成日常其他异步请求结果。

## Examples : 使用例子

#### 获取服务器时间

```python
from taskoperator import TaskQueue,TaskOperater
from tasklists import *

#设置任务默认的API
Task.set_default_binance_API(
   BinanceRestApi(api_key   = "key_1",
			      api_secret= "screte_1"))

#定义一个任务
task = CoinMServerTime()
#定义一个任务队列
q = TaskQueue()
#往任务队列添加任务
q +=task #Task 0

#定义一个执行器并添加任务队列
op = TaskOperater().add_queue(q)

#执行任务队列的任务
op.run()

#获得任务结果
print(task.result)
```

#### 每秒循环获取Ticker

```python
from taskoperator import TaskRing,TaskOperater
from tasklists import *

#设置任务默认的API
Task.set_default_binance_API(
   BinanceRestApi(api_key   = "key_1",
			      api_secret= "screte_1"))

#定义一个Ticker任务
task = CoinMFetchTicker(symbol = "BTCUSD_PERP",pair = "BTCUSD")

#定义一个循环任务队列
q = TaskRing(iter_interval = 1) #循环间隔为1秒

#往任务队列添加任务
q += task #Task 0

#展示任务队列
q.show_tasks()

op = TaskOperater().add_queue(q)

#执行任务队列的任务
for task in op.fishih_task_generator():
   print(task.result)

#output:
# -------当前任务队列(1)-------
# Task 0
# 获取币本位合约:BTCUSD_PERP 实时价格
# -----------------------
# 定义一个执行器并添加任务队列
# [{'symbol': 'BTCUSD_PERP', 'ps': 'BTCUSD', 'price': '55163.4', 'time': 1618897014034}]
# [{'symbol': 'BTCUSD_PERP', 'ps': 'BTCUSD', 'price': '55163.4', 'time': 1618897014034}]
# [{'symbol': 'BTCUSD_PERP', 'ps': 'BTCUSD', 'price': '55163.4', 'time': 1618897014034}]
# [{'symbol': 'BTCUSD_PERP', 'ps': 'BTCUSD', 'price': '55163.4', 'time': 1618897014034}]
# ...
```

#### 每秒循环 并发获取 服务器时间 与 Ticker

```python
from taskoperator import TaskRing,TaskOperater
from tasks import GatherTask
from tasklists import *

#设置任务默认的API
Task.set_default_binance_API(
   BinanceRestApi(api_key   = "key_1",
			      api_secret= "screte_1"))
#定义一个循环任务队列
q = TaskRing(iter_interval = 1) #循环间隔为1秒

#往任务队列添加并发任务
q += GatherTask(CoinMServerTime(),
            CoinMFetchTicker(symbol = "BTCUSD_PERP",pair = "BTCUSD"))

#展示任务队列
q.show_tasks()

for task in TaskOperater().add_queue(q).fishih_task_generator():
   print(task.result)

#output:
#-------当前任务队列(1)-------
#Task 0
#并发任务(2):
#    获取币安币本位服务器时间
#    获取币本位合约:BTCUSD_PERP 实时价格
#-----------------------
#[{'serverTime': 1618897355627}, [{'symbol': 'BTCUSD_PERP', 'ps': 'BTCUSD', 'price': '54927.5', 'time': #1618897355247}]]
#[{'serverTime': 1618897356024}, [{'symbol': 'BTCUSD_PERP', 'ps': 'BTCUSD', 'price': '54925.0', 'time': #1618897356011}]]
#[{'serverTime': 1618897356404}, [{'symbol': 'BTCUSD_PERP', 'ps': 'BTCUSD', 'price': '54925.0', 'time': #1618897356011}]]
#...
```

#### 串行执行k线获取

```python
from taskoperator import TaskQueue,TaskOperater
from tasklists import CoinMFetchKline
from utils import *
from tasks import Task
import time

#设置任务默认的API
Task.set_default_binance_API(
   BinanceRestApi(api_key   = "key_1",
			      api_secret= "screte_1"))

#定义一个任务队列
q = TaskQueue()

#获取两个周期的k线
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
#output: 
#-------当前任务队列(2)-------
#Task 0
#获取币本位合约:BTCUSD_PERP 1m周期 K线<None to 1618898005000>(limit 1)
#Task 1
#获取币本位合约:BTCUSD_PERP 1m周期 K线<None to 1618897945000>(limit 1)
#-----------------------
#获取币本位合约:BTCUSD_PERP 1m周期 K线<None to 1618898005000>(limit 1) finish!
#[[1618897980000, '54963.2', '54975.9', '54963.2', '54975.8', '2662', 1618898039999, '4.84281221', 73, #'2329', '4.23701807', '0']]
#获取币本位合约:BTCUSD_PERP 1m周期 K线<None to 1618897945000>(limit 1) finish!
#[[1618897920000, '54881.1', '54963.2', '54881.1', '54963.1', '17844', 1618897979999, '32.49263090', 320, #15905', '28.96235089', '0']]    
```

#### 并发执行两个币种k线的串行获取

```python
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
#output:
#-------当前任务队列(1)-------
#Task 0
#并发任务(2):
#    串行任务(2):
#        获取币本位合约:BTCUSD_PERP 1m周期 K线<None to 1618898371000>(limit 1)
#        获取币本位合约:BTCUSD_PERP 1m周期 K线<None to 1618898371000>(limit 1)
#    串行任务(2):
#        获取币本位合约:ETHUSD_PERP 1m周期 K线<None to 1618898371000>(limit 1)
#        获取币本位合约:ETHUSD_PERP 1m周期 K线<None to 1618898371000>(limit 1)
#-----------------------
#finish
#[[1618898340000, '54962.4', '55016.4', '54962.4', '55016.4', '15264', 1618898399999, '27.75471862', 150, #'10905', '19.82837640', '0']]
#[[1618898340000, '54962.4', '55016.4', '54962.4', '55016.4', '15284', 1618898399999, '27.79107142', 151, #'10925', '19.86472920', '0']]
#[[1618898340000, '2118.17', '2120.31', '2118.17', '2119.90', '47561', 1618898399999, '224.39426159', 109, '27294', '128.79773623', '0']]
#[[1618898340000, '2118.17', '2120.31', '2118.17', '2119.90', '47561', 1618898399999, '224.39426159', 109, #'27294', '128.79773623', '0']]

```