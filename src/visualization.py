"""
visualization.py
----------------
模块功能：
集中展示与保存各断面分析结果，包括：
- 车头时距分布
- 到达分布（泊松拟合）
- 流量与速度变化趋势
"""

import os
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

plt.rcParams["font.sans-serif"] = ["SimHei"]
plt.rcParams["axes.unicode_minus"] = False


def save_plot(fig, filename, folder="results"):
    """保存图像到 results 文件夹"""
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, filename)
    fig.savefig(path, dpi=300, bbox_inches="tight")
    print(f"✅ 已保存图像：{path}")


def plot_headway_distribution(results):
    """绘制并保存车头时距分布图"""
    for y_section, arr_df in results.items():
        headways = arr_df["车头时距(s)"].dropna()
        if len(headways) == 0:
            continue

        fig, ax = plt.subplots(figsize=(7, 4))
        sns.histplot(
            headways,
            bins=50,
            kde=True,
            color="skyblue",
            edgecolor="black",
            alpha=0.7,
            ax=ax,
        )
        ax.set_xlabel("车头时距 (s)")
        ax.set_ylabel("频数")
        ax.set_title(f"断面 {y_section} ft 的车头时距分布")
        ax.grid(alpha=0.3)
        plt.tight_layout()

        save_plot(fig, f"headway_distribution_{y_section}ft.png")
        plt.close(fig)


def plot_flow_speed(flow_stats):
    """绘制并保存流量与速度曲线图"""
    for y_section, df_out in flow_stats.items():
        fig, ax1 = plt.subplots(figsize=(8, 4))

        ax1.plot(
            df_out["时间窗起点(s)"],
            df_out["流量(veh/h)"],
            color="tab:blue",
            label="流量 (veh/h)",
        )
        ax1.set_xlabel("时间 (s)")
        ax1.set_ylabel("流量 (veh/h)", color="tab:blue")
        ax1.tick_params(axis="y", labelcolor="tab:blue")

        ax2 = ax1.twinx()
        ax2.plot(
            df_out["时间窗起点(s)"],
            df_out["时间平均速度(ft/s)"],
            color="tab:green",
            label="时间均速 (ft/s)",
        )
        ax2.plot(
            df_out["时间窗起点(s)"],
            df_out["空间平均速度(ft/s)"],
            color="tab:red",
            label="空间均速 (ft/s)",
        )
        ax2.set_ylabel("速度 (ft/s)", color="tab:red")
        ax2.tick_params(axis="y", labelcolor="tab:red")

        fig.suptitle(f"断面 {y_section} ft 的流量与速度变化", fontsize=12)
        fig.legend(loc="upper right")
        fig.tight_layout()

        save_plot(fig, f"flow_speed_{y_section}ft.png")
        plt.close(fig)


def plot_summary(flow_stats):
    """绘制多断面的总体对比图"""
    summary_data = []
    for y_section, df_out in flow_stats.items():
        avg_q = df_out["流量(veh/h)"].mean()
        avg_vt = df_out["时间平均速度(ft/s)"].mean()
        avg_vs = df_out["空间平均速度(ft/s)"].mean()
        summary_data.append([y_section, avg_q, avg_vt, avg_vs])

    df_summary = pd.DataFrame(
        summary_data,
        columns=[
            "断面位置(ft)",
            "平均流量(veh/h)",
            "平均时间均速(ft/s)",
            "平均空间均速(ft/s)",
        ],
    )

    fig, ax1 = plt.subplots(figsize=(8, 4))
    ax1.bar(
        df_summary["断面位置(ft)"],
        df_summary["平均流量(veh/h)"],
        color="skyblue",
        width=50,
        label="平均流量 (veh/h)",
    )
    ax2 = ax1.twinx()
    ax2.plot(
        df_summary["断面位置(ft)"],
        df_summary["平均空间均速(ft/s)"],
        color="red",
        marker="o",
        label="平均空间均速 (ft/s)",
    )

    ax1.set_xlabel("断面位置 (ft)")
    ax1.set_ylabel("平均流量 (veh/h)", color="tab:blue")
    ax2.set_ylabel("平均空间均速 (ft/s)", color="tab:red")
    fig.suptitle("各断面平均流量与空间均速对比")
    fig.legend(loc="upper right")

    save_plot(fig, "summary_flow_speed.png")
    plt.close(fig)


if __name__ == "__main__":
    from data_loader import load_ngsim_data
    from section_analysis import compute_section_crossings
    from flow_speed_analysis import compute_flow_speed

    df = load_ngsim_data(
        r"C:\Users\31078\Desktop\ngsim-traffic-analysis\data\NGSIM\US-101-Main-Data\vehicle-trajectory-data\0820am-0835am\trajectories-0820am-0835am.txt"
    )
    df_lane = df[df["Lane ID"] == 2]
    sections = [200, 400, 600]
    results = compute_section_crossings(df_lane, sections)
    flow_stats = compute_flow_speed(results, df_lane)

    from visualization import plot_headway_distribution, plot_flow_speed, plot_summary

    plot_headway_distribution(results)
    plot_flow_speed(flow_stats)
    plot_summary(flow_stats)
