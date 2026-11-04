import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Set clean publication style
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['font.size'] = 9.5
plt.rcParams['mathtext.fontset'] = 'cm'

# Helper function for sharp rounded boxes with professional drop shadows/borders
def draw_card(ax, x, y, w, h, title, subtitle="", bg_color="#FFFFFF", border_color="#2C3E50", title_color="#2C3E50", sub_color="#555555"):
    # Main Card
    card = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=0.12",
                                 facecolor=bg_color, edgecolor=border_color, linewidth=1.5, zorder=3)
    ax.add_patch(card)
    
    if subtitle:
        ax.text(x + w/2, y + h*0.65, title, color=title_color, weight='bold', fontsize=10, ha='center', va='center', zorder=4)
        ax.text(x + w/2, y + h*0.30, subtitle, color=sub_color, fontsize=8, ha='center', va='center', zorder=4)
    else:
        ax.text(x + w/2, y + h/2, title, color=title_color, weight='bold', fontsize=10, ha='center', va='center', zorder=4)

# Draw orthogonal arrow path (segmented lines with arrow head at end)
def draw_orthogonal_arrow(ax, path, label="", label_pos=(0, 0), color="#2C3E50", ls="-", lw=1.5):
    # path is a list of (x, y) coordinates forming right angles
    xs, ys = zip(*path)
    ax.plot(xs, ys, color=color, linestyle=ls, linewidth=lw, zorder=2)
    
    # Arrow head at the last segment
    x_end, y_end = path[-1]
    x_prev, y_prev = path[-2]
    dx = x_end - x_prev
    dy = y_end - y_prev
    
    # Normalize direction
    if dx != 0:
        dx = 0.001 if dx > 0 else -0.001
    if dy != 0:
        dy = 0.001 if dy > 0 else -0.001
        
    ax.annotate("", xy=(x_end, y_end), xytext=(x_end - dx, y_end - dy),
                arrowprops=dict(arrowstyle="-|>", color=color, mutation_scale=14, lw=1.5), zorder=2)
    
    if label:
        lx, ly = label_pos
        ax.text(lx, ly, label, color=color, weight='bold', fontsize=8.5, ha='center', va='center',
                bbox=dict(boxstyle="square,pad=0.15", facecolor="white", edgecolor=color, lw=0.8, alpha=0.95), zorder=5)

# ==============================================================================
# FIGURE 1: HIGH-LEVEL SYSTEM ARCHITECTURE (Orthogonal & Non-overlapping)
# ==============================================================================
fig, ax = plt.subplots(figsize=(11, 6), dpi=300)
ax.axis('off')
ax.set_xlim(0, 11)
ax.set_ylim(0, 6)

# Title Header Banner
ax.text(5.5, 5.7, "Multi-Tiered Agentic RAG System Architecture", fontsize=13, weight='bold', ha='center', color='#1A252C')

# Nodes placement
draw_card(ax, 0.4, 2.3, 1.3, 1.0, "User Query (q)", "Input Request", "#EBF5FB", "#2980B9", "#1B4F72")
draw_card(ax, 2.2, 2.3, 1.5, 1.0, "Router Node", "Intent Classifier", "#E8F8F5", "#16A085", "#0E6655")

# Tier Nodes
draw_card(ax, 4.3, 4.2, 2.1, 1.1, "Tier 1: Local KB", "ChromaDB + BM25\n(bge-m3 Embeddings)", "#FEF9E7", "#F39C12", "#7E5109")
draw_card(ax, 4.3, 2.25, 2.1, 1.0, "Tier 3: Expert API", "Tavily Research Engine", "#F4ECF7", "#8E44AD", "#4A235A")
draw_card(ax, 4.3, 0.35, 2.1, 1.1, "Tier 2: Web Fallback", "DuckDuckGo Web Index", "#EAF2F8", "#2980B9", "#1B4F72")

# Grader & Generator
draw_card(ax, 7.1, 4.2, 1.4, 1.1, "Grader Node", "Binary Score (S_rel)", "#FDEDEC", "#E74C3C", "#78281F")
draw_card(ax, 9.1, 2.1, 1.5, 1.3, "Generator Node", "Qwen2.5 (7B LLM)\nGrounded Answer A", "#E8F8F5", "#2ECC71", "#145A32")

# Orthogonal Connections (Strictly horizontal & vertical, zero overlap)
# 1. Query -> Router (Straight)
draw_orthogonal_arrow(ax, [(1.7, 2.8), (2.2, 2.8)])

# 2. Router -> Tier 1 (Orthogonal: Right -> Up -> Right)
draw_orthogonal_arrow(ax, [(3.7, 2.8), (3.9, 2.8), (3.9, 4.75), (4.3, 4.75)], label="Local Intent", label_pos=(3.9, 3.8), color="#27AE60")

# 3. Router -> Tier 3 (Straight)
draw_orthogonal_arrow(ax, [(3.7, 2.8), (4.3, 2.8)], label="Expert Intent", label_pos=(4.0, 2.8), color="#8E44AD")

# 4. Tier 1 -> Grader (Straight)
draw_orthogonal_arrow(ax, [(6.4, 4.75), (7.1, 4.75)])

# 5. Grader -> Generator (S_rel = 1: Right -> Down -> Right)
draw_orthogonal_arrow(ax, [(8.5, 4.75), (8.8, 4.75), (8.8, 2.75), (9.1, 2.75)], label="S_rel = 1", label_pos=(8.8, 3.9), color="#27AE60")

# 6. Grader -> Tier 2 Fallback (S_rel = 0: Right -> Down -> Left)
draw_orthogonal_arrow(ax, [(8.5, 4.75), (8.8, 4.75), (8.8, 0.9), (6.4, 0.9)], label="S_rel = 0 (Fallback)", label_pos=(8.8, 0.9), color="#C0392B")

# 7. Tier 2 -> Generator (Right -> Up -> Right)
draw_orthogonal_arrow(ax, [(6.4, 0.9), (8.6, 0.9), (8.6, 2.5), (9.1, 2.5)], color="#2980B9")

# 8. Tier 3 -> Generator (Straight)
draw_orthogonal_arrow(ax, [(6.4, 2.75), (9.1, 2.75)], color="#8E44AD")

plt.tight_layout()
plt.savefig('fig1_architecture.png', dpi=300)
plt.close()
print("Generated perfect fig1_architecture.png!")

# ==============================================================================
# FIGURE 2: STATE GRAPH TRANSITION MODEL (Orthogonal Layout)
# ==============================================================================
fig, ax = plt.subplots(figsize=(10.5, 5.5), dpi=300)
ax.axis('off')
ax.set_xlim(0, 10.5)
ax.set_ylim(0, 5.5)

ax.text(5.25, 5.15, r"Agentic State Graph Model $\mathcal{G} = (\mathcal{V}, \mathcal{E}, \mathcal{S})$", fontsize=13, weight='bold', ha='center', color='#1A252C')

# Nodes placement
draw_card(ax, 0.3, 2.1, 1.1, 0.9, "Start", "Query q", "#EBF5FB", "#2980B9")
draw_card(ax, 1.8, 2.05, 1.5, 1.0, "N_router", "Intent Classification", "#E8F8F5", "#16A085")
draw_card(ax, 3.9, 3.7, 1.6, 1.0, "N_local", "Tier 1 Retrieval", "#FEF9E7", "#F39C12")
draw_card(ax, 3.9, 0.5, 1.6, 1.0, "N_expert", "Tier 3 API Engine", "#F4ECF7", "#8E44AD")
draw_card(ax, 6.1, 3.7, 1.5, 1.0, "N_grader", "Relevance Check", "#FDEDEC", "#E74C3C")
draw_card(ax, 6.1, 0.5, 1.5, 1.0, "N_web", "Tier 2 Web Fallback", "#EAF2F8", "#2980B9")
draw_card(ax, 8.2, 2.05, 1.3, 1.0, "N_generator", "Answer Synthesis", "#E8F8F5", "#2ECC71")
draw_card(ax, 9.7, 2.1, 0.6, 0.9, "End", "", "#D5F5E3", "#27AE60")

# Orthogonal Connections
# 1. Start -> N_router
draw_orthogonal_arrow(ax, [(1.4, 2.55), (1.8, 2.55)])

# 2. N_router -> N_local (Up -> Right)
draw_orthogonal_arrow(ax, [(3.3, 2.55), (3.5, 2.55), (3.5, 4.2), (3.9, 4.2)], label=r"$\delta_{router} = \text{local}$", label_pos=(3.5, 3.4), color="#27AE60")

# 3. N_router -> N_expert (Down -> Right)
draw_orthogonal_arrow(ax, [(3.3, 2.55), (3.5, 2.55), (3.5, 1.0), (3.9, 1.0)], label=r"$\delta_{router} = \text{expert}$", label_pos=(3.5, 1.7), color="#8E44AD")

# 4. N_local -> N_grader (Straight)
draw_orthogonal_arrow(ax, [(5.5, 4.2), (6.1, 4.2)])

# 5. N_grader -> N_generator (Right -> Down -> Right)
draw_orthogonal_arrow(ax, [(7.6, 4.2), (7.9, 4.2), (7.9, 2.7), (8.2, 2.7)], label=r"$S_{\text{rel}} = 1$", label_pos=(7.9, 3.6), color="#27AE60")

# 6. N_grader -> N_web (Straight Down)
draw_orthogonal_arrow(ax, [(6.85, 3.7), (6.85, 1.5)], label=r"$S_{\text{rel}} = 0$", label_pos=(6.85, 2.6), color="#C0392B")

# 7. N_web -> N_generator (Right -> Up -> Right)
draw_orthogonal_arrow(ax, [(7.6, 1.0), (7.9, 1.0), (7.9, 2.4), (8.2, 2.4)], color="#2980B9")

# 8. N_expert -> N_generator (Right -> Up -> Right)
draw_orthogonal_arrow(ax, [(5.5, 1.0), (7.9, 1.0), (7.9, 2.45), (8.2, 2.45)], color="#8E44AD")

# 9. N_generator -> End (Straight)
draw_orthogonal_arrow(ax, [(9.5, 2.55), (9.7, 2.55)])

plt.tight_layout()
plt.savefig('fig2_state_graph.png', dpi=300)
plt.close()
print("Generated perfect fig2_state_graph.png!")
