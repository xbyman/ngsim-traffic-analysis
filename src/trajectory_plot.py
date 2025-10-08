"""
trajectory_plot.py
-------------------
模块功能：
绘制指定车道的车辆时空轨迹图（Space-Time Diagram）。

输入：
    DataFrame（包含至少 Frame ID、Local Y、Lane ID、Vehicle ID）

输出：
    可视化时空图（支持保存至 results/ 文件夹）
"""

import os
import matplotlib.pyplot as plt
import pandas as pd


plt.rcParams["font.sans-serif"] = ["SimHei"]  # 中文显示
plt.rcParams["axes.unicode_minus"] = False  # 正常显示负号


def plot_space_time(df: pd.DataFrame, lane_id: int, save_path: str = None):
    """
    绘制指定车道的车辆时空轨迹图。

    参数：
        df (pd.DataFrame): NGSIM数据（需包含 "Frame ID", "Local Y", "Lane ID", "Vehicle ID"）
        lane_id (int): 要绘制的车道编号
        save_path (str): 若提供路径，则保存图像，否则直接显示
    """
    # 过滤指定车道
    df_lane = df[df["Lane ID"] == lane_id]

    if df_lane.empty:
        print(f"⚠️ 未找到车道 {lane_id} 的数据。")
        return

    # 创建绘图
    plt.figure(figsize=(10, 6))
    for vid, g in df_lane.groupby("Vehicle ID"):
        plt.plot(g["Frame ID"], g["Local Y"], linewidth=0.4, alpha=0.5)

    # 坐标标签与标题
    plt.xlabel("时间 (s)")
    plt.ylabel("纵向位置 Y (ft)")
    plt.title(f"车道 {lane_id} 的车辆时空轨迹图")

    plt.grid(alpha=0.3)
    # save_plot(plt, f"space_time_lane{lane_id}.png", folder="results") # 默认保存

    # 保存或展示

    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
        plt.close()
        print(f"✅ 已保存图像：{save_path}")
    else:
        plt.show()


# 测试运行（可独立执行）
if __name__ == "__main__":
    from src.data_loader import load_ngsim_data

    df = load_ngsim_data(
        r"C:\Users\31078\Desktop\ngsim-traffic-analysis\data\NGSIM\US-101-Main-Data\vehicle-trajectory-data\0820am-0835am\trajectories-0820am-0835am.txt"
    )

    plot_space_time(
        df=df,
        lane_id=2,
        save_path=r"C:\Users\31078\Desktop\ngsim-traffic-analysis\results\space_time_lane2.png",
    )
