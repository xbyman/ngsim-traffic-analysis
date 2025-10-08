"""
section_analysis.py
-------------------
模块功能：
对选定车道进行断面分析，计算每辆车的过断面时间与车头时距。
"""

import pandas as pd  # 数据处理库，用于 DataFrame 操作
import numpy as np  # 数值计算库，用于数组与数学运算


def compute_section_crossings(df_lane, sections):
    results = {}

    for y_section in sections:
        arrivals = []

        for vid, g in df_lane.groupby("Vehicle ID"):
            g = g.sort_values("Frame ID")
            y = g["Local Y"].values
            t = g["Frame ID"].values

            for i in range(1, len(g)):
                if (y[i - 1] < y_section <= y[i]) or (y[i - 1] > y_section >= y[i]):
                    alpha = (y_section - y[i - 1]) / (y[i] - y[i - 1])
                    t_cross = t[i - 1] + alpha * (t[i] - t[i - 1])
                    arrivals.append({"Vehicle ID": vid, "过断面时间(s)": t_cross})

        # ✅ 这三行要放到“每个断面”循环内部
        arr_df = pd.DataFrame(arrivals)
        arr_df = arr_df.sort_values("过断面时间(s)").reset_index(drop=True)
        arr_df["车头时距(s)"] = arr_df["过断面时间(s)"].diff()

        results[y_section] = arr_df  # ✅ 在 for y_section 内存储结果

    return results


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
    print(
        f"车道 {lane_id} 的 Local Y 范围：{df_lane['Local Y'].min():.2f} ~ {df_lane['Local Y'].max():.2f}"
    )
    print(f"断面列表：{sections}")

    # 打印其中一个断面的前几行
    print("✅ 断面 400 ft 结果预览：")
    print(results[400].head(10))
