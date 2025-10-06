"""
data_loader.py
--------------
模块功能：
读取 NGSIM 轨迹数据文件，返回带列名的 DataFrame。
"""

import pandas as pd  # 数据处理库，用于读取与操作 DataFrame


def load_ngsim_data(path):
    """
    读取 NGSIM 数据文件。
    参数：
        path (str): 数据文件路径 (.txt)
    返回：
        df (DataFrame): 含标准列名的轨迹数据
    """
    col_names = [  # 指定输入文件的列名，匹配 NGSIM 原始数据字段顺序
        "Vehicle ID",
        "Frame ID",
        "Total Frames",
        "Global Time",
        "Local X",
        "Local Y",
        "Global X",
        "Global Y",
        "Vehicle Length",
        "Vehicle Width",
        "Vehicle Class",
        "Vehicle Velocity",
        "Vehicle Acceleration",
        "Lane ID",
        "Preceding Vehicle ID",
        "Following Vehicle ID",
        "Space Headway",
        "Time Headway",
        "Road Grade",
    ]

    # 读取数据
    df = pd.read_csv(path, sep=r"\s+", names=col_names)  # 按空白分隔读取并应用列名

    # 帧号转换为秒
    df["Frame ID"] *= 0.1  # 将 Frame ID（单位：0.1s）转换为秒

    return df


# 测试代码：仅在单独运行该文件时执行
if __name__ == "__main__":
    test_path = r"C:\Users\31078\Desktop\ngsim-traffic-analysis\data\NGSIM\US-101-Main-Data\vehicle-trajectory-data\0820am-0835am\trajectories-0820am-0835am.txt"
    df = load_ngsim_data(test_path)
    print("✅ 数据加载成功！")
    print(df.head())
