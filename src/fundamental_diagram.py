"""
fundamental_diagram.py
---------------------
模块功能：
计算并绘制交通流三要素（流量 q、密度 k、速度 v）的基本关系图，
并拟合 Greenshields 模型以生成平滑曲线。
输出：
    1. 流量–密度关系 (q–k)
    2. 速度–密度关系 (v–k)
    3. 流量–速度关系 (q–v)
"""

import os
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit

plt.rcParams["font.sans-serif"] = ["SimHei"]
plt.rcParams["axes.unicode_minus"] = False


# ===================== 计算密度 =====================
def compute_density(flow_stats):
    """
    根据流量与空间平均速度计算密度。
    参数：
        flow_stats (dict): 每个断面的流量与速度统计结果
    返回：
        density_stats (dict): 含密度数据的 DataFrame 字典
    """
    density_stats = {}
    for sec, df in flow_stats.items():
        df = df.copy()
        df["密度(veh/mi)"] = df["流量(veh/h)"] / (df["空间平均速度(ft/s)"] * 0.6818)
        density_stats[sec] = df
        print(f"✅ 断面 {sec} ft：平均密度 = {df['密度(veh/mi)'].mean():.2f} veh/mi")
    return density_stats


# ===================== 绘制基本关系散点图 =====================
def plot_fundamental_diagrams(density_stats):
    """绘制三张基本关系散点图并保存"""
    os.makedirs("results", exist_ok=True)

    # 1️⃣ 流量–密度 (q–k)
    plt.figure(figsize=(7, 5))
    for sec, df in density_stats.items():
        plt.scatter(df["密度(veh/mi)"], df["流量(veh/h)"], label=f"{sec} ft", alpha=0.7)
    plt.xlabel("密度 k (veh/mi)")
    plt.ylabel("流量 q (veh/h)")
    plt.title("流量–密度关系 (q–k)")
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig("results/fundamental_qk.png", dpi=300)
    print("✅ 已保存图像：results/fundamental_qk.png")

    # 2️⃣ 速度–密度 (v–k)
    plt.figure(figsize=(7, 5))
    for sec, df in density_stats.items():
        plt.scatter(
            df["密度(veh/mi)"],
            df["空间平均速度(ft/s)"] * 0.6818,
            label=f"{sec} ft",
            alpha=0.7,
        )
    plt.xlabel("密度 k (veh/mi)")
    plt.ylabel("速度 v (mph)")
    plt.title("速度–密度关系 (v–k)")
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig("results/fundamental_vk.png", dpi=300)
    print("✅ 已保存图像：results/fundamental_vk.png")

    # 3️⃣ 流量–速度 (q–v)
    plt.figure(figsize=(7, 5))
    for sec, df in density_stats.items():
        plt.scatter(
            df["空间平均速度(ft/s)"] * 0.6818,
            df["流量(veh/h)"],
            label=f"{sec} ft",
            alpha=0.7,
        )
    plt.xlabel("速度 v (mph)")
    plt.ylabel("流量 q (veh/h)")
    plt.title("流量–速度关系 (q–v)")
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig("results/fundamental_qv.png", dpi=300)
    print("✅ 已保存图像：results/fundamental_qv.png")
    plt.show()


# ===================== Greenshields 拟合曲线 =====================
def greenshields(k, vf, kj):
    """Greenshields 模型：v = vf * (1 - k/kj)"""
    return vf * (1 - k / kj)


def fit_and_plot_greenshields(density_stats):
    """
    对每个断面拟合 Greenshields 模型并绘制速度–密度曲线。
    同时生成理论流量–密度曲线。
    """
    os.makedirs("results", exist_ok=True)

    # 速度–密度拟合图
    plt.figure(figsize=(8, 6))
    for sec, df in density_stats.items():
        k = df["密度(veh/mi)"].values
        v = df["空间平均速度(ft/s)"].values * 0.6818
        mask = (k > 0) & (k < 200) & (v > 0)
        k, v = k[mask], v[mask]

        if len(k) < 5:
            continue

        try:
            popt, _ = curve_fit(greenshields, k, v, p0=[70, 150])
            vf, kj = popt
            k_fit = np.linspace(0, max(k), 100)
            v_fit = greenshields(k_fit, vf, kj)
            plt.scatter(k, v, s=15, alpha=0.5, label=f"{sec} ft 实测")
            plt.plot(
                k_fit,
                v_fit,
                lw=2,
                label=f"{sec} ft 拟合曲线 (v_f={vf:.1f}, k_j={kj:.1f})",
            )
        except RuntimeError:
            plt.scatter(k, v, s=15, alpha=0.5, label=f"{sec} ft (拟合失败)")

    plt.xlabel("密度 k (veh/mi)")
    plt.ylabel("速度 v (mph)")
    plt.title("Greenshields 速度–密度拟合曲线")
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig("results/fundamental_greenshields_vk.png", dpi=300)
    print("✅ 已保存拟合图：results/fundamental_greenshields_vk.png")

    # 理论流量–密度曲线
    plt.figure(figsize=(8, 6))
    for sec, df in density_stats.items():
        k = df["密度(veh/mi)"].values
        v = df["空间平均速度(ft/s)"].values * 0.6818
        mask = (k > 0) & (k < 200) & (v > 0)
        k, v = k[mask], v[mask]
        if len(k) < 5:
            continue
        try:
            popt, _ = curve_fit(greenshields, k, v, p0=[70, 150])
            vf, kj = popt
            k_fit = np.linspace(0, kj, 100)
            q_fit = k_fit * greenshields(k_fit, vf, kj)
            plt.scatter(k, k * v, s=15, alpha=0.5, label=f"{sec} ft 实测")
            plt.plot(
                k_fit,
                q_fit,
                lw=2,
                label=f"{sec} ft 拟合曲线 (v_f={vf:.1f}, k_j={kj:.1f})",
            )
        except RuntimeError:
            plt.scatter(k, k * v, s=15, alpha=0.5, label=f"{sec} ft (拟合失败)")

    plt.xlabel("密度 k (veh/mi)")
    plt.ylabel("流量 q (veh/h)")
    plt.title("Greenshields 理论流量–密度曲线")
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig("results/fundamental_greenshields_qk.png", dpi=300)
    print("✅ 已保存拟合图：results/fundamental_greenshields_qk.png")
    plt.show()


# 🧪 模块测试（单独运行）
if __name__ == "__main__":
    from src.data_loader import load_ngsim_data
    from src.section_analysis import compute_section_crossings
    from src.flow_speed_analysis import compute_flow_speed

    df = load_ngsim_data(
        r"C:\Users\31078\Desktop\ngsim-traffic-analysis\data\NGSIM\US-101-Main-Data\vehicle-trajectory-data\0820am-0835am\trajectories-0820am-0835am.txt"
    )
    df_lane = df[df["Lane ID"] == 2]
    sections = [200, 400, 600]

    results = compute_section_crossings(df_lane, sections)
    flow_stats = compute_flow_speed(results, df_lane, window_s=10)

    density_stats = compute_density(flow_stats)
    plot_fundamental_diagrams(density_stats)
    fit_and_plot_greenshields(density_stats)
