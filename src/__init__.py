"""
ngsim_traffic_analysis 包的初始化模块。

该包包含用于 NGSIM 数据加载与断面分析的若干模块：
- data_loader: 读取原始轨迹数据并返回 DataFrame
- section_analysis: 计算车辆过断面时间与车头时距
- headway_analysis: 分析并绘制车头时距分布
- arrival_analysis: 统计到达分布并拟合泊松分布
- flow_speed_analysis: 计算流量与速度统计
- visualization: 将结果绘图并保存

在此模块中不强制导出任何符号；保留为包文档说明。
"""
