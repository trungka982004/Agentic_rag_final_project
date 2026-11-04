import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Ensure science_paper_assets directory exists
os.makedirs("science_paper_assets", exist_ok=True)

plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['font.size'] = 9.5
plt.rcParams['mathtext.fontset'] = 'cm'

def draw_card(ax, x, y, w, h, title, subtitle="", bg_color="#FFFFFF", border_color="#2C3E50", title_color="#2C3E50", sub_color="#555555"):
    card = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=0.12",
                                 facecolor=bg_color, edgecolor=border_color, linewidth=1.5, zorder=3)
    ax.add_patch(card)
    if subtitle:
        ax.text(x + w/2, y + h*0.65, title, color=title_color, weight='bold', fontsize=10, ha='center', va='center', zorder=4)
        ax.text(x + w/2, y + h*0.30, subtitle, color=sub_color, fontsize=8, ha='center', va='center', zorder=4)
    else:
        ax.text(x + w/2, y + h/2, title, color=title_color, weight='bold', fontsize=10, ha='center', va='center', zorder=4)

def draw_orthogonal_arrow(ax, path, label="", label_pos=(0, 0), color="#2C3E50", ls="-", lw=1.5):
    xs, ys = zip(*path)
    ax.plot(xs, ys, color=color, linestyle=ls, linewidth=lw, zorder=2)
    x_end, y_end = path[-1]
    x_prev, y_prev = path[-2]
    dx = 0.001 if (x_end - x_prev) > 0 else (-0.001 if (x_end - x_prev) < 0 else 0)
    dy = 0.001 if (y_end - y_prev) > 0 else (-0.001 if (y_end - y_prev) < 0 else 0)
    ax.annotate("", xy=(x_end, y_end), xytext=(x_end - dx, y_end - dy),
                arrowprops=dict(arrowstyle="-|>", color=color, mutation_scale=14, lw=1.5), zorder=2)
    if label:
        lx, ly = label_pos
        ax.text(lx, ly, label, color=color, weight='bold', fontsize=8.5, ha='center', va='center',
                bbox=dict(boxstyle="square,pad=0.15", facecolor="white", edgecolor=color, lw=0.8, alpha=0.95), zorder=5)

def save_fig(name):
    target_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "science_paper_images")
    os.makedirs(target_dir, exist_ok=True)
    p = os.path.join(target_dir, name)
    plt.tight_layout()
    plt.savefig(p, dpi=300)
    plt.close()

# ==============================================================================
# FIGURE 1: HIGH-LEVEL SYSTEM ARCHITECTURE
# ==============================================================================
fig, ax = plt.subplots(figsize=(11, 6), dpi=300)
ax.axis('off')
ax.set_xlim(0, 11)
ax.set_ylim(0, 6)

ax.text(5.5, 5.7, "Multi-Tiered Agentic RAG System Architecture", fontsize=13, weight='bold', ha='center', color='#1A252C')

draw_card(ax, 0.4, 2.3, 1.3, 1.0, "User Query (q)", "Input Request", "#EBF5FB", "#2980B9", "#1B4F72")
draw_card(ax, 2.2, 2.3, 1.5, 1.0, "Router Node", "Intent Classifier", "#E8F8F5", "#16A085", "#0E6655")

draw_card(ax, 4.3, 4.2, 2.1, 1.1, "Tier 1: Local KB", "ChromaDB (8 Domains) + BM25\n(bge-m3 Embeddings)", "#FEF9E7", "#F39C12", "#7E5109")
draw_card(ax, 4.3, 2.25, 2.1, 1.0, "Tier 3: Expert API", "Tavily Research Engine", "#F4ECF7", "#8E44AD", "#4A235A")
draw_card(ax, 4.3, 0.35, 2.1, 1.1, "Tier 2: Web Fallback", "DuckDuckGo Web Index", "#EAF2F8", "#2980B9", "#1B4F72")

draw_card(ax, 7.1, 4.2, 1.4, 1.1, "Grader Node", "Binary Score (S_rel)", "#FDEDEC", "#E74C3C", "#78281F")
draw_card(ax, 9.1, 2.1, 1.5, 1.3, "Generator Node", "Qwen2.5 (7B LLM)\nGrounded Answer A", "#E8F8F5", "#2ECC71", "#145A32")

draw_orthogonal_arrow(ax, [(1.7, 2.8), (2.2, 2.8)])
draw_orthogonal_arrow(ax, [(3.7, 2.8), (3.9, 2.8), (3.9, 4.75), (4.3, 4.75)], label="Local Intent", label_pos=(3.9, 3.8), color="#27AE60")
draw_orthogonal_arrow(ax, [(3.7, 2.8), (4.3, 2.8)], label="Expert Intent", label_pos=(4.0, 2.8), color="#8E44AD")
draw_orthogonal_arrow(ax, [(6.4, 4.75), (7.1, 4.75)])
draw_orthogonal_arrow(ax, [(8.5, 4.75), (8.8, 4.75), (8.8, 2.75), (9.1, 2.75)], label="S_rel = 1", label_pos=(8.8, 3.9), color="#27AE60")
draw_orthogonal_arrow(ax, [(8.5, 4.75), (8.8, 4.75), (8.8, 0.9), (6.4, 0.9)], label="S_rel = 0 (Fallback)", label_pos=(8.8, 0.9), color="#C0392B")
draw_orthogonal_arrow(ax, [(6.4, 0.9), (8.6, 0.9), (8.6, 2.5), (9.1, 2.5)], color="#2980B9")
draw_orthogonal_arrow(ax, [(6.4, 2.75), (9.1, 2.75)], color="#8E44AD")

save_fig("fig1_architecture.png")

# ==============================================================================
# FIGURE 2: STATE GRAPH TRANSITION MODEL
# ==============================================================================
fig, ax = plt.subplots(figsize=(10.5, 5.5), dpi=300)
ax.axis('off')
ax.set_xlim(0, 10.5)
ax.set_ylim(0, 5.5)

ax.text(5.25, 5.15, r"Agentic State Graph Model $\mathcal{G} = (\mathcal{V}, \mathcal{E}, \mathcal{S})$", fontsize=13, weight='bold', ha='center', color='#1A252C')

draw_card(ax, 0.3, 2.1, 1.1, 0.9, "Start", "Query q", "#EBF5FB", "#2980B9")
draw_card(ax, 1.8, 2.05, 1.5, 1.0, "N_router", "Intent Classification", "#E8F8F5", "#16A085")
draw_card(ax, 3.9, 3.7, 1.6, 1.0, "N_local", "Tier 1 Retrieval", "#FEF9E7", "#F39C12")
draw_card(ax, 3.9, 0.5, 1.6, 1.0, "N_expert", "Tier 3 API Engine", "#F4ECF7", "#8E44AD")
draw_card(ax, 6.1, 3.7, 1.5, 1.0, "N_grader", "Relevance Check", "#FDEDEC", "#E74C3C")
draw_card(ax, 6.1, 0.5, 1.5, 1.0, "N_web", "Tier 2 Web Fallback", "#EAF2F8", "#2980B9")
draw_card(ax, 8.2, 2.05, 1.3, 1.0, "N_generator", "Answer Synthesis", "#E8F8F5", "#2ECC71")
draw_card(ax, 9.7, 2.1, 0.6, 0.9, "End", "", "#D5F5E3", "#27AE60")

draw_orthogonal_arrow(ax, [(1.4, 2.55), (1.8, 2.55)])
draw_orthogonal_arrow(ax, [(3.3, 2.55), (3.5, 2.55), (3.5, 4.2), (3.9, 4.2)], label=r"$\delta_{router} = \text{local}$", label_pos=(3.5, 3.4), color="#27AE60")
draw_orthogonal_arrow(ax, [(3.3, 2.55), (3.5, 2.55), (3.5, 1.0), (3.9, 1.0)], label=r"$\delta_{router} = \text{expert}$", label_pos=(3.5, 1.7), color="#8E44AD")
draw_orthogonal_arrow(ax, [(5.5, 4.2), (6.1, 4.2)])
draw_orthogonal_arrow(ax, [(7.6, 4.2), (7.9, 4.2), (7.9, 2.7), (8.2, 2.7)], label=r"$S_{\text{rel}} = 1$", label_pos=(7.9, 3.6), color="#27AE60")
draw_orthogonal_arrow(ax, [(6.85, 3.7), (6.85, 1.5)], label=r"$S_{\text{rel}} = 0$", label_pos=(6.85, 2.6), color="#C0392B")
draw_orthogonal_arrow(ax, [(7.6, 1.0), (7.9, 1.0), (7.9, 2.4), (8.2, 2.4)], color="#2980B9")
draw_orthogonal_arrow(ax, [(5.5, 1.0), (7.9, 1.0), (7.9, 2.45), (8.2, 2.45)], color="#8E44AD")
draw_orthogonal_arrow(ax, [(9.5, 2.55), (9.7, 2.55)])

save_fig("fig2_state_graph.png")

# ==============================================================================
# FIGURE 3: WEBSOCKET SEQUENCE DIAGRAM
# ==============================================================================
fig, ax = plt.subplots(figsize=(9.5, 6), dpi=300)
ax.axis('off')
ax.set_xlim(0, 10)
ax.set_ylim(0, 7)

cols = [1.2, 3.2, 5.2, 7.2, 8.8]
labels = ["Client UI\n(Next.js)", "FastAPI\nGateway", "LangGraph\nEngine", "Tier 1\nChromaDB", "Tier 2\nDuckDuckGo"]
colors = ["#34495e", "#3498db", "#2ecc71", "#9b59b6", "#f39c12"]

for x, label, col_color in zip(cols, labels, colors):
    ax.text(x, 6.4, label, color="white", weight="bold", fontsize=9, ha="center", va="center",
            bbox=dict(boxstyle="round,pad=0.3", facecolor=col_color, edgecolor="black", lw=1))
    ax.plot([x, x], [0.5, 5.9], "--", color="#bdc3c7", lw=1.2, zorder=1)

steps = [
    (5.4, 0, 1, "1. WS Connect & Query q", "#2c3e50", "solid"),
    (4.8, 1, 2, "2. Init State s0 = (q, null, 0)", "#2980b9", "solid"),
    (4.2, 2, 1, "3. Event: Node N_router Started", "#27ae60", "dashed"),
    (3.6, 1, 0, "4. WS Frame: N_router Running", "#3498db", "dashed"),
    (3.0, 2, 3, "5. Execute Hybrid Search", "#8e44ad", "solid"),
    (2.4, 3, 2, "6. Return D_ret", "#8e44ad", "dashed"),
    (1.8, 2, 4, "7. Fallback Search (S_rel=0)", "#e67e22", "solid"),
    (1.2, 4, 2, "8. Return D_web Context", "#e67e22", "dashed"),
    (0.6, 2, 0, "9. Stream Packetized Tokens (A)", "#1abc9c", "solid")
]

for y, src_idx, dst_idx, text, msg_color, style in steps:
    x_src, x_dst = cols[src_idx], cols[dst_idx]
    ls = "-" if style == "solid" else "--"
    ax.annotate("", xy=(x_dst, y), xytext=(x_src, y),
                arrowprops=dict(arrowstyle="->", color=msg_color, lw=1.5, ls=ls), zorder=3)
    mid_x = (x_src + x_dst) / 2
    ax.text(mid_x, y + 0.15, text, color=msg_color, weight="bold", fontsize=8.2, ha="center", va="bottom",
            bbox=dict(boxstyle="square,pad=0.1", facecolor="white", edgecolor="none", alpha=0.8))

save_fig("fig3_sequence_diagram.png")

# ==============================================================================
# FIGURE 4: PARETO FRONTIER CHART (Version 2.0 - Synchronized with Table II)
# ==============================================================================
fig, ax1 = plt.subplots(figsize=(8.5, 5), dpi=300)

paradigms = ['Pure Local RAG', 'Naive Static RAG', 'Pure Web RAG', 'Proposed Agentic RAG']
costs = [0.00, 2.50, 5.00, 0.90]                 # Marginal Cost ($ / 1k queries)
faithfulness = [52.0, 55.0, 48.0, 62.0]          # Faithfulness Score (%)
relevance = [61.0, 65.0, 68.0, 73.0]             # Answer Relevance (%)
latencies = [1.12, 2.10, 3.45, 1.85]             # First-Token Latency (seconds)

colors = ['#3498db', '#9b59b6', '#e74c3c', '#2ecc71']

# Bubble size proportional to First-Token Latency
sizes = [l * 120 for l in latencies]
scatter = ax1.scatter(costs, faithfulness, s=sizes, c=colors, alpha=0.9, edgecolors='black', linewidth=1.5, zorder=5)

# Annotate points with exact v2 values
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
ax1.set_title('Fig. 4: Pareto Efficiency Frontier (Faithfulness vs Marginal Cost vs First-Token Latency)', fontsize=12, fontweight='bold', pad=15)

ax1.set_xlim(-0.4, 5.8)
ax1.set_ylim(44, 68)
ax1.grid(True, linestyle='--', alpha=0.6)
ax1.legend(loc='lower right', frameon=True, facecolor='white', edgecolor='#bdc3c7', fontsize=9.5)

save_fig("fig4_pareto_chart.png")

print("All figures successfully regenerated and saved to science_paper_assets/science_paper_images!")
