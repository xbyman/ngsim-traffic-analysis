"""
main.py
-------
项目主入口文件：
统一调度各功能模块，完成完整的交通流断面分析流程。
"""

import os
import datetime
from src.data_loader import load_ngsim_data
from src.section_analysis import compute_section_crossings
from src.headway_analysis import analyze_headways  # ✅ 已包含分布检验结果
from src.arrival_analysis import compute_arrival_counts, fit_and_plot_distribution
from src.flow_speed_analysis import compute_flow_speed
from src.visualization import plot_headway_distribution, plot_flow_speed, plot_summary
from src.trajectory_plot import plot_space_time


def save_summary_report(
    headway_stats, poisson_results, flow_stats, lane_id, sections, window_s
):
    """生成并保存交通流分析汇总报告，包含车头时距分布检验结果。"""
    os.makedirs("results", exist_ok=True)
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    path = os.path.join("results", "summary_report.txt")

    with open(path, "w", encoding="utf-8") as f:
        f.write("NGSIM 交通流分析报告\n")
        f.write("-" * 50 + "\n")
        f.write(f"生成时间：{now}\n")
        f.write(f"分析车道：{lane_id}\n")
        f.write(f"分析断面：{', '.join(map(str, sections))}\n")
        f.write(f"时间窗：{window_s} 秒\n\n")

        # 【车头时距统计 + 分布检验】
        f.write("【车头时距统计与分布检验】\n")
        for sec, val in headway_stats.items():
            f.write(
                f"断面 {sec} ft:\n"
                f"  平均={val['平均车头时距(s)']:.2f}s, 标准差={val['标准差(s)']:.2f}s, CV={val['变异系数(CV)']:.2f}\n"
            )
            if "指数分布 p值" in val:
                f.write(
                    f"  指数分布 K-S p={val['指数分布 p值']:.3f}, "
                    f"对数正态分布 K-S p={val['对数正态 p值']:.3f}, "
                    f"最优分布={val['最优分布']} 分布\n"
                )
            f.write("\n")

        # 【到达分布泊松检验】
        f.write("【到达分布泊松检验】\n")
        for sec, res in poisson_results.items():
            f.write(
                f"断面 {sec} ft: χ²={res['chi2']:.2f}, p={res['p']:.3f} → {res['结论']}\n"
            )
        f.write("\n")

        # 【平均流量与速度】
        f.write("【平均流量与速度】\n")
        for sec, df in flow_stats.items():
            avg_q = df["流量(veh/h)"].mean()
            avg_vt = df["时间平均速度(ft/s)"].mean()
            avg_vs = df["空间平均速度(ft/s)"].mean()
            f.write(
                f"断面 {sec} ft: 平均流量={avg_q:.1f} veh/h, "
                f"时间均速={avg_vt:.1f} ft/s, 空间均速={avg_vs:.1f} ft/s\n"
            )
        f.write("\n✅ 图像文件已保存到 results/ 目录。\n")

    print(f"📝 已生成汇总报告：{path}")


def main():
    data_path = (
        r"C:\Users\31078\Desktop\ngsim-traffic-analysis\data"
        r"\NGSIM\US-101-Main-Data\vehicle-trajectory-data\0820am-0835am\trajectories-0820am-0835am.txt"
    )
    lane_id = 2
    sections = [200, 400, 600]
    window_s = 10

    print("🚀 开始交通流分析流程...")
    df = load_ngsim_data(data_path)
    df_lane = df[df["Lane ID"] == lane_id]

    results = compute_section_crossings(df_lane, sections)

    # ✅ 分析车头时距（带分布检验）
    headway_stats = analyze_headways(results)

    # 到达分布 + 泊松检验
    counts_by_section = compute_arrival_counts(results, window_s=window_s)
    poisson_results = fit_and_plot_distribution(counts_by_section)

    # 流量与速度
    flow_stats = compute_flow_speed(results, df_lane, window_s=window_s)

    # 绘图
    plot_headway_distribution(results)
    plot_flow_speed(flow_stats)
    plot_summary(flow_stats)

    print("🎬 绘制车道时空轨迹图中...")
    plot_space_time(
        df, lane_id=lane_id, save_path=f"results/space_time_lane{lane_id}.png"
    )

    # ✅ 生成汇总报告（含分布检验）
    save_summary_report(
        headway_stats, poisson_results, flow_stats, lane_id, sections, window_s
    )

    print("🏁 全部分析完成！")


if __name__ == "__main__":
    main()
