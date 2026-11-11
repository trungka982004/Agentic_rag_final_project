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

# Set high DPI and professional font styling (large, crisp, readable)
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

def draw_node(ax, x, y, w, h, title, subtitle="", color="#1E293B", text_color="white", title_fs=12, sub_fs=10):
    box = patches.FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.1,rounding_size=0.18",
        facecolor=color, edgecolor="#0F172A", linewidth=1.8, alpha=0.95
    )
    ax.add_patch(box)
    if subtitle:
        ax.text(x + w/2, y + h*0.62, title, color=text_color, weight='bold', fontsize=title_fs, ha='center', va='center')
        ax.text(x + w/2, y + h*0.28, subtitle, color=text_color, fontsize=sub_fs, ha='center', va='center')
    else:
        ax.text(x + w/2, y + h/2, title, color=text_color, weight='bold', fontsize=title_fs, ha='center', va='center')

arrow_main = dict(arrowstyle="-|>", color=c_edge, lw=2.2, mutation_scale=16)
arrow_dash = dict(arrowstyle="-|>", color="#DC2626", lw=2.0, ls="--", mutation_scale=16)

# =============================================================================
# FIGURE 1: Overall System Architecture (300 DPI, Vector PDF, Clean, >= 11pt)
# =============================================================================
fig1, ax1 = plt.subplots(figsize=(12, 6.6), dpi=300)
ax1.axis('off')
ax1.set_xlim(0, 12)
ax1.set_ylim(0, 6.6)

# 1. Input Node
draw_node(ax1, 0.4, 2.7, 1.8, 1.3, "User Query (q)", "Raw Query Stream / UI", c_input, title_fs=12, sub_fs=10.5)

# 2. Router Node
draw_node(ax1, 2.8, 2.7, 2.0, 1.3, "Router Node (δ_router)", "Heuristic + Qwen-7B\nIntent Classifier", c_router, title_fs=12, sub_fs=10.5)

# 3. Knowledge Tiers + REPL Sandbox
draw_node(ax1, 5.5, 4.9, 2.8, 1.3, "Tier 1: Local Corpus", "ChromaDB + BM25 (RRF)\n618 Papers (144k Chunks)", c_tier1, title_fs=12, sub_fs=10.5)
draw_node(ax1, 5.5, 3.4, 2.8, 1.2, "Tier 3: Expert Synthesis", "Tavily Academic API\nCross-Paper Synthesis", c_tier3, title_fs=12, sub_fs=10.5)
draw_node(ax1, 5.5, 1.9, 2.8, 1.2, "Tier 2: Web Fallback", "DuckDuckGo Search\nTriggered on Overlap < 0.25", c_tier2, title_fs=12, sub_fs=10.5)
draw_node(ax1, 5.5, 0.4, 2.8, 1.2, "Python REPL (v_repl)", "Deterministic Math & Code\nIsolated Execution", c_repl, title_fs=12, sub_fs=10.5)

# 4. Relevance Grader Node
draw_node(ax1, 9.0, 4.9, 2.0, 1.3, "Relevance Grader", "Token Overlap Metric\nThreshold τ ≥ 0.25", c_grader, title_fs=12, sub_fs=10.5)

# 5. LLM Generator Node with Self-Correction
draw_node(ax1, 9.0, 1.9, 2.0, 1.8, "LLM Generator", "Qwen2.5-7B Instruct\nGrounded Synthesis\n(Retry r ≤ 2)", c_gen, title_fs=12, sub_fs=10.5)

# Connectors
ax1.annotate("", xy=(2.8, 3.35), xytext=(2.2, 3.35), arrowprops=arrow_main)

# Router branching
ax1.annotate("Local Query", xy=(5.5, 5.55), xytext=(4.8, 3.9), arrowprops=arrow_main, fontsize=10.5, color="#065F46", weight='bold')
ax1.annotate("Comparative", xy=(5.5, 4.0), xytext=(4.8, 3.4), arrowprops=arrow_main, fontsize=10.5, color="#5B21B6", weight='bold')
ax1.annotate("Math / Code", xy=(5.5, 1.0), xytext=(4.8, 2.8), arrowprops=arrow_main, fontsize=10.5, color="#9D174D", weight='bold')

# Tier 1 to Grader
ax1.annotate("", xy=(9.0, 5.55), xytext=(8.3, 5.55), arrowprops=arrow_main)

# Grader to Generator / Fallback
ax1.annotate("Pass (τ ≥ 0.25)", xy=(9.5, 3.7), xytext=(9.5, 4.9), arrowprops=arrow_main, fontsize=10.5, color="#047857", weight='bold')
ax1.annotate("Fail -> Fallback", xy=(8.3, 2.5), xytext=(9.1, 4.9), arrowprops=arrow_dash, fontsize=10, color="#C2410C", weight='bold')

# Tiers to Generator
ax1.annotate("", xy=(9.0, 2.8), xytext=(8.3, 2.5), arrowprops=arrow_main)
ax1.annotate("", xy=(9.0, 3.0), xytext=(8.3, 4.0), arrowprops=arrow_main)
ax1.annotate("", xy=(9.0, 2.2), xytext=(8.3, 1.0), arrowprops=arrow_main)

# Output stream label
ax1.annotate("", xy=(11.8, 2.8), xytext=(11.0, 2.8), arrowprops=arrow_main)
ax1.text(11.4, 3.2, "Grounded Output\n(WebSocket Stream)", fontsize=10.5, weight='bold', color="#065F46", ha='center')

plt.tight_layout()
for d in OUT_DIRS:
    fig1.savefig(os.path.join(d, "fig1_overall_architecture.png"), dpi=300, bbox_inches='tight')
    fig1.savefig(os.path.join(d, "fig1_overall_architecture.pdf"), bbox_inches='tight')
plt.close(fig1)
print("Updated Figure 1: PNG (300 DPI) and PDF (Vector) across manuscript folders.")

# =============================================================================
# FIGURE 2: LangGraph State Machine (LangGraph Graph with V = {7 nodes})
# =============================================================================
fig2, ax2 = plt.subplots(figsize=(11.5, 6.5), dpi=300)
ax2.axis('off')
ax2.set_xlim(0, 11.5)
ax2.set_ylim(0, 6.5)

# START node
draw_node(ax2, 0.4, 2.9, 0.9, 0.8, "START", "", "#1E293B", title_fs=11)

# All 7 nodes in V:
draw_node(ax2, 1.8, 2.8, 1.8, 1.0, "v_router", "Query Router", "#4F46E5", title_fs=12, sub_fs=10.5)
draw_node(ax2, 4.3, 4.9, 2.1, 1.1, "v_retrieve", "Retrieve Local (RRF)", "#059669", title_fs=12, sub_fs=10.5)
draw_node(ax2, 4.3, 3.1, 2.1, 1.1, "v_expert", "Expert (Tavily)", "#7C3AED", title_fs=12, sub_fs=10.5)
draw_node(ax2, 4.3, 0.8, 2.1, 1.1, "v_repl", "Python REPL Sandbox", "#DB2777", title_fs=12, sub_fs=10.5)
draw_node(ax2, 7.1, 4.9, 2.0, 1.1, "v_grade", "Relevance Grader", "#EA580C", title_fs=12, sub_fs=10.5)
draw_node(ax2, 7.1, 3.1, 2.0, 1.1, "v_web", "Web Search Fallback", "#D97706", title_fs=12, sub_fs=10.5)
draw_node(ax2, 9.7, 2.7, 1.6, 1.4, "v_generate", "LLM Generate\n(Qwen2.5-7B)", "#0D9488", title_fs=12, sub_fs=10.5)

# Connectors
ax2.annotate("", xy=(1.8, 3.3), xytext=(1.3, 3.3), arrowprops=arrow_main)

# Router Edges
ax2.annotate("route=local", xy=(4.3, 5.45), xytext=(3.5, 3.8), arrowprops=arrow_main, fontsize=10, color="#065F46", weight='bold')
ax2.annotate("route=expert", xy=(4.3, 3.65), xytext=(3.6, 3.4), arrowprops=arrow_main, fontsize=10, color="#5B21B6", weight='bold')
ax2.annotate("route=code", xy=(4.3, 1.35), xytext=(3.5, 2.8), arrowprops=arrow_main, fontsize=10, color="#9D174D", weight='bold')

# Retrieve to Grade
ax2.annotate("", xy=(7.1, 5.45), xytext=(6.4, 5.45), arrowprops=arrow_main)

# Grade edges
ax2.annotate("grade=pass", xy=(9.7, 3.8), xytext=(8.8, 5.45), arrowprops=arrow_main, fontsize=10, color="#047857", weight='bold')
ax2.annotate("grade=fail", xy=(8.1, 4.2), xytext=(8.1, 4.9), arrowprops=arrow_main, fontsize=10, color="#C2410C", weight='bold')

# Web, Expert, REPL to Generate
ax2.annotate("", xy=(9.7, 3.4), xytext=(9.1, 3.65), arrowprops=arrow_main)
ax2.annotate("", xy=(9.7, 3.2), xytext=(6.4, 3.45), arrowprops=arrow_main)
ax2.annotate("", xy=(9.7, 3.0), xytext=(6.4, 1.35), arrowprops=arrow_main)

# Self-Correction Loop on Generate
curve = patches.FancyArrowPatch(
    (10.5, 4.1), (10.5, 2.7),
    connectionstyle="arc3,rad=1.35",
    arrowstyle="-|>", color="#DC2626", lw=2.2, mutation_scale=16
)
ax2.add_patch(curve)
ax2.text(10.8, 4.6, "Self-Correction Loop\n(Hallucination Retry r ≤ 2)", color="#B91C1C", fontsize=9.5, weight='bold', ha='center')

plt.tight_layout()
for d in OUT_DIRS:
    fig2.savefig(os.path.join(d, "fig2_langgraph_state_machine.png"), dpi=300, bbox_inches='tight')
    fig2.savefig(os.path.join(d, "fig2_langgraph_state_machine.pdf"), bbox_inches='tight')
plt.close(fig2)
print("Updated Figure 2: PNG (300 DPI) and PDF (Vector) across manuscript folders.")

# =============================================================================
# FIGURE 3: SciStudio Software Architecture (Paper 2 Software Impacts)
# =============================================================================
fig3, ax3 = plt.subplots(figsize=(12, 6.8), dpi=300)
ax3.axis('off')
ax3.set_xlim(0, 12)
ax3.set_ylim(0, 6.8)

# 4 Horizontal Tiers
draw_node(ax3, 0.5, 5.2, 11.0, 1.2, "Presentation Layer (Vue.js 3 + Vite SPA)", "Monaco Editor | PyMuPDF Canvas Viewer | Click-to-Verify Tooltip | WebSocket Client", "#1E40AF", title_fs=12, sub_fs=11)
draw_node(ax3, 0.5, 3.6, 11.0, 1.2, "API Gateway & Services (FastAPI)", "REST Endpoints (/api/projects, /api/papers) | WebSocket Gateway (/ws/chat) | JWT Bearer Auth | Citation Linker", "#4338CA", title_fs=12, sub_fs=11)
draw_node(ax3, 0.5, 2.0, 11.0, 1.2, "Agentic Execution Engine (LangGraph Core)", "Intent Classifier Router | Weighted RRF Hybrid Retriever | Relevance Fallback | Local LLM Generator", "#047857", title_fs=12, sub_fs=11)
draw_node(ax3, 0.5, 0.4, 11.0, 1.2, "Storage & Sandbox Layer", "ChromaDB Vector Store (144k Embeddings) | BM25 Pickle Cache (0.84s init) | SQLite DB | Isolated REPL Jail", "#B45309", title_fs=12, sub_fs=11)

# Downward flow arrows between tiers
ax3.annotate("", xy=(6.0, 4.8), xytext=(6.0, 5.2), arrowprops=arrow_main)
ax3.annotate("", xy=(6.0, 3.2), xytext=(6.0, 3.6), arrowprops=arrow_main)
ax3.annotate("", xy=(6.0, 1.6), xytext=(6.0, 2.0), arrowprops=arrow_main)

plt.tight_layout()
for d in OUT_DIRS:
    fig3.savefig(os.path.join(d, "fig3_scistudio_software_architecture.png"), dpi=300, bbox_inches='tight')
    fig3.savefig(os.path.join(d, "fig3_scistudio_software_architecture.pdf"), bbox_inches='tight')
plt.close(fig3)
print("Updated Figure 3: PNG (300 DPI) and PDF (Vector) across manuscript folders.")
