"""
headway_analysis.py
-------------------
模块功能：
分析并可视化每个断面的车头时距分布，
并进行分布拟合（指数分布、对数正态分布）检验。
"""

import os
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from scipy import stats

plt.rcParams["font.sans-serif"] = ["SimHei"]  # 支持中文
plt.rcParams["axes.unicode_minus"] = False  # 解决负号乱码


def analyze_headways(results, save_dir="results"):
    """
    分析并绘制各断面的车头时距分布图，包含分布拟合与K-S检验。

    参数：
        results (dict): 来自 section_analysis 的结果字典
        save_dir (str): 图像保存文件夹路径
    返回：
        stats (dict): 每个断面的统计指标与分布检验结果
    """
    os.makedirs(save_dir, exist_ok=True)
    stats_summary = {}

    for y_section, arr_df in results.items():
        headways = arr_df["车头时距(s)"].dropna()
        if len(headways) == 0:
            continue

        # === 1️⃣ 计算基础统计量 ===
        mean_hw = headways.mean()
        std_hw = headways.std()
        cv_hw = std_hw / mean_hw if mean_hw > 0 else float("nan")

        # === 2️⃣ 拟合分布：指数分布、对数正态分布 ===
        # 指数分布参数估计
        loc_exp, scale_exp = stats.expon.fit(headways, floc=0)
        # 对数正态分布参数估计
        shape_ln, loc_ln, scale_ln = stats.lognorm.fit(headways, floc=0)

        # === 3️⃣ K-S 检验 ===
        ks_exp = stats.kstest(headways, "expon", args=(loc_exp, scale_exp))
        ks_logn = stats.kstest(headways, "lognorm", args=(shape_ln, loc_ln, scale_ln))

        # === 4️⃣ 绘制直方图 + 理论分布曲线 ===
        fig, ax = plt.subplots(figsize=(7, 4))
        sns.histplot(
            headways,
            bins=50,
            kde=False,
            color="skyblue",
            edgecolor="black",
            stat="density",
            alpha=0.6,
            ax=ax,
        )

        x_vals = np.linspace(headways.min(), headways.max(), 200)
        ax.plot(
            x_vals,
            stats.expon.pdf(x_vals, loc_exp, scale_exp),
            "r--",
            lw=2,
            label=f"指数分布 (λ={1/scale_exp:.2f})",
        )
        ax.plot(
            x_vals,
            stats.lognorm.pdf(x_vals, shape_ln, loc_ln, scale_ln),
            "g-",
            lw=2,
            label="对数正态分布",
        )

        ax.set_xlabel("车头时距 (s)")
        ax.set_ylabel("概率密度")
        ax.set_title(f"断面 {y_section} ft 的车头时距分布拟合")
        ax.legend()
        ax.grid(alpha=0.3)
        plt.tight_layout()

        save_path = os.path.join(save_dir, f"headway_distribution_{y_section}ft.png")
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
        plt.close(fig)
        print(f"✅ 已保存图像：{save_path}")

        # === 5️⃣ 汇总结果 ===
        stats_summary[y_section] = {
            "平均车头时距(s)": mean_hw,
            "标准差(s)": std_hw,
            "变异系数(CV)": cv_hw,
            "指数分布 p值": ks_exp.pvalue,
            "对数正态 p值": ks_logn.pvalue,
            "最优分布": ("指数" if ks_exp.pvalue > ks_logn.pvalue else "对数正态"),
        }

        # 控制台输出摘要
        print(f"\n📊 断面 {y_section} ft：")
        print(f"  平均={mean_hw:.2f}s, 标准差={std_hw:.2f}s, CV={cv_hw:.2f}")
        print(
            f"  指数分布 K-S p={ks_exp.pvalue:.3f}, 对数正态 K-S p={ks_logn.pvalue:.3f}"
        )
        print(f"  ➤ 拟合结果：{stats_summary[y_section]['最优分布']} 分布\n")

    return stats_summary


# ---------------- 测试模块 ----------------
if __name__ == "__main__":
    from data_loader import load_ngsim_data
    from section_analysis import compute_section_crossings

    df = load_ngsim_data(
        r"C:\Users\31078\Desktop\ngsim-traffic-analysis\data\NGSIM\US-101-Main-Data\vehicle-trajectory-data\0820am-0835am\trajectories-0820am-0835am.txt"
    )
    df_lane = df[df["Lane ID"] == 2]
    sections = [200, 400, 600]
    results = compute_section_crossings(df_lane, sections)
    stats_summary = analyze_headways(results)

    print("\n🧾 全部断面统计结果：")
    print(pd.DataFrame(stats_summary).T.round(3))
