"""
arrival_analysis.py
-------------------
模块功能：
分析车辆到达分布（PMF），并拟合泊松分布，进行卡方检验与图像保存。
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
from src.visualization import save_plot  # 可选：使用自定义保存函数

plt.rcParams["font.sans-serif"] = ["SimHei"]  # 设置中文字体
plt.rcParams["axes.unicode_minus"] = False  # 正常显示负号


def compute_arrival_counts(results, window_s=10):
    """
    根据断面结果，统计每个时间窗的到达辆数。
    """
    counts_by_section = {}
    for y_section, arr_df in results.items():
        times = arr_df["过断面时间(s)"].values
        if len(times) == 0:
            continue

        # 时间窗划分
        t_min, t_max = times.min(), times.max()
        t0 = np.floor(t_min / window_s) * window_s
        t1 = np.ceil(t_max / window_s) * window_s
        bins = np.arange(t0, t1 + window_s, window_s)

        bin_lefts = []
        for t in times:
            k = int((t - t0) // window_s)
            b = t0 + k * window_s
            bin_lefts.append(b)

        counts_dict = {b: 0 for b in bins[:-1]}
        for b in bin_lefts:
            counts_dict[b] += 1

        out = (
            pd.DataFrame(
                {
                    "时间窗起点(s)": list(counts_dict.keys()),
                    "到达辆数": list(counts_dict.values()),
                }
            )
            .sort_values("时间窗起点(s)")
            .reset_index(drop=True)
        )
        counts_by_section[y_section] = out
    return counts_by_section


def fit_and_plot_distribution(counts_by_section):
    """
    拟合泊松分布并绘制比较图，同时返回每个断面的卡方检验结果。
    """
    results = {}
    os.makedirs("results", exist_ok=True)  # 确保保存目录存在

    for y_section, out in counts_by_section.items():
        arrivals = out["到达辆数"].values
        if len(arrivals) == 0:
            continue

        # ===== 计算统计量 =====
        mean_val = np.mean(arrivals)
        var_val = np.var(arrivals, ddof=1)
        lambda_hat = mean_val

        print(f"\n🚗 断面 {y_section} ft:")
        print(f"  平均到达数 = {mean_val:.2f}, 方差 = {var_val:.2f}")

        # ===== 拟合泊松分布 =====
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

        results[y_section] = {
            "chi2": chi2.statistic,
            "p": chi2.pvalue,
            "结论": conclusion,
        }

        # ===== 绘图并保存 =====
        fig, ax = plt.subplots(figsize=(7, 4))
        ax.bar(
            k_vals,
            np.bincount(arrivals, minlength=len(k_vals)) / len(arrivals),
            alpha=0.6,
            edgecolor="black",
            label="观测分布",
        )
        ax.plot(
            k_vals, pmf_poisson, "r--", lw=2, label=f"泊松分布 (λ={lambda_hat:.2f})"
        )
        ax.set_xlabel("每窗到达辆数 k")
        ax.set_ylabel("概率")
        ax.set_title(f"断面 {y_section} ft：泊松到达分布拟合")
        ax.legend()
        ax.grid(alpha=0.3)

        # 保存图像
        save_path = os.path.join("results", f"arrival_distribution_{y_section}ft.png")
        fig.savefig(save_path, dpi=300, bbox_inches="tight")
        plt.close(fig)
        print(f"✅ 已保存图像：{save_path}")

    return results


# ----------------------- 模块独立测试 -----------------------
if __name__ == "__main__":
    from data_loader import load_ngsim_data
    from section_analysis import compute_section_crossings

    df = load_ngsim_data(
        r"C:\Users\31078\Desktop\ngsim-traffic-analysis\data\NGSIM\US-101-Main-Data\vehicle-trajectory-data\0820am-0835am\trajectories-0820am-0835am.txt"
    )
    df_lane = df[df["Lane ID"] == 2]
    sections = [200, 400, 600]
    results = compute_section_crossings(df_lane, sections)
    counts_by_section = compute_arrival_counts(results, window_s=10)
    fit_and_plot_distribution(counts_by_section)
