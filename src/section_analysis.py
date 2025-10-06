"""
section_analysis.py
-------------------
模块功能：
对选定车道进行断面分析，计算每辆车的过断面时间与车头时距。
"""

import pandas as pd  # 数据处理库，用于 DataFrame 操作
import numpy as np  # 数值计算库，用于数组与数学运算


def compute_section_crossings(df_lane, sections):
    """
    计算各断面的车辆过车时间与车头时距。

    参数：
        df_lane (DataFrame): 指定车道的数据（已筛选好 Lane ID）
        sections (list): 要分析的断面位置（单位 ft）

    返回：
        results (dict): key=断面位置, value=该断面的 DataFrame
    """
    results = {}  # 用于保存每个断面的到达记录 DataFrame

    for y_section in sections:  # 遍历每个待分析的断面位置
        arrivals = []  # 存储该断面下所有车辆的过断面时间（后续转换为 DataFrame）

        # 遍历每一辆车的轨迹数据以检测是否经过该断面
        for vid, g in df_lane.groupby("Vehicle ID"):
            g = g.sort_values("Frame ID")  # 按时间排序该车辆轨迹点
            y = g["Local Y"].values  # 该车辆的 y 坐标序列
            t = g["Frame ID"].values  # 该车辆对应的时间序列（秒）

            # 遍历相邻两个轨迹点，检测是否跨越断面（由 y 值变化判断）
            for i in range(1, len(g)):
                if (y[i - 1] < y_section <= y[i]) or (y[i - 1] > y_section >= y[i]):
                    # 若跨过断面，使用线性插值估计更精确的过断面时间
                    alpha = (y_section - y[i - 1]) / (y[i] - y[i - 1])
                    t_cross = t[i - 1] + alpha * (
                        t[i] - t[i - 1]
                    )  # 插值得到的时间（秒）
                    arrivals.append(
                        {"Vehicle ID": vid, "过断面时间(s)": t_cross}
                    )  # 记录通过事件

    # 将记录列表转换为 DataFrame 并按时间排序
    arr_df = pd.DataFrame(arrivals)  # 转换为 DataFrame

    # 按过断面时间排序并计算相邻车辆时间差作为车头时距
    arr_df = arr_df.sort_values("过断面时间(s)").reset_index(drop=True)
    arr_df["车头时距(s)"] = arr_df["过断面时间(s)"].diff()  # 计算车头时距

    results[y_section] = arr_df  # 保存该断面的 DataFrame 到结果字典

    return results  # 返回字典：key=断面位置，value=对应 DataFrame（含过断面时间与车头时距）


# 测试模块：单独运行时执行
if __name__ == "__main__":
    from data_loader import load_ngsim_data

    # 加载数据
    df = load_ngsim_data(
        r"C:\Users\31078\Desktop\ngsim-traffic-analysis\data\NGSIM\US-101-Main-Data\vehicle-trajectory-data\0820am-0835am\trajectories-0820am-0835am.txt"
    )

    # 选择车道
    lane_id = 2
    df_lane = df[df["Lane ID"] == lane_id]

    # 断面列表
    sections = [200, 400, 600]

    # 计算结果
    results = compute_section_crossings(df_lane, sections)

    # 打印其中一个断面的前几行
    print("✅ 断面 400 ft 结果预览：")
    print(results[400].head(10))
