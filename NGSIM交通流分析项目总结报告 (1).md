# 🚦 NGSIM交通流分析项目总结报告

> 汇总时间：2025-10-06  
> 作者：望川空  
> 项目主题：基于 NGSIM 轨迹数据的多断面交通流特征分析与可视化

---

## 🧩 一、项目目标与总体框架

### 🎯 项目目标
本项目基于美国 NGSIM 实测轨迹数据，对交通流进行系统性分析，计算：
- 车辆到达分布；
- 车头时距；
- 断面流量；
- 时间平均速度与空间平均速度；
并验证泊松到达假设是否成立。

### 🏗️ 项目结构
```
ngsim-traffic-analysis/
│
├─ data/                  ← 原始 NGSIM 数据（不上传）
├─ results/               ← 输出结果（不上传）
├─ src/                   ← 模块化源码目录
│   ├─ data_loader.py
│   ├─ section_analysis.py
│   ├─ headway_analysis.py
│   ├─ arrival_analysis.py
│   ├─ flow_speed_analysis.py
│   ├─ visualization.py
│   └─ trajectory_plot.py
│
├─ main.py                ← 主程序入口
├─ requirements.txt       ← 依赖清单
├─ .gitignore             ← 忽略 data/ 与 results/
└─ README.md              ← 项目说明
```

---

## 📘 二、Python 数据处理与算法原理

### 🧮 1. 数据源：NGSIM轨迹文件
每行代表一辆车在某时刻的状态，核心字段：

| 列名 | 含义 |
|------|------|
| Vehicle ID | 车辆编号 |
| Frame ID | 帧编号（每帧0.1秒） |
| Local X / Y | 局部坐标（英尺） |
| Vehicle Velocity | 速度 (ft/s) |
| Lane ID | 车道编号 |
| Preceding Vehicle ID | 前车编号 |
| Space Headway | 车距 (ft) |
| Time Headway | 时距 (s) |

> 关键转换：`Frame ID × 0.1 = 时间 (s)`。

---

### 🧩 2. Pandas 操作要点

```python
df = pd.read_csv(path, sep=r"\s+", names=col_names)
df["Frame ID"] *= 0.1
df_lane = df[df["Lane ID"] == 2]
df.groupby("Vehicle ID")
```

掌握操作：
- `groupby()` 分组遍历；
- `sort_values()` 排序；
- `diff()` 计算相邻差；
- `reset_index(drop=True)` 重置索引。

---

### 🧠 3. 线性插值原理

计算车辆通过断面的精确时刻：

\[
t_\text{cross} = t_{i-1} + \frac{y_s - y_{i-1}}{y_i - y_{i-1}} (t_i - t_{i-1})
\]

作用：消除帧率离散误差，使断面过车时刻更连续、精确。

---

## 📈 三、交通流特征与指标计算

### 🚗 1. 车辆到达分布
在每个时间窗（如10秒）统计通过断面的车辆数：

- 观测分布：`np.bincount(arrivals)`
- 理论分布：`stats.poisson.pmf(k, λ)`
- 检验方法：卡方检验

\[
\chi^2 = \sum \frac{(O_i - E_i)^2}{E_i}
\]

判断标准：
- p > 0.05 → 接受泊松假设
- p ≤ 0.05 → 拒绝泊松假设（存在聚集或车流干扰）

---

### ⏱️ 2. 车头时距（Headway）
定义：连续两车通过同一断面的时间间隔。

\[
h_i = t_i - t_{i-1}
\]

统计指标：
- 平均车头时距；
- 标准差；
- 变异系数 \( CV = \frac{σ}{μ} \)。

交通状态判断：
| CV 值 | 车流特性 |
|--------|------------|
| < 0.33 | 稀疏流 |
| 0.33~0.6 | 稳定流 |
| > 0.6 | 拥挤流 |

---

### 🚦 3. 流量与速度指标

- 流量：  
  \[
  Q = \frac{n}{Δt} × 3600
  \]

- 时间平均速度：  
  \[
  v_t = \frac{1}{n}\sum v_i
  \]

- 空间平均速度：  
  \[
  v_s = \frac{n}{\sum (1/v_i)}
  \]

对比：
| 指标 | 特征 | 偏向性 |
|------|------|---------|
| 时间平均速度 | 算术平均 | 偏向快车 |
| 空间平均速度 | 调和平均 | 更代表整体流效率 |

---

## 🎨 四、可视化与结果展示

### 🧭 1. 车辆时空轨迹图
```python
for vid, g in df_lane.groupby("Vehicle ID"):
    plt.plot(g["Frame ID"], g["Local Y"], linewidth=0.4, alpha=0.5)
```
横轴为时间，纵轴为位置，反映交通运行动态。

---

### 🕒 2. 车头时距直方图
```python
plt.hist(headways, bins=30, edgecolor="black", alpha=0.7)
```

---

### 📊 3. 到达分布与泊松拟合
```python
plt.bar(k_vals, pmf_obs)
plt.plot(k_vals, pmf_poisson, "r--")
```

---

### 📈 4. 流量与速度曲线对比
展示各断面的流量变化、速度变化趋势。

---

### 📝 5. 自动报告生成

`results/summary_report.txt` 包含：

```
NGSIM 交通流分析报告
--------------------------------------------------
生成时间：2025-10-06 20:34:19
分析车道：2
分析断面：200, 400, 600
时间窗：10 秒
...
✅ 图像文件已保存到 results/ 目录。
```

---

## 🧮 五、统计分析与结果解释

| 项目 | 结果 | 含义 |
|------|------|------|
| 泊松检验 p < 0.05 | 拒绝泊松假设 | 存在车流聚集 |
| CV ≈ 0.5 | 中等波动 | 流态稳定但非完全自由 |
| 时间均速略高于空间均速 | 交通流存在差异性 | 稳定流特征明显 |

---

## 🧰 六、工程化实现要点

| 模块 | 功能 |
|------|------|
| `data_loader.py` | 读取与预处理数据 |
| `section_analysis.py` | 计算断面过车时刻 |
| `headway_analysis.py` | 分析车头时距 |
| `arrival_analysis.py` | 拟合泊松分布并绘图 |
| `flow_speed_analysis.py` | 计算流量与速度 |
| `visualization.py` | 绘制图像并保存结果 |
| `main.py` | 主流程调度与报告生成 |

---

## 💾 七、Git 与 GitHub 工作流

### ⚙️ 基础命令
```bash
git init
git add .
git commit -m "update: 优化泊松分布检验与可视化"
git push
```

### ⚠️ 忽略大文件（`.gitignore`）
```plaintext
data/
results/
__pycache__/
*.pyc
```

### 💡 更新流程
```bash
git add .
git commit -m "fix: 调整 section_analysis 缩进问题"
git push
```

---

## 🧭 八、自动化分析流程图

```
main.py
│
├─ 数据加载 → load_ngsim_data()
├─ 断面计算 → compute_section_crossings()
├─ 车头时距 → analyze_headways()
├─ 到达统计 → compute_arrival_counts()
├─ 分布检验 → fit_and_plot_distribution()
├─ 流量速度 → compute_flow_speed()
├─ 可视化输出 → visualization 模块
└─ 汇总报告 → save_summary_report()
```

---

## 🧠 九、学习成果总结

| 能力类别 | 收获 |
|-----------|------|
| 数据分析 | 掌握交通流轨迹数据清洗与特征提取 |
| 数学建模 | 理解泊松分布与卡方检验原理 |
| 编程能力 | 熟练掌握 Pandas / NumPy / Matplotlib |
| 工程化 | 能独立搭建模块化 Python 项目结构 |
| 可视化表达 | 设计出交通流断面特征图、分布对比图 |
| 自动化 | 生成可复现分析与自动报告 |
| 版本控制 | 完整掌握 Git + GitHub 工作流 |

---

## 🚀 十、未来扩展方向

- 📈 多车道流量比较分析；
- 📊 用指数分布 / Erlang 拟合车头时距；
- 🧠 引入聚类检测异常车流；
- 📉 增加 KDE 平滑分布；
- 🧾 输出 PDF 报告；
- ☁️ 使用 GitHub Actions 自动运行分析。

---

## ✅ 十一、总结

> 本项目实现了一个完整的科研级交通流分析流程，  
> 从时空轨迹到断面统计、从分布检验到自动化报告，  
> 不仅具备理论深度，也符合工程实践标准。  
>  
> 你已掌握从「数据 → 分析 → 可视化 → 报告 → 上传」的全栈科研能力。
