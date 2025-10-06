# NGSIM Traffic Analysis

选取一个车道的几个断面，计算这些断面上的车辆到达分布、车头时距分布、流量、时间平均速度、空间平均速度。
验证时间平均速度与空间平均速度的函数关系。
绘制车辆轨迹时空图和基本图。

运行方法：
```bash
python main.py

##  项目结构
ngsim-traffic-analysis/
├── data/ # 数据文件夹（放原始 txt）
├── src/ # 源代码（各功能模块）
├── results/ # 输出图表和统计结果
├── notebooks/ # Jupyter Notebook（可选）
├── main.py # 主程序入口
├── requirements.txt # 环境依赖
└── README.md # 项目说明文件

---

## ⚙️ 环境配置
```bash
# 创建虚拟环境
conda create -n ngsim python=3.11
conda activate ngsim

# 安装依赖
pip install -r requirements.txt
#运行方法
python main.py
本项目使用 NGSIM US-101 数据集
数据集：http://ngsim-community.org/

