"""
arrival_analysis.py
-------------------
模块功能：
分析车辆到达分布（PMF），并拟合泊松分布与负二项分布，进行卡方检验。
"""

import numpy as np  # 数值计算库，用于数组与数学运算
import pandas as pd  # 数据处理库，用于 DataFrame 操作
import matplotlib.pyplot as plt  # 绘图库，用于绘制图形
from scipy import stats  # SciPy 的统计模块，用于分布与检验

plt.rcParams["font.sans-serif"] = ["SimHei"]  # 设置绘图默认中文字体为 SimHei
plt.rcParams["axes.unicode_minus"] = False  # 避免坐标轴负号显示为中文问号


def compute_arrival_counts(results, window_s=10):
    """
    根据断面结果，统计每个时间窗的到达辆数。
    参数：
        results (dict): 来自 section_analysis 的结果
        window_s (float): 时间窗大小（秒）
    返回：
        counts_by_section (dict): 各断面的到达统计表
    """
    counts_by_section = {}  # 存放每个断面对应的每窗到达辆数字典

    for y_section, arr_df in results.items():  # 遍历每个断面及其数据表
        times = arr_df["过断面时间(s)"].values  # 提取所有通过时间的 numpy 数组
        if len(times) == 0:  # 若该断面没有车辆通过则跳过
            continue

        # 计算时间范围并构建以 window_s 为宽度的时间窗边界
        t_min, t_max = times.min(), times.max()  # 获取最早/最晚通过时间
        t0 = np.floor(t_min / window_s) * window_s  # 向下对齐到第一个窗起点
        t1 = np.ceil(t_max / window_s) * window_s  # 向上对齐到最后一个窗终点
        bins = np.arange(t0, t1 + window_s, window_s)  # 生成所有窗的左边界数组

        # 将每辆车的通过时间映射到对应窗口的起点（左边界）
        bin_lefts = []  # 存放每辆车所属窗口的左边界时间
        for t in times:
            k = int((t - t0) // window_s)  # 计算时间落在哪个窗口索引
            b = t0 + k * window_s  # 计算该窗口的起点时间
            bin_lefts.append(b)  # 记录该车辆的窗口起点

        # 统计每个窗口内的到达辆数
        counts_dict = {
            b: 0 for b in bins[:-1]
        }  # 初始化每个窗的计数为 0（排除最后一个边界）
        for b in bin_lefts:
            counts_dict[b] += 1  # 对应窗口计数加一

        # 将计数字典转换为排序后的 DataFrame，便于后续分析与绘图
        out = (
            pd.DataFrame(
                {
                    "时间窗起点(s)": list(counts_dict.keys()),  # 窗口起点列表
                    "到达辆数": list(counts_dict.values()),  # 每窗到达车辆数列表
                }
            )
            .sort_values("时间窗起点(s)")  # 按时间升序排序
            .reset_index(drop=True)  # 重置索引，丢弃旧索引
        )

        counts_by_section[y_section] = out  # 保存该断面的统计表

    return counts_by_section


def fit_and_plot_distribution(counts_by_section):
    """
    拟合泊松分布并绘制比较图，同时返回每个断面的卡方检验结果。
    """
    results = {}  # 用于保存每个断面的检验结果

    for y_section, out in counts_by_section.items():  # 遍历每个断面
        arrivals = out["到达辆数"].values
        if len(arrivals) == 0:
            continue

        # ===== 计算统计量 =====
        mean_val = np.mean(arrivals)
        var_val = np.var(arrivals, ddof=1)
        lambda_hat = mean_val

        print(f"\n🚗 断面 {y_section} ft:")
        print(f"  平均到达数 = {mean_val:.2f}, 方差 = {var_val:.2f}")

        # ===== 观测与期望频数 =====
        k_vals = np.arange(0, max(arrivals) + 1)
        pmf_poisson = stats.poisson.pmf(k_vals, lambda_hat)
        obs_counts = np.bincount(arrivals)
        exp_pois = pmf_poisson * len(arrivals)

        n = min(len(obs_counts), len(exp_pois))
        obs_counts = obs_counts[:n]
        exp_pois = exp_pois[:n]
        exp_pois *= obs_counts.sum() / exp_pois.sum()

        chi2 = stats.chisquare(f_obs=obs_counts, f_exp=exp_pois)
        conclusion = "拒绝泊松假设" if chi2.pvalue <= 0.05 else "接受泊松假设"

        print(f"  泊松检验: χ²={chi2.statistic:.2f}, p={chi2.pvalue:.3f}")
        print(f"  结论: {conclusion}")

        # ===== 保存结果 =====
        results[y_section] = {
            "chi2": chi2.statistic,
            "p": chi2.pvalue,
            "结论": conclusion,
        }

        # ===== 绘图 =====
        plt.figure(figsize=(7, 4))
        plt.bar(
            k_vals,
            np.bincount(arrivals, minlength=len(k_vals)) / len(arrivals),
            alpha=0.6,
            edgecolor="black",
            label="观测分布",
        )
        plt.plot(
            k_vals, pmf_poisson, "r--", lw=2, label=f"泊松分布 (λ={lambda_hat:.2f})"
        )
        plt.xlabel("每窗到达辆数 k")
        plt.ylabel("概率")
        plt.title(f"断面 {y_section} ft：泊松到达分布拟合")
        plt.legend()
        plt.grid(alpha=0.3)
        plt.tight_layout()
        plt.show()

    return results  # ✅ 返回每个断面的检验结果字典


if __name__ == "__main__":  # 脚本直接运行时执行以下代码块
    from src.data_loader import load_ngsim_data
    from src.section_analysis import compute_section_crossings

    # 加载数据（指定文件路径）
    df = load_ngsim_data(
        r"C:\Users\31078\Desktop\ngsim-traffic-analysis\data\NGSIM\US-101-Main-Data\vehicle-trajectory-data\0820am-0835am\trajectories-0820am-0835am.txt"
    )
    df_lane = df[df["Lane ID"] == 2]  # 仅选择车道 ID 为 2 的车辆
    sections = [200, 400, 600]  # 需要分析的断面位置（单位：ft）
    results = compute_section_crossings(df_lane, sections)  # 计算每辆车通过各断面的时间

    # 计算每个时间窗的到达数
    counts_by_section = compute_arrival_counts(results, window_s=10)

    # 对每个断面拟合分布并绘图展示
    fit_and_plot_distribution(counts_by_section)
