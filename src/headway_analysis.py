"""
headway_analysis.py
-------------------
模块功能：
分析并可视化每个断面的车头时距分布。
"""

import matplotlib.pyplot as plt  # 绘图库
import seaborn as sns  # 统计绘图库，便于绘制带 KDE 的直方图
import pandas as pd  # 数据处理

plt.rcParams["font.sans-serif"] = ["SimHei"]  # 设置中文字体以支持中文显示
plt.rcParams["axes.unicode_minus"] = False  # 避免负号显示问题


def analyze_headways(results):
    """
    分析并绘制各断面的车头时距分布图。

    参数：
        results (dict): 来自 section_analysis 的结果字典
                        key=断面位置(ft)，value=DataFrame(过断面时间, 车头时距)
    返回：
        stats (dict): 每个断面的统计指标（均值、标准差、变异系数）
    """
    stats = {}  # 存储每个断面计算得到的统计指标

    for y_section, arr_df in results.items():  # 遍历每个断面的 DataFrame
        headways = arr_df["车头时距(s)"].dropna()  # 去掉首行可能存在的 NaN 值

        # 如果该断面没有有效数据则跳过
        if len(headways) == 0:
            continue

        # 计算统计量：均值、标准差与变异系数
        mean_hw = headways.mean()  # 平均车头时距
        std_hw = headways.std()  # 标准差
        cv_hw = std_hw / mean_hw if mean_hw > 0 else float("nan")  # 变异系数（CV）

        stats[y_section] = {
            "平均车头时距(s)": mean_hw,
            "标准差(s)": std_hw,
            "变异系数(CV)": cv_hw,
        }  # 保存该断面的统计结果

        # 绘制车头时距分布的直方图（带核密度估计）
        plt.figure(figsize=(7, 4))
        sns.histplot(
            headways, bins=50, kde=True, color="skyblue", edgecolor="black", alpha=0.7
        )  # histplot 会绘制直方图并可选绘制 KDE
        plt.xlabel("车头时距 (s)")  # x 轴标签
        plt.ylabel("频数")  # y 轴标签
        plt.title(f"断面 {y_section} ft 的车头时距分布")  # 图表标题
        plt.grid(alpha=0.3)  # 添加网格线
        plt.tight_layout()  # 自动调整布局
        plt.show()  # 显示图形

        print(
            f"断面 {y_section} ft：平均={mean_hw:.2f}s，标准差={std_hw:.2f}s，CV={cv_hw:.2f}"
        )  # 打印统计摘要

    return stats  # 返回所有断面的统计字典


# 测试模块（单独运行）
if __name__ == "__main__":
    from data_loader import load_ngsim_data
    from section_analysis import compute_section_crossings

    # 读取数据
    df = load_ngsim_data(
        r"C:\Users\31078\Desktop\ngsim-traffic-analysis\data\NGSIM\US-101-Main-Data\vehicle-trajectory-data\0820am-0835am\trajectories-0820am-0835am.txt"
    )
    df_lane = df[df["Lane ID"] == 2]
    sections = [200, 400, 600]

    # 计算断面结果
    results = compute_section_crossings(df_lane, sections)

    # 分析车头时距
    stats = analyze_headways(results)
    print("\n车头时距统计：")
    print(pd.DataFrame(stats).T)
