"""
main.py
-------
项目主入口文件：
统一调度各功能模块，完成完整的交通流断面分析流程。
"""

import os  # 操作系统接口，用于创建目录与路径拼接
import datetime  # 时间与日期处理模块，用于生成报告时间戳
from src.data_loader import load_ngsim_data  # 从 data_loader 导入数据加载函数
from src.section_analysis import compute_section_crossings  # 导入断面穿越计算函数
from src.headway_analysis import analyze_headways  # 导入车头时距分析函数
from src.arrival_analysis import (
    compute_arrival_counts,
    fit_and_plot_distribution,
)  # 导入到达统计和拟合绘图函数
from src.flow_speed_analysis import compute_flow_speed  # 导入流量与速度计算函数
from src.visualization import (
    plot_headway_distribution,
    plot_flow_speed,
    plot_summary,
)  # 导入可视化函数


def save_summary_report(
    headway_stats, poisson_results, flow_stats, lane_id, sections, window_s
):
    """生成并保存交通流分析汇总报告。将各分析结果写入 results/summary_report.txt 中。"""
    os.makedirs("results", exist_ok=True)  # 确保 results 目录存在（若不存在则创建）
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # 获取当前时间字符串
    path = os.path.join("results", "summary_report.txt")  # 报告文件路径

    with open(path, "w", encoding="utf-8") as f:  # 以 UTF-8 写模式打开报告文件
        f.write("NGSIM 交通流分析报告\n")  # 写入报告标题
        f.write("-" * 50 + "\n")  # 写入分隔线
        f.write(f"生成时间：{now}\n")  # 写入生成时间
        f.write(f"分析车道：{lane_id}\n")  # 写入分析的车道 ID
        f.write(f"分析断面：{', '.join(map(str, sections))}\n")  # 写入断面列表
        f.write(f"时间窗：{window_s} 秒\n\n")  # 写入时间窗信息并换行

        # 写入车头时距结果
        f.write("【车头时距统计】\n")  # 分节标题：车头时距
        for sec, val in headway_stats.items():  # 遍历每个断面的车头时距统计
            f.write(
                f"断面 {sec} ft: 平均={val['平均车头时距(s)']:.2f}s, "
                f"标准差={val['标准差(s)']:.2f}s, CV={val['变异系数(CV)']:.2f}\n"
            )  # 写入该断面的统计指标
        f.write("\n")  # 空行分隔

        # 写入泊松检验结果
        f.write("【到达分布泊松检验】\n")  # 分节标题：泊松检验
        for sec, res in poisson_results.items():  # 遍历泊松检验结果字典
            f.write(
                f"断面 {sec} ft: χ²={res['chi2']:.2f}, p={res['p']:.3f} → {res['结论']}\n"
            )  # 写入检验统计量与结论
        f.write("\n")  # 空行分隔

        # 写入流量速度结果
        f.write("【平均流量与速度】\n")  # 分节标题：平均流量与速度
        for sec, df in flow_stats.items():  # 遍历流量速度结果（每个断面对应 DataFrame）
            avg_q = df["流量(veh/h)"].mean()  # 计算平均流量
            avg_vt = df["时间平均速度(ft/s)"].mean()  # 计算时间平均速度
            avg_vs = df["空间平均速度(ft/s)"].mean()  # 计算空间平均速度
            f.write(
                f"断面 {sec} ft: 平均流量={avg_q:.1f} veh/h, "
                f"时间均速={avg_vt:.1f} ft/s, 空间均速={avg_vs:.1f} ft/s\n"
            )  # 写入该断面的速度与流量统计
        f.write("\n✅ 图像文件已保存到 results/ 目录。\n")  # 写入结尾提示

    print(f"📝 已生成汇总报告：{path}")  # 在控制台打印报告生成路径


def main():
    data_path = (
        r"C:\Users\31078\Desktop\ngsim-traffic-analysis\data"
        r"\NGSIM\US-101-Main-Data\vehicle-trajectory-data\0820am-0835am\trajectories-0820am-0835am.txt"
    )  # 数据文件的绝对路径（原始 NGSIM 轨迹数据）
    lane_id = 2  # 要分析的车道 ID
    sections = [200, 400, 600]  # 要分析的断面位置（单位 ft）
    window_s = 10  # 时间窗大小（秒）

    print("🚀 开始交通流分析流程...")  # 起始提示信息
    df = load_ngsim_data(data_path)  # 加载数据文件，返回 DataFrame
    df_lane = df[df["Lane ID"] == lane_id]  # 按车道筛选出感兴趣的数据

    results = compute_section_crossings(
        df_lane, sections
    )  # 计算每辆车通过各断面的时间点
    headway_stats = analyze_headways(results)  # 分析各断面的车头时距并返回统计
    counts_by_section = compute_arrival_counts(
        results, window_s=window_s
    )  # 统计每窗到达辆数

    # 绘制并查看拟合图（此处不捕获返回值）
    fit_and_plot_distribution(counts_by_section)  # 拟合泊松分布并绘图对比

    flow_stats = compute_flow_speed(
        results, df_lane, window_s=window_s
    )  # 计算流量与速度统计

    plot_headway_distribution(results)  # 绘制车头时距分布图
    plot_flow_speed(flow_stats)  # 绘制流量-速度图
    plot_summary(flow_stats)  # 绘制汇总视图

    # 再次计算并获取泊松检验结果（用于报告保存）
    counts_by_section = compute_arrival_counts(
        results, window_s=window_s
    )  # 重新统计以确保一致
    poisson_results = fit_and_plot_distribution(
        counts_by_section
    )  # 获取泊松检验结果字典

    save_summary_report(
        headway_stats, poisson_results, flow_stats, lane_id, sections, window_s
    )  # 保存汇总报告到 results/summary_report.txt

    print("🏁 全部分析完成！")  # 完成提示


if __name__ == "__main__":
    main()  # 作为脚本直接运行时执行 main()
