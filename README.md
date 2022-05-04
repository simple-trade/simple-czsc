# Simple缠论量化工具集

## 一、简介

​	缠论只是一个工具，请不要将它神化，发现一些客观的规律远比追求虚无缥缈的神论更有意义。

​	本模型按照简单可控的方式实现，与原著的描述不尽相同，为了模型可推导做了一些调整，模型整体按照零参数设计，不必关注策略应该设置定什么参数，是否过度拟合等问题。

​	缠论是一种结构化分析方法，但每个人对于缠论的理解不同，如果有计算机基础，每个人量化的缠论模型也不会完全一致，所以没必要过多纠结是否与自己的实现方式一样，学缠的人一旦纠于细节，理论化、精度化、完美化，基本也就缠进去了。从另一个角度说，缠论是一种视觉体现，是对市场阶段性顶底和交易密集区的量化展示，本模型重在交易，在保证无任何未来函数上实现了实时模型，如果仔细观察最后一个笔和线段是动态的，随着行情的变化而变化，但是确认了的构件是不会改变的，这就保证了回测的稳定性，在本模型基础上按照规则开发出的策略没有任何漂移。

​	开源本模型，提供一种无参的量化实现，爱好者可以继续摸索，形成自己一套技术分析体系。在市场上仅仅懂得技术分析是远远不够的，但是作为散户，没有精力读研报做调研，技术分析仍是一种有效的市场解读方法。技术分析体系的建立意味着面对杂乱无章的市场，你有了自己的解读语言，可以与之对话、交流、提升，进一步可以形成一套交易策略，知道自己在自己的体系下什么情况亏什么时候赚，在概率基础上可以形成持久的可调整的交易框架。希望可以帮助各位找到自己的方法论。


![上证指数](https://user-images.githubusercontent.com/104715342/166645675-89aff9e2-826d-47a8-aef6-2e3200098f2a.png)

演示地址：http://simple-trade.cn:18188/  账户：guest/1

## 二、架构

### 2.1 概览图

本项目基本实现了缠论模型计算、可视化、选股、策略模板等功能，部分功能仍在开发中。

![量化架构-逻辑架构](https://user-images.githubusercontent.com/104715342/166646137-5af0371d-3e2a-4776-86db-10450d251879.png)

## 三、工程结构

```
├── bin # 命令脚本
├── czsc_demo
│   ├── conf 配置项
│   ├── draw 绘图
│   ├── pusher # 消息推送
│   ├── strategy 
│   │   └── myquant # 掘金策略
│   │       ├── code # 策略
│   │       └── selector # 指标选股
│   └── tests # 测试类
├── gmcache # 掘金缓存
└── output # 输出目录
    └── html
```

## 四、开发环境搭建

参考概览图，本项目实现了行情数据推进和策略回测的其他部分，为简单起见使用掘金量化平台的行情数据推进和策略回测进行demo演示。缠论模型自身不依赖任何三方平台，开发策略过程中可以对接任意量化平台或自行实现。

### 4.1 主要技术栈

python 3.7、pandas、pyecharts、selenium

PS：建议使用Anaconda管理开发环境，[清华镜像站下载](https://mirrors.tuna.tsinghua.edu.cn/)。

### 4.2 掘金客户端与策略分离部署

**Windows用户可直接下载本项目使用掘金客户端或者任何Python IDE运行，本节可忽略。**具体使用方法可参考掘金量化平台官方文档。

因掘金客户端目前只有Windows版，而本人日常使用MacOS，所以采用了掘金客户端与策略分离部署方式搭建的开发环境，这也是掘金量化平台亮点---SDK支持外部调用。

#### 4.2.1 分离部署网络架构

​	如`分离部署网络架构图`所示，掘金客户端部署在Windows，策略运行在/Win/Linux/MacOS。从网络层面看，策略运行环境需要访问掘金客户端所在环境的两个端口，以支持掘金平台策略管理和回测。因此需要开放网络策略，方向：工程（策略）运行环境 -> 掘金客户端，端口：rpcPort和subPort。

<center>    <img style="border-radius: 0.3125em;    box-shadow: 0 2px 4px 0 rgba(34,36,38,.12),0 2px 10px 0 rgba(34,36,38,.08);"     src="https://user-images.githubusercontent.com/104715342/166646145-783dfdc7-b0a4-4085-81df-25d3f81af571.png">    <br>    <div style="color:orange; border-bottom: 1px solid #d9d9d9;    display: inline-block;    color: #999;    padding: 2px;">分离部署网络架构图</div> </center>

#### 4.2.2 掘金客户端配置

​	如`掘金客户端配置文件图`所示，安装掘金客户端后配置文件中已默认指定rpcPort和subPort，可在系统用户目录下的.goldminer3/\.gmserv.json修改。（如：C:\Users\Administrator\\.goldminer3\\.gmserv.json）

<center>    <img style="border-radius: 0.3125em;    box-shadow: 0 2px 4px 0 rgba(34,36,38,.12),0 2px 10px 0 rgba(34,36,38,.08);"     src="https://user-images.githubusercontent.com/104715342/166646150-4d748f9e-1a86-4f4a-bcc5-ba7efe555f8d.png">    <br>    <div style="color:orange; border-bottom: 1px solid #d9d9d9;    display: inline-block;    color: #999;    padding: 2px;">掘金客户端配置文件图</div> </center>

#### 4.2.3 创建空白策略

​	打开掘金客户端创建一个空白策略，记录好策略ID。

#### 4.2.4 工程配置	

​	如`工程配置掘金策略ID和客户端地址图`所示，修改工程目录conf/conf.yaml文件，token设置为掘金客户端密钥---在客户端系统管理中查看，serv_addr设置为掘金客户端IP：rpcPort，strategy_id设置为上一步的策略ID。

<center>    <img style="border-radius: 0.3125em;    box-shadow: 0 2px 4px 0 rgba(34,36,38,.12),0 2px 10px 0 rgba(34,36,38,.08);"     src="https://user-images.githubusercontent.com/104715342/166646130-296fef95-a0c2-4765-b99d-6e6859326823.png">    <br>    <div style="color:orange; border-bottom: 1px solid #d9d9d9;    display: inline-block;    color: #999;    padding: 2px;">工程配置掘金策略ID和客户端地址图</div> </center>

### 4.3 运行DEMO策略

可使用三种方式运行策略：

1. bin/test_myquant_strategy_stock_demo.sh 后台运行，后台运行日志存储在bin/simple.log，该方式适用于分离部署时正式执行回测。

2. IDE或命令行运行test_myquant_strategy_stock_demo.py，该方式适用于调试策略。
3. 使用掘金客户端运行策略。

### 4.4 其他依赖

[使用pyecharts提供的selenium方式渲染图片](https://pyecharts.org/#/zh-cn/render_images?id=make_snapshot)







