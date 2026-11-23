# -*- coding: utf-8 -*-
"""Tao cac hinh ve cho bai bao (so lieu lay tu log.txt - 7 kich ban, 1000 s)."""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

plt.rcParams["font.family"] = "Times New Roman"
plt.rcParams["font.size"] = 11
OUT = "figures"
os.makedirs(OUT, exist_ok=True)
NODES = [f"S{i}" for i in range(1, 11)]

# ---------------- So lieu theo nut (trich tu log.txt) ----------------
PDR = {
    "KB-0": [100, 100, 100, 100, 97.2, 97.2, 97.2, 97.2, 94.6, 94.6],
    "KB-1": [100, 97.1, 91.4, 97.7, 95.5, 95.5, 95.5, 88.9, 80.6, 73.0],
    "KB-2": [97.1, 97.1, 91.4, 86.0, 93.2, 88.6, 82.2, 72.2, 72.2, 70.3],
    "KB-3": [99.2, 87.9, 75.2, 81.3, 80.6, 56.9, 39.4, 13.9, 16.7, 13.5],
    "KB-4": [98.4, 92.1, 78.5, 33.8, 25.0, 10.3, 8.3, 10.9, 8.5, 8.3],
    "KB-5": [100, 100, 100, 94.3, 94.4, 94.4, 94.4, 86.1, 89.2, 91.9],
    "KB-6": [100, 80.6, 75.0, 38.0, 66.7, 11.7, 7.3, 8.3, 8.3, 8.3],
}
LAT = {
    "KB-0": [0.06, 3.14, 6.94, 10.58, 14.05, 18.15, 21.67, 25.31, 28.63, 32.50],
    "KB-1": [0.06, 4.33, 7.07, 22.10, 27.57, 33.95, 40.94, 57.90, 64.84, 73.58],
    "KB-2": [0.06, 3.24, 5.72, 20.15, 24.82, 31.04, 46.97, 62.31, 65.07, 69.10],
    "KB-5": [0.06, 3.55, None, 6.59, 10.64, 13.57, 17.62, 21.52, 24.76, 27.45],
}
TX = {
    "KB-0": [350, 315, 280, 245, 216, 180, 144, 108, 74, 37],
    "KB-3": [1261, 1159, 1044, 904, 688, 267, 201, 137, 105, 70],
    "KB-4": [746, 648, 532, 621, 600, 284, 232, 138, 115, 68],
}

# ---------------- Hinh 1: Topology ----------------
fig, ax = plt.subplots(figsize=(9, 3.6))
k = 0.22
ax.axvspan(175, 375, color="#f4c7a1", alpha=0.45, lw=0)
ax.text(275, 118, "Vùng sạt lở giả định (S4–S7)", ha="center", fontsize=10, color="#8a4b14")
xs = [0] + [50 * i for i in range(1, 11)]
ax.plot([-20, 520], [-20 * k, 520 * k], color="#8c7b6b", lw=1, ls=":")
for i in range(1, 11):
    x = 50 * i
    ax.add_patch(FancyArrowPatch((x - 6, x * k - 1.3), (x - 44, (x - 50) * k + 1.3),
                                 arrowstyle="-|>", mutation_scale=11, color="#1f4e79", lw=1.2))
for i in range(1, 11):
    x = 50 * i
    face = "#c00000" if i == 5 else "#2e75b6"
    ax.plot(x, x * k, "o", ms=13, color=face, mec="black", mew=0.6, zorder=3)
    ax.text(x, x * k - 13, f"S{i}", ha="center", fontsize=10)
ax.plot(0, 0, "s", ms=15, color="#548235", mec="black", mew=0.6, zorder=3)
ax.text(0, -13, "GW (S11)", ha="center", fontsize=10)
ax.add_patch(FancyArrowPatch((200, 200 * k + 5), (100, 100 * k + 5), connectionstyle="arc3,rad=0.45",
                             arrowstyle="-|>", mutation_scale=11, color="#7030a0", lw=1.2, ls="--"))
ax.text(150, 88, "Liên kết nối vòng 100 m\n(ví dụ: S4 → S2 khi S3 hỏng)", ha="center", fontsize=9, color="#7030a0")
ax.annotate("", xy=(450, 450 * k - 22), xytext=(500, 500 * k - 22),
            arrowprops=dict(arrowstyle="<->", color="black", lw=0.8))
ax.text(475, 450 * k - 33, "d = 50 m", ha="center", fontsize=9)
ax.text(255, 255 * k + 12, "điểm khởi phát", ha="left", fontsize=8.5, color="#c00000")
ax.set_xlim(-30, 530); ax.set_ylim(-40, 130)
ax.set_xlabel("Khoảng cách dọc tuyến tính từ trạm cổng (m)")
ax.set_yticks([]); ax.spines[["left", "top", "right"]].set_visible(False)
fig.tight_layout(); fig.savefig(f"{OUT}/fig1_topology.png", dpi=300); plt.close(fig)

# ---------------- Hinh 2: May trang thai ngu thich ung ----------------
fig, ax = plt.subplots(figsize=(9, 3.4))
ax.set_xlim(0, 10); ax.set_ylim(0, 4); ax.axis("off")
boxes = {"L0": (0.6, "#f8cbad", "Level 0 – Khẩn cấp\nT = 5 s (mô phỏng)\nT = 1 phút (thực địa)"),
         "L1": (3.9, "#ffe699", "Level 1 – Cảnh báo\nT = 15 s (mô phỏng)\nT = 5 phút (thực địa)"),
         "L2": (7.2, "#c5e0b4", "Level 2 – Ổn định\nT = 30 s (mô phỏng)\nT = 15 phút (thực địa)")}
for key, (x, c, t) in boxes.items():
    ax.add_patch(FancyBboxPatch((x, 1.45), 2.2, 1.1, boxstyle="round,pad=0.05", fc=c, ec="black", lw=0.8))
    ax.text(x + 1.1, 2.0, t, ha="center", va="center", fontsize=9.5)
def arr(p1, p2, rad, label, ly, lx=None):
    ax.add_patch(FancyArrowPatch(p1, p2, connectionstyle=f"arc3,rad={rad}", arrowstyle="-|>",
                                 mutation_scale=12, lw=1, color="black"))
    ax.text(lx if lx else (p1[0] + p2[0]) / 2, ly, label, ha="center", fontsize=8.8)
arr((2.85, 2.35), (3.85, 2.35), -0.35, "stable ≥ 3\nhoặc FLAG = 100", 3.0)
arr((6.15, 2.35), (7.15, 2.35), -0.35, "stable ≥ 6", 2.95)
arr((7.2, 1.55), (2.85, 1.55), -0.25, "FLAG = 255  hoặc  Δ ≥ θ  hoặc  nhận gói 255/150 (leo thang 60 s)", 0.35, 5.0)
arr((3.9, 1.6), (2.85, 1.6), 0.0, "", 1.0)
fig.tight_layout(); fig.savefig(f"{OUT}/fig2_sleep_fsm.png", dpi=300); plt.close(fig)

# ---------------- Hinh 3: PDR theo nut ----------------
fig, ax = plt.subplots(figsize=(8, 4.2))
markers = ["o", "s", "^", "D", "v", "P", "X"]
for (kb, v), m in zip(PDR.items(), markers):
    ax.plot(NODES, v, marker=m, ms=5, lw=1.3, label=kb)
ax.set_ylabel("PDR đầu-cuối (%)"); ax.set_xlabel("Nút nguồn (số chặng tới trạm cổng tăng dần)")
ax.set_ylim(0, 105); ax.grid(alpha=0.3); ax.legend(ncol=4, fontsize=9, loc="lower left")
fig.tight_layout(); fig.savefig(f"{OUT}/fig3_pdr_per_node.png", dpi=300); plt.close(fig)

# ---------------- Hinh 4: Do tre theo nut ----------------
fig, ax = plt.subplots(figsize=(8, 4.0))
for (kb, v), m in zip(LAT.items(), markers):
    xs_ = [n for n, y in zip(NODES, v) if y is not None]
    ys_ = [y for y in v if y is not None]
    ax.plot(xs_, ys_, marker=m, ms=5, lw=1.3, label=kb)
ax.set_ylabel("Độ trễ đầu-cuối trung bình (s)"); ax.set_xlabel("Nút nguồn")
ax.grid(alpha=0.3); ax.legend(fontsize=9)
fig.tight_layout(); fig.savefig(f"{OUT}/fig4_latency_per_node.png", dpi=300); plt.close(fig)

# ---------------- Hinh 5: So lan phat theo nut ----------------
fig, ax = plt.subplots(figsize=(8, 4.0))
w = 0.27
for j, (kb, v) in enumerate(TX.items()):
    ax.bar([i + (j - 1) * w for i in range(10)], v, width=w, label=kb)
ax.set_xticks(range(10)); ax.set_xticklabels(NODES)
ax.set_ylabel("Số lần phát vật lý [TX]"); ax.set_xlabel("Nút")
ax.grid(axis="y", alpha=0.3); ax.legend(fontsize=9)
fig.tight_layout(); fig.savefig(f"{OUT}/fig5_tx_per_node.png", dpi=300); plt.close(fig)
print("Figures saved to", OUT)
