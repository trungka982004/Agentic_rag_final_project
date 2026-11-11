import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Ensure output directory exists
OUT_DIR = "manuscripts/paper1_springer_nature/figures"
os.makedirs(OUT_DIR, exist_ok=True)

# Set high DPI and professional font styling
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['font.family'] = 'sans-serif'

# -----------------------------------------------------------------------------
# FIGURE 1: Overall System Architecture (Redrawn, Clean, No In-Image Title)
# -----------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(11, 6.2), dpi=300)
ax.axis('off')
ax.set_xlim(0, 11)
ax.set_ylim(0, 6.2)

# Scientific color palette
c_input   = '#3B82F6'  # Blue
c_router  = '#6366F1'  # Indigo
c_tier1   = '#10B981'  # Emerald
c_tier2   = '#F59E0B'  # Amber
c_tier3   = '#8B5CF6'  # Purple
c_repl    = '#EC4899'  # Pink
c_grader  = '#D97706'  # Dark Amber
c_gen     = '#059669'  # Dark Emerald

def draw_node(ax, x, y, w, h, title, subtitle="", color="#1E293B", text_color="white"):
    box = patches.FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.08,rounding_size=0.15",
        facecolor=color, edgecolor="#0F172A", linewidth=1.5, alpha=0.95
    )
    ax.add_patch(box)
    if subtitle:
        ax.text(x + w/2, y + h*0.62, title, color=text_color, weight='bold', fontsize=11, ha='center', va='center')
        ax.text(x + w/2, y + h*0.28, subtitle, color=text_color, fontsize=9.5, ha='center', va='center')
    else:
        ax.text(x + w/2, y + h/2, title, color=text_color, weight='bold', fontsize=11, ha='center', va='center')

arrow_main = dict(arrowstyle="-|>", color="#1E293B", lw=2, mutation_scale=15)
arrow_dash = dict(arrowstyle="-|>", color="#475569", lw=1.8, ls="--", mutation_scale=15)

# 1. Input
draw_node(ax, 0.4, 2.5, 1.6, 1.2, "User Query (q)", "Raw Query Stream", c_input)

# 2. Dynamic Router
draw_node(ax, 2.6, 2.5, 1.8, 1.2, "Router Node", "Heuristic + Qwen-7B", c_router)

# 3. Knowledge Tiers + REPL
draw_node(ax, 5.0, 4.6, 2.6, 1.2, "Tier 1: Local Corpus", "ChromaDB + BM25 (RRF)\n618 Papers (144k Chunks)", c_tier1)
draw_node(ax, 5.0, 3.1, 2.6, 1.1, "Tier 3: Expert Synthesis", "Tavily Academic API", c_tier3)
draw_node(ax, 5.0, 1.6, 2.6, 1.1, "Tier 2: Web Fallback", "DuckDuckGo Search", c_tier2)
draw_node(ax, 5.0, 0.2, 2.6, 1.0, "Python REPL Sandbox", "Deterministic Computation", c_repl)

# 4. Grader Node (Phase 1)
draw_node(ax, 8.2, 4.6, 1.7, 1.2, "Relevance Grader", "Token Set Intersection\nOverlap >= 0.25", c_grader)

# 5. Generator Node
draw_node(ax, 8.2, 1.8, 1.7, 1.6, "LLM Generator", "Qwen2.5-7B\nGrounded Synthesis\n(Max 2 Retries)", c_gen)

# Arrows
ax.annotate("", xy=(2.6, 3.1), xytext=(2.0, 3.1), arrowprops=arrow_main)

# Router outgoing
ax.annotate("Local Query", xy=(5.0, 5.2), xytext=(4.4, 3.7), arrowprops=arrow_main, fontsize=9, color="#047857", weight='bold')
ax.annotate("Comparison / Trend", xy=(5.0, 3.65), xytext=(4.4, 3.1), arrowprops=arrow_main, fontsize=8.5, color="#6D28D9", weight='bold')
ax.annotate("Math / Code", xy=(5.0, 0.7), xytext=(4.4, 2.5), arrowprops=arrow_main, fontsize=9, color="#BE185D", weight='bold')

# Tier 1 to Grader
ax.annotate("", xy=(8.2, 5.2), xytext=(7.6, 5.2), arrowprops=arrow_main)

# Grader to Web Fallback (If not relevant)
ax.annotate("Pass (Relevant)", xy=(8.6, 3.4), xytext=(8.6, 4.6), arrowprops=arrow_main, fontsize=8.5, color="#047857", weight='bold')
ax.annotate("Fail -> Trigger Fallback", xy=(7.6, 2.15), xytext=(8.6, 4.6), arrowprops=arrow_dash, fontsize=8.5, color="#B45309", weight='bold')

# Tiers to Generator
ax.annotate("", xy=(8.2, 2.6), xytext=(7.6, 2.15), arrowprops=arrow_main)
ax.annotate("", xy=(8.2, 2.8), xytext=(7.6, 3.65), arrowprops=arrow_main)
ax.annotate("", xy=(8.2, 2.2), xytext=(7.6, 0.7), arrowprops=arrow_main)

# Output stream
ax.annotate("", xy=(10.7, 2.6), xytext=(9.9, 2.6), arrowprops=arrow_main)
ax.text(10.3, 2.9, "Grounded Output\n(WebSocket Stream)", fontsize=9, weight='bold', color="#065F46", ha='center')

plt.tight_layout()
fig1_path = os.path.join(OUT_DIR, "fig1_overall_architecture.png")
fig.savefig(fig1_path, dpi=300, bbox_inches='tight')
plt.close(fig)
print(f"Generated Figure 1: {fig1_path}")

# -----------------------------------------------------------------------------
# FIGURE 2: LangGraph State Machine (LangGraph Graph with V = {7 nodes})
# -----------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(10.5, 6), dpi=300)
ax.axis('off')
ax.set_xlim(0, 10.5)
ax.set_ylim(0, 6)

# Nodes: Router, Retrieve, Grade, WebSearch, ExpertSearch, PythonREPL, Generate
draw_node(ax, 0.5, 2.5, 1.8, 1.1, "v_router", "Query Router", "#4F46E5")
draw_node(ax, 3.0, 4.5, 2.0, 1.1, "v_retrieve", "Retrieve Local (RRF)", "#059669")
draw_node(ax, 3.0, 2.5, 2.0, 1.1, "v_expert", "Expert Consult (Tavily)", "#7C3AED")
draw_node(ax, 3.0, 0.5, 2.0, 1.1, "v_repl", "Python REPL (Sandbox)", "#DB2777")
draw_node(ax, 5.7, 4.5, 2.0, 1.1, "v_grade", "Relevance Grader", "#D97706")
draw_node(ax, 5.7, 2.5, 2.0, 1.1, "v_web", "Web Search Fallback", "#EA580C")
draw_node(ax, 8.4, 2.5, 1.8, 1.4, "v_generate", "LLM Generate\n(Self-Correction)", "#0D9488")

# Router Edges
ax.annotate("route=local", xy=(3.0, 5.0), xytext=(2.3, 3.2), arrowprops=arrow_main, fontsize=8.5, color="#065F46")
ax.annotate("route=expert", xy=(3.0, 3.05), xytext=(2.3, 3.05), arrowprops=arrow_main, fontsize=8.5, color="#6D28D9")
ax.annotate("route=code", xy=(3.0, 1.05), xytext=(2.3, 2.9), arrowprops=arrow_main, fontsize=8.5, color="#BE185D")

# Retrieve to Grade
ax.annotate("", xy=(5.7, 5.05), xytext=(5.0, 5.05), arrowprops=arrow_main)

# Grade edges
ax.annotate("grade=pass", xy=(8.4, 3.5), xytext=(7.7, 5.05), arrowprops=arrow_main, fontsize=8.5, color="#047857", weight='bold')
ax.annotate("grade=fail", xy=(6.7, 3.6), xytext=(6.7, 4.5), arrowprops=arrow_main, fontsize=8.5, color="#C2410C", weight='bold')

# Web to Generate
ax.annotate("", xy=(8.4, 3.05), xytext=(7.7, 3.05), arrowprops=arrow_main)
# Expert to Generate
ax.annotate("", xy=(8.4, 2.9), xytext=(5.0, 2.9), arrowprops=arrow_main)
# REPL to Generate
ax.annotate("", xy=(8.4, 2.7), xytext=(5.0, 1.05), arrowprops=arrow_main)

# Self-Correction Loop on Generate
curve = patches.FancyArrowPatch(
    (9.3, 3.9), (9.3, 1.8),
    connectionstyle="arc3,rad=1.3",
    arrowstyle="-|>", color="#DC2626", lw=2, mutation_scale=15
)
ax.add_patch(curve)
ax.text(10.3, 2.85, "Self-Correction\nHallucination Retry\n(r <= 2)", color="#B91C1C", fontsize=8.5, weight='bold', ha='center')

plt.tight_layout()
fig2_path = os.path.join(OUT_DIR, "fig2_langgraph_state_machine.png")
fig.savefig(fig2_path, dpi=300, bbox_inches='tight')
plt.close(fig)
print(f"Generated Figure 2: {fig2_path}")
