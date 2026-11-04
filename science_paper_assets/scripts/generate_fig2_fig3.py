import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Set global matplotlib parameters
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['font.size'] = 10

# ==========================================
# FIGURE 2: STATE GRAPH TRANSITION MODEL
# ==========================================
fig, ax = plt.subplots(figsize=(9, 5.5), dpi=300)
ax.axis('off')
ax.set_xlim(0, 10)
ax.set_ylim(0, 6)

def draw_node(ax, x, y, w, h, text, subtext="", bg_color="#34495e", text_color="white", shape="box"):
    if shape == "circle":
        circle = patches.Circle((x + w/2, y + h/2), radius=w/2, facecolor=bg_color, edgecolor="black", lw=1.2)
        ax.add_patch(circle)
        ax.text(x + w/2, y + h/2, text, color=text_color, weight='bold', fontsize=9, ha='center', va='center')
    else:
        box = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.1,rounding_size=0.15",
                                   facecolor=bg_color, edgecolor="black", lw=1.2)
        ax.add_patch(box)
        if subtext:
            ax.text(x + w/2, y + h*0.65, text, color=text_color, weight='bold', fontsize=9.5, ha='center', va='center')
            ax.text(x + w/2, y + h*0.3, subtext, color=text_color, fontsize=8, ha='center', va='center')
        else:
            ax.text(x + w/2, y + h/2, text, color=text_color, weight='bold', fontsize=9.5, ha='center', va='center')

# Nodes
draw_node(ax, 0.4, 2.5, 1.2, 0.9, "Start", "User Query q", "#e74c3c", "white", "circle")
draw_node(ax, 2.2, 2.4, 1.6, 1.1, "N_router", "Intent Classifier", "#3498db")
draw_node(ax, 4.4, 4.2, 1.7, 1.1, "N_local", "Tier 1 Retrieval", "#2ecc71")
draw_node(ax, 4.4, 0.7, 1.7, 1.1, "N_expert", "Tier 3 API Engine", "#9b59b6")
draw_node(ax, 6.7, 4.2, 1.5, 1.1, "N_grader", "Relevance Score S_rel", "#e67e22")
draw_node(ax, 6.7, 2.4, 1.5, 1.1, "N_web", "Tier 2 Web Fallback", "#f1c40f", "black")
draw_node(ax, 8.6, 2.4, 1.1, 1.1, "N_generator", "Qwen2.5 Answer", "#1abc9c")

# Connectors
arrow = dict(arrowstyle="->", color="#2c3e50", lw=1.8)

ax.annotate("", xy=(2.2, 2.95), xytext=(1.6, 2.95), arrowprops=arrow)

# Router transitions
ax.annotate("δ_router = local", xy=(4.4, 4.75), xytext=(3.8, 2.95), arrowprops=arrow, fontsize=8, color="#27ae60", weight="bold")
ax.annotate("δ_router = expert", xy=(4.4, 1.25), xytext=(3.8, 2.95), arrowprops=arrow, fontsize=8, color="#8e44ad", weight="bold")

# Local -> Grader
ax.annotate("", xy=(6.7, 4.75), xytext=(6.1, 4.75), arrowprops=arrow)

# Grader transitions
ax.annotate("S_rel = 1 (Relevant)", xy=(8.6, 2.95), xytext=(8.2, 4.75), arrowprops=dict(arrowstyle="->", color="#27ae60", lw=1.8), fontsize=8, color="#27ae60", weight="bold")
ax.annotate("S_rel = 0 (Fallback)", xy=(7.45, 3.5), xytext=(7.45, 4.2), arrowprops=dict(arrowstyle="->", color="#e67e22", lw=1.8), fontsize=8, color="#e67e22", weight="bold")

# Web & Expert -> Generator
ax.annotate("", xy=(8.6, 2.95), xytext=(8.2, 2.95), arrowprops=arrow)
ax.annotate("", xy=(8.6, 2.95), xytext=(6.1, 1.25), arrowprops=arrow)

plt.tight_layout()
plt.savefig('fig2_state_graph.png', dpi=300)
plt.close()

print("Successfully generated fig2_state_graph.png!")

# ==========================================
# FIGURE 3: WEBSOCKET SEQUENCE DIAGRAM
# ==========================================
fig, ax = plt.subplots(figsize=(9.5, 6), dpi=300)
ax.axis('off')
ax.set_xlim(0, 10)
ax.set_ylim(0, 7)

# Columns: Client, Gateway, Agent, Tier1, Tier2
cols = [1.2, 3.2, 5.2, 7.2, 8.8]
labels = ["Client UI\n(Next.js)", "FastAPI\nGateway", "LangGraph\nEngine", "Tier 1\nChromaDB", "Tier 2\nDuckDuckGo"]
colors = ["#34495e", "#3498db", "#2ecc71", "#9b59b6", "#f39c12"]

# Draw vertical lifelines
for x, label, col_color in zip(cols, labels, colors):
    ax.text(x, 6.4, label, color="white", weight="bold", fontsize=9, ha="center", va="center",
            bbox=dict(boxstyle="round,pad=0.3", facecolor=col_color, edgecolor="black", lw=1))
    ax.plot([x, x], [0.5, 5.9], "--", color="#bdc3c7", lw=1.2, zorder=1)

# Sequence steps (from top to bottom)
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

plt.tight_layout()
plt.savefig('fig3_sequence_diagram.png', dpi=300)
plt.close()

print("Successfully generated fig3_sequence_diagram.png!")
