import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Ensure output directories exist in both manuscript packages
OUT_DIRS = [
    os.path.abspath("manuscripts/paper1_springer_nature/figures"),
    os.path.abspath("manuscripts/paper2_software_impacts/figures")
]
for d in OUT_DIRS:
    os.makedirs(d, exist_ok=True)

# Set high DPI and professional font styling (large, crisp, highly legible)
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['font.family'] = 'sans-serif'

# Harmonized Palette matching Draw.io
c_input   = '#3B82F6'  # Blue
c_router  = '#4F46E5'  # Indigo
c_tier1   = '#059669'  # Emerald
c_tier2   = '#D97706'  # Amber
c_tier3   = '#7C3AED'  # Purple
c_repl    = '#DB2777'  # Pink
c_grader  = '#EA580C'  # Orange
c_gen     = '#0D9488'  # Teal
c_edge    = '#1E293B'  # Slate

def draw_node(ax, x, y, w, h, title, subtitle="", color="#1E293B", text_color="white", title_fs=12.5, sub_fs=10.5):
    """Draw a clean rounded card with sharp border and centered two-line text."""
    box = patches.FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.1,rounding_size=0.18",
        facecolor=color, edgecolor="#0F172A", linewidth=1.8, alpha=0.98, zorder=2
    )
    ax.add_patch(box)
    if subtitle:
        ax.text(x + w/2, y + h*0.62, title, color=text_color, weight='bold', fontsize=title_fs, ha='center', va='center', zorder=3)
        ax.text(x + w/2, y + h*0.28, subtitle, color=text_color, fontsize=sub_fs, ha='center', va='center', zorder=3)
    else:
        ax.text(x + w/2, y + h/2, title, color=text_color, weight='bold', fontsize=title_fs, ha='center', va='center', zorder=3)

def draw_badge(ax, x, y, text, text_color, border_color="#CBD5E1", fontsize=10.5, zorder=4):
    """Draw a white-background note badge with subtle border over an arrow line."""
    ax.text(
        x, y, text,
        fontsize=fontsize, weight='bold', color=text_color,
        ha='center', va='center', zorder=zorder,
        bbox=dict(boxstyle="round,pad=0.35,rounding_size=0.2", facecolor="#FFFFFF", edgecolor=border_color, linewidth=1.4, alpha=1.0)
    )

arrow_main = dict(arrowstyle="-|>", color=c_edge, lw=2.2, mutation_scale=16)
arrow_dash = dict(arrowstyle="-|>", color="#DC2626", lw=2.0, ls="--", mutation_scale=16)

# =============================================================================
# FIGURE 1: Overall System Architecture (Wide Canvas, Generous Spacing, White Badges)
# =============================================================================
fig1, ax1 = plt.subplots(figsize=(14.2, 7.6), dpi=300)
ax1.axis('off')
ax1.set_xlim(0, 14.2)
ax1.set_ylim(0, 7.6)

# 1. Input Node
draw_node(ax1, 0.4, 3.1, 2.0, 1.4, "User Query (q)", "Raw Query Stream / UI", c_input, title_fs=12.5, sub_fs=10.5)

# 2. Router Node
draw_node(ax1, 3.2, 3.0, 2.2, 1.6, "Router Node (δ_router)", "Heuristic + Qwen-7B\nIntent Classifier", c_router, title_fs=12.5, sub_fs=10.5)

# 3. Knowledge Tiers + REPL Sandbox (Generous spacing, w=3.3)
draw_node(ax1, 6.3, 5.7, 3.3, 1.4, "Tier 1: Local Knowledge Corpus", "ChromaDB (Dense) + BM25 (Sparse)\nWeighted RRF (k=60, w=0.7/0.3)\n618 Papers | 144,380 Chunks", c_tier1, title_fs=12, sub_fs=10)
draw_node(ax1, 6.3, 4.0, 3.3, 1.3, "Tier 3: Expert Synthesis", "Tavily Academic Search API\nCross-Paper Synthesis", c_tier3, title_fs=12, sub_fs=10.5)
draw_node(ax1, 6.3, 2.3, 3.3, 1.3, "Tier 2: Web Search Fallback", "DuckDuckGo Search API\nTriggered on Overlap < 0.25", c_tier2, title_fs=12, sub_fs=10.5)
draw_node(ax1, 6.3, 0.6, 3.3, 1.3, "Python REPL Sandbox (v_repl)", "Deterministic Math & Code\nProcess-Isolated Execution", c_repl, title_fs=12, sub_fs=10.5)

# 4. Relevance Grader Node
draw_node(ax1, 10.6, 5.7, 2.4, 1.4, "Relevance Grader (δ_grader)", "Token Set Overlap Metric\nThreshold τ ≥ 0.25", c_grader, title_fs=12, sub_fs=10.5)

# 5. LLM Generator Node with Self-Correction
draw_node(ax1, 10.6, 2.3, 2.4, 2.0, "LLM Generator Node", "Qwen2.5-7B Instruct\nGrounded Synthesis\n(Retry Loop r ≤ 2)", c_gen, title_fs=12.5, sub_fs=10.5)

# Output stream box
draw_node(ax1, 13.5, 2.7, 0.5, 1.2, "", "", "#047857")
ax1.text(13.75, 3.3, "Grounded Output\n(WebSocket Stream)", fontsize=11, weight='bold', color="#065F46", ha='left', va='center')

# Connectors - Input to Router
ax1.annotate("", xy=(3.2, 3.8), xytext=(2.4, 3.8), arrowprops=arrow_main)

# Router outgoing arrows
ax1.annotate("", xy=(6.3, 6.4), xytext=(5.4, 4.3), arrowprops=arrow_main)
draw_badge(ax1, 5.7, 5.5, "Local Query", "#047857", "#A7F3D0")

ax1.annotate("", xy=(6.3, 4.65), xytext=(5.4, 3.9), arrowprops=arrow_main)
draw_badge(ax1, 5.7, 4.4, "Comparative", "#6D28D9", "#DDD6FE")

ax1.annotate("", xy=(6.3, 1.25), xytext=(5.4, 3.3), arrowprops=arrow_main)
draw_badge(ax1, 5.7, 2.1, "Math / Code", "#BE185D", "#FBCFE8")

# Tier 1 to Grader
ax1.annotate("", xy=(10.6, 6.4), xytext=(9.6, 6.4), arrowprops=arrow_main)

# Grader to Generator (Pass)
ax1.annotate("", xy=(11.3, 4.3), xytext=(11.3, 5.7), arrowprops=arrow_main)
draw_badge(ax1, 11.3, 5.0, "Pass (Overlap ≥ 0.25)", "#047857", "#A7F3D0")

# Grader to Tier 2 Fallback (Fail)
ax1.annotate("", xy=(9.6, 3.1), xytext=(10.6, 6.0), arrowprops=arrow_dash)
draw_badge(ax1, 10.0, 4.3, "Fail -> Fallback (τ < 0.25)", "#C2410C", "#FED7AA")

# Tiers to Generator
ax1.annotate("", xy=(10.6, 3.5), xytext=(9.6, 3.1), arrowprops=arrow_main)
ax1.annotate("", xy=(10.6, 3.9), xytext=(9.6, 4.65), arrowprops=arrow_main)
ax1.annotate("", xy=(10.6, 2.7), xytext=(9.6, 1.25), arrowprops=arrow_main)

# Output arrow
ax1.annotate("", xy=(13.5, 3.3), xytext=(13.0, 3.3), arrowprops=arrow_main)

# Self-Correction Loop on Generator
curve = patches.FancyArrowPatch(
    (11.8, 4.3), (11.8, 2.3),
    connectionstyle="arc3,rad=1.35",
    arrowstyle="-|>", color="#DC2626", lw=2.4, mutation_scale=16, zorder=3
)
ax1.add_patch(curve)
draw_badge(ax1, 12.8, 3.3, "Hallucination Retry\n(r ≤ 2)", "#B91C1C", "#FECACA")

plt.tight_layout()
for d in OUT_DIRS:
    fig1.savefig(os.path.join(d, "fig1_overall_architecture.png"), dpi=300, bbox_inches='tight')
    fig1.savefig(os.path.join(d, "fig1_overall_architecture.pdf"), bbox_inches='tight')
plt.close(fig1)
print("Updated Figure 1 with crisp white note badges and generous spacing.")

# =============================================================================
# FIGURE 2: LangGraph State Machine Graph (All 7 Nodes in V, White Badges)
# =============================================================================
fig2, ax2 = plt.subplots(figsize=(14.2, 7.5), dpi=300)
ax2.axis('off')
ax2.set_xlim(0, 14.2)
ax2.set_ylim(0, 7.5)

# START node
draw_node(ax2, 0.4, 3.3, 1.0, 0.9, "START", "", "#1E293B", title_fs=12)

# All 7 nodes in V:
draw_node(ax2, 1.9, 3.1, 2.1, 1.3, "v_router", "Query Router", "#4F46E5", title_fs=12.5, sub_fs=11)
draw_node(ax2, 4.8, 5.7, 2.5, 1.3, "v_retrieve", "Retrieve Local (RRF)", "#059669", title_fs=12.5, sub_fs=11)
draw_node(ax2, 4.8, 3.8, 2.5, 1.3, "v_expert", "Expert Consult (Tavily)", "#7C3AED", title_fs=12.5, sub_fs=11)
draw_node(ax2, 4.8, 0.7, 2.5, 1.3, "v_repl", "Python REPL Sandbox", "#DB2777", title_fs=12.5, sub_fs=11)
draw_node(ax2, 8.2, 5.7, 2.4, 1.3, "v_grade", "Relevance Grader", "#EA580C", title_fs=12.5, sub_fs=11)
draw_node(ax2, 8.2, 3.8, 2.4, 1.3, "v_web", "Web Search Fallback", "#D97706", title_fs=12.5, sub_fs=11)
draw_node(ax2, 11.5, 3.1, 2.1, 1.6, "v_generate", "LLM Generate\n(Qwen2.5-7B)", "#0D9488", title_fs=12.5, sub_fs=11)

# END node
draw_node(ax2, 14.1, 3.3, 0.1, 0.9, "", "", "#1E293B")
ax2.text(14.2, 3.75, "END", fontsize=12, weight='bold', color="#1E293B", ha='left', va='center')

# Connectors - Start to Router
ax2.annotate("", xy=(1.9, 3.75), xytext=(1.4, 3.75), arrowprops=arrow_main)

# Router Edges with white badges
ax2.annotate("", xy=(4.8, 6.35), xytext=(4.0, 4.2), arrowprops=arrow_main)
draw_badge(ax2, 4.2, 5.5, "route = local", "#065F46", "#A7F3D0")

ax2.annotate("", xy=(4.8, 4.45), xytext=(4.0, 3.9), arrowprops=arrow_main)
draw_badge(ax2, 4.2, 4.3, "route = expert", "#6D28D9", "#DDD6FE")

ax2.annotate("", xy=(4.8, 1.35), xytext=(4.0, 3.3), arrowprops=arrow_main)
draw_badge(ax2, 4.2, 2.1, "route = code", "#BE185D", "#FBCFE8")

# Retrieve to Grade
ax2.annotate("", xy=(8.2, 6.35), xytext=(7.3, 6.35), arrowprops=arrow_main)

# Grade edges with white badges
ax2.annotate("", xy=(11.5, 4.5), xytext=(10.6, 6.35), arrowprops=arrow_main)
draw_badge(ax2, 11.0, 5.6, "grade = pass", "#047857", "#A7F3D0")

ax2.annotate("", xy=(9.4, 5.1), xytext=(9.4, 5.7), arrowprops=arrow_main)
draw_badge(ax2, 9.4, 5.4, "grade = fail", "#C2410C", "#FED7AA")

# Web, Expert, REPL to Generate
ax2.annotate("", xy=(11.5, 4.0), xytext=(10.6, 4.45), arrowprops=arrow_main)
ax2.annotate("", xy=(11.5, 3.75), xytext=(7.3, 4.45), arrowprops=arrow_main)
ax2.annotate("", xy=(11.5, 3.4), xytext=(7.3, 1.35), arrowprops=arrow_main)

# Self-Correction Loop on Generate with white badge
curve2 = patches.FancyArrowPatch(
    (12.5, 4.7), (12.5, 3.1),
    connectionstyle="arc3,rad=1.35",
    arrowstyle="-|>", color="#DC2626", lw=2.4, mutation_scale=16, zorder=3
)
ax2.add_patch(curve2)
draw_badge(ax2, 13.5, 4.0, "hallucinated\n∧ r < 2", "#B91C1C", "#FECACA")

# Terminal Edge with white badge
ax2.annotate("", xy=(14.1, 3.75), xytext=(13.6, 3.75), arrowprops=arrow_main)
draw_badge(ax2, 13.8, 3.2, "grounded ∨ r ≥ 2", "#0D9488", "#CCFBF1", fontsize=9.5)

plt.tight_layout()
for d in OUT_DIRS:
    fig2.savefig(os.path.join(d, "fig2_langgraph_state_machine.png"), dpi=300, bbox_inches='tight')
    fig2.savefig(os.path.join(d, "fig2_langgraph_state_machine.pdf"), bbox_inches='tight')
plt.close(fig2)
print("Updated Figure 2 with crisp white note badges and generous spacing.")

# =============================================================================
# FIGURE 3: SciStudio Multi-Tier Architecture (Generous Swimlane Spacing)
# =============================================================================
fig3, ax3 = plt.subplots(figsize=(14.2, 8.4), dpi=300)
ax3.axis('off')
ax3.set_xlim(0, 14.2)
ax3.set_ylim(0, 8.4)

# 4 Horizontal Tiers with wide separation (gap = 0.5)
draw_node(ax3, 0.5, 6.4, 13.2, 1.4, "Presentation Layer (Vue.js 3 + Vite SPA)", "Monaco Editor | PyMuPDF Canvas Viewer | Click-to-Verify Bounding Box Engine | WebSocket Stream Client", "#1E40AF", title_fs=13, sub_fs=11)
draw_node(ax3, 0.5, 4.4, 13.2, 1.4, "API Gateway & Services (FastAPI)", "REST Endpoints (/api/projects, /api/papers) | WebSocket Gateway (/ws/chat) | JWT Bearer Auth | Citation Linker", "#4338CA", title_fs=13, sub_fs=11)
draw_node(ax3, 0.5, 2.4, 13.2, 1.4, "Core Agentic Engine (LangGraph State Graph)", "Intent Classifier Router | Weighted RRF Hybrid Retriever | Relevance Fallback | Local LLM Generator", "#047857", title_fs=13, sub_fs=11)
draw_node(ax3, 0.5, 0.4, 13.2, 1.4, "Storage & Persistence Layer", "ChromaDB Vector Store (144k Embeddings) | BM25 Pickle Cache (0.84s init) | SQLite DB | Isolated REPL Jail", "#B45309", title_fs=13, sub_fs=11)

# Downward flow arrows between tiers with prominent white badges
ax3.annotate("", xy=(7.1, 5.8), xytext=(7.1, 6.4), arrowprops=arrow_main)
draw_badge(ax3, 7.1, 6.1, "User Events & Streaming State", "#334155", "#CBD5E1")

ax3.annotate("", xy=(7.1, 3.8), xytext=(7.1, 4.4), arrowprops=arrow_main)
draw_badge(ax3, 7.1, 4.1, "REST API & LangGraph Workflow Invocations", "#334155", "#CBD5E1")

ax3.annotate("", xy=(7.1, 1.8), xytext=(7.1, 2.4), arrowprops=arrow_main)
draw_badge(ax3, 7.1, 2.1, "Chroma Vector & BM25 Cache Lookups", "#334155", "#CBD5E1")

plt.tight_layout()
for d in OUT_DIRS:
    fig3.savefig(os.path.join(d, "fig3_scistudio_software_architecture.png"), dpi=300, bbox_inches='tight')
    fig3.savefig(os.path.join(d, "fig3_scistudio_software_architecture.pdf"), bbox_inches='tight')
plt.close(fig3)
print("Updated Figure 3 with crisp white note badges and generous spacing.")
