import os
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

# Set clean publication style
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['font.size'] = 10
plt.rcParams['mathtext.fontset'] = 'cm'

# ==============================================================================
# FIGURE 4: PARETO FRONTIER CHART (Version 4.0 - Synchronized with Table II)
# ==============================================================================
fig, ax1 = plt.subplots(figsize=(8.5, 5.2), dpi=300)

paradigms = ['Pure Local RAG', 'Naive Static RAG', 'Pure Web RAG', 'Proposed Agentic RAG']
costs = [0.00, 2.50, 5.00, 0.90]                  # Marginal API Cost ($ / 1k queries)
faithfulness = [52.0, 55.0, 48.0, 62.0]           # Faithfulness Score (%)
relevance = [61.0, 65.0, 68.0, 73.0]              # Answer Relevance (%)
latencies = [1.12, 2.10, 3.45, 1.85]              # First-Token Latency (seconds)

colors = ['#3498db', '#9b59b6', '#e74c3c', '#2ecc71']

# Bubble size proportional to First-Token Latency
sizes = [l * 120 for l in latencies]
scatter = ax1.scatter(costs, faithfulness, s=sizes, c=colors, alpha=0.9, edgecolors='black', linewidth=1.5, zorder=5)

# Annotate points with exact values matching Table II
annotations = [
    (0.00, 52.0, 0.18, 1.2, "Pure Local RAG\n(Cost: $0.00, Faith: 52.0%, Rel: 61.0%)"),
    (2.50, 55.0, 0.18, 1.2, "Naive Static RAG\n(Cost: $2.50, Faith: 55.0%, Rel: 65.0%)"),
    (5.00, 48.0, -1.85, 1.8, "Pure Web RAG\n(Cost: $5.00, Faith: 48.0%, Rel: 68.0%)"),
    (0.90, 62.0, -0.65, 1.6, "Proposed Agentic RAG\n(Cost: $0.90, Faith: 62.0%, Rel: 73.0%)")
]

for x, y, ox, oy, text in annotations:
    ax1.annotate(text, (x, y), xytext=(x + ox, y + oy),
                 fontsize=9.5, fontweight='bold', color='#2c3e50',
                 arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0.15', color='#7f8c8d', lw=1.2))

# Pareto frontier connecting Pure Local ($0.00, 52.0%) to Proposed Agentic RAG ($0.90, 62.0%)
pareto_x = [0.00, 0.90]
pareto_y = [52.0, 62.0]
ax1.plot(pareto_x, pareto_y, '--', color='#27ae60', linewidth=2.5, label='Pareto Frontier (Optimal Trade-off Curve)', zorder=4)

ax1.set_xlabel('Marginal API Cost ($ / 1,000 Queries)', fontsize=11, fontweight='bold', labelpad=10)
ax1.set_ylabel('Faithfulness Score (%)', fontsize=11, fontweight='bold', labelpad=10)
ax1.set_title('Fig. 4: Pareto Efficiency Frontier (Faithfulness vs Marginal Cost vs Latency)', fontsize=12, fontweight='bold', pad=15)

ax1.set_xlim(-0.4, 5.8)
ax1.set_ylim(44, 68)
ax1.grid(True, linestyle='--', alpha=0.6)
ax1.legend(loc='lower right', frameon=True, facecolor='white', edgecolor='#bdc3c7', fontsize=9.5)

plt.tight_layout()

# Save to both target directories to guarantee availability
script_dir = os.path.dirname(os.path.abspath(__file__))
target_images_dir = os.path.join(script_dir, "science_paper_images")
os.makedirs(target_images_dir, exist_ok=True)

path1 = os.path.join(target_images_dir, "fig4_pareto_chart.png")
path2 = os.path.join(script_dir, "fig4_pareto_chart.png")

plt.savefig(path1, dpi=300)
plt.savefig(path2, dpi=300)
plt.close()

print(f"Successfully generated and saved Fig 4 to:\n- {path1}\n- {path2}")
