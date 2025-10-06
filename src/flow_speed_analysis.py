"""
flow_speed_analysis.py
----------------------
模块功能：
计算各断面在每个时间窗内的流量、时间平均速度、空间平均速度。
"""

import pandas as pd  # 数据处理库
import numpy as np  # 数值计算库
import matplotlib.pyplot as plt  # 绘图库

plt.rcParams["font.sans-serif"] = ["SimHei"]  # 设置中文字体
plt.rcParams["axes.unicode_minus"] = False  # 修复负号显示问题


def compute_flow_speed(results, df_lane, window_s=10):
    """
    计算流量、时间平均速度、空间平均速度。

    参数：
        results (dict): section_analysis 的输出结果 (断面过车时间)
        df_lane (DataFrame): 当前车道的数据
        window_s (float): 时间窗大小（秒）

    返回：
        flow_stats (dict): 每个断面的流量与速度统计表
    """
    flow_stats = {}  # 保存每个断面的流量与速度统计表

    for y_section, arr_df in results.items():  # 遍历每个断面
        # 提取该断面的过断面时间数组
        times = arr_df["过断面时间(s)"].values
        if len(times) == 0:  # 若无数据则跳过
            continue

        # 确定时间窗边界，保证覆盖所有过车时间
        t_min, t_max = times.min(), times.max()
        t0 = np.floor(t_min / window_s) * window_s
        t1 = np.ceil(t_max / window_s) * window_s
        bins = np.arange(t0, t1 + window_s, window_s)  # 生成窗口左边界序列

        # 为每个车辆匹配其在 df_lane 中的平均速度（作为代表值）
        speed_map = {}
        for vid in arr_df["Vehicle ID"].unique():
            v = df_lane[df_lane["Vehicle ID"] == vid]["Vehicle Velocity"].mean()
            speed_map[vid] = v  # 存储车辆平均速度

        # 计算每个时间窗的指标并收集到 data 列表
        data = []
        for b in bins[:-1]:  # 对每个时间窗（左边界 b）进行统计
            in_window = arr_df[
                (arr_df["过断面时间(s)"] >= b)
                & (arr_df["过断面时间(s)"] < b + window_s)
            ]  # 选取落在该时间窗内的车辆记录

            if len(in_window) == 0:  # 若该窗没有车辆，则记录空值
                data.append(
                    {
                        "时间窗起点(s)": b,
                        "流量(veh/h)": 0,
                        "时间平均速度(ft/s)": np.nan,
                        "空间平均速度(ft/s)": np.nan,
                    }
                )
                continue

            # 流量计算(veh/h) = 窗内车辆数 * 3600 / 窗大小(秒)
            q = len(in_window) * (3600 / window_s)

            # 时间平均速度(算术平均)
            time_mean_v = np.mean([speed_map[vid] for vid in in_window["Vehicle ID"]])

            # 空间平均速度(调和平均)：len / sum(1/v)
            space_mean_v = len(in_window) / np.sum(
                1.0 / np.array([speed_map[vid] for vid in in_window["Vehicle ID"]])
            )

            data.append(
                {
                    "时间窗起点(s)": b,
                    "流量(veh/h)": q,
                    "时间平均速度(ft/s)": time_mean_v,
                    "空间平均速度(ft/s)": space_mean_v,
                }
            )  # 将该窗的统计加入 data

        df_out = pd.DataFrame(data)  # 转为 DataFrame 以便展示与保存
        flow_stats[y_section] = df_out  # 保存该断面的统计表

        # 绘制流量与速度随时间变化曲线
        plt.figure(figsize=(8, 4))
        plt.plot(
            df_out["时间窗起点(s)"],
            df_out["流量(veh/h)"],
            label="流量 (veh/h)",
            color="tab:blue",
        )
        plt.plot(
            df_out["时间窗起点(s)"],
            df_out["时间平均速度(ft/s)"],
            label="时间平均速度 (ft/s)",
            color="tab:green",
        )
        plt.plot(
            df_out["时间窗起点(s)"],
            df_out["空间平均速度(ft/s)"],
            label="空间平均速度 (ft/s)",
            color="tab:red",
        )
        plt.xlabel("时间 (s)")  # x 轴为时间（秒）
        plt.ylabel("指标值")  # y 轴为指标值（流量或速度）
        plt.title(f"断面 {y_section} ft 的流量与速度变化")  # 图表标题
        plt.legend()  # 显示图例
        plt.grid(alpha=0.3)  # 添加网格
        plt.tight_layout()  # 自动调整布局
        plt.show()  # 显示图形

        # 打印前几行结果供检查
        print(f"\n断面 {y_section} ft 的流量与速度统计：")
        print(df_out.head(5))

    return flow_stats  # 返回包含每个断面统计 DataFrame 的字典


# 测试模块
if __name__ == "__main__":
    from data_loader import load_ngsim_data
    from section_analysis import compute_section_crossings

    df = load_ngsim_data(
        r"C:\Users\31078\Desktop\ngsim-traffic-analysis\data\NGSIM\US-101-Main-Data\vehicle-trajectory-data\0820am-0835am\trajectories-0820am-0835am.txt"
    )
    df_lane = df[df["Lane ID"] == 2]
    sections = [200, 400, 600]
    results = compute_section_crossings(df_lane, sections)

    compute_flow_speed(results, df_lane)
