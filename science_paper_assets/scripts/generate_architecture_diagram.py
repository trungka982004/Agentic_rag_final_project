import matplotlib.pyplot as plt
import matplotlib.patches as patches

fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
ax.axis('off')

# Main background & title
ax.set_xlim(0, 10)
ax.set_ylim(0, 6)

# Colors
c_query = '#e74c3c'
c_router = '#3498db'
c_tier1 = '#2ecc71'
c_tier2 = '#f39c12'
c_tier3 = '#9b59b6'
c_grader = '#e67e22'
c_gen = '#1abc9c'

# Helper function to draw rounded boxes
def draw_box(ax, x, y, w, h, title, subtitle="", color="#34495e", text_color="white"):
    rect = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.1,rounding_size=0.15",
                                 facecolor=color, edgecolor="black", linewidth=1.2, alpha=0.9)
    ax.add_patch(rect)
    if subtitle:
        ax.text(x + w/2, y + h*0.6, title, color=text_color, weight='bold', fontsize=10, ha='center', va='center')
        ax.text(x + w/2, y + h*0.3, subtitle, color=text_color, fontsize=8, ha='center', va='center')
    else:
        ax.text(x + w/2, y + h/2, title, color=text_color, weight='bold', fontsize=10, ha='center', va='center')

# Draw Components
# 1. User Query
draw_box(ax, 0.3, 2.5, 1.4, 1.0, "User Query (q)", "Input Stream", c_query)

# 2. Router Node
draw_box(ax, 2.2, 2.5, 1.6, 1.0, "Router Node", "Intent Classifier", c_router)

# 3. Tier Blocks (Local, Web, Expert)
draw_box(ax, 4.3, 4.3, 2.2, 1.1, "Tier 1: Local Knowledge", "ChromaDB + BM25 Ensemble\n(bge-m3 Embeddings)", c_tier1)
draw_box(ax, 4.3, 2.5, 2.2, 1.0, "Tier 3: Expert Synthesis", "Tavily API Research Engine", c_tier3)
draw_box(ax, 4.3, 0.6, 2.2, 1.1, "Tier 2: Web Search Fallback", "DuckDuckGo Real-Time Web", c_tier2)

# 4. Grader Node
draw_box(ax, 7.0, 4.3, 1.3, 1.1, "Grader Node", "Binary Score\n(S_rel)", c_grader)

# 5. Generator Node
draw_box(ax, 8.5, 2.3, 1.3, 1.4, "Generator", "Qwen2.5 (7B)\nGrounded Answer", c_gen)

# Connectors with arrows
arrow_style = dict(arrowstyle="->", color="#2c3e50", lw=2)

# Query -> Router
ax.annotate("", xy=(2.2, 3.0), xytext=(1.7, 3.0), arrowprops=arrow_style)

# Router -> Tier 1 & Tier 3
ax.annotate("Local Intent", xy=(4.3, 4.85), xytext=(3.8, 3.0), arrowprops=arrow_style, fontsize=8, color="#27ae60", weight="bold")
ax.annotate("Expert Intent", xy=(4.3, 3.0), xytext=(3.8, 3.0), arrowprops=arrow_style, fontsize=8, color="#8e44ad", weight="bold")

# Tier 1 -> Grader
ax.annotate("", xy=(7.0, 4.85), xytext=(6.5, 4.85), arrowprops=arrow_style)

# Grader -> Generator (Valid context S_rel = 1)
ax.annotate("S_rel = 1", xy=(8.5, 3.2), xytext=(8.3, 4.85), arrowprops=dict(arrowstyle="->", color="#27ae60", lw=2), fontsize=8, color="#27ae60", weight="bold")

# Grader -> Tier 2 Fallback (Invalid context S_rel = 0)
ax.annotate("Fallback (S_rel = 0)", xy=(5.4, 1.7), xytext=(7.65, 4.3), arrowprops=dict(arrowstyle="->", color="#e67e22", lw=2, connectionstyle="arc3,rad=0.3"), fontsize=8, color="#e67e22", weight="bold")

# Tier 2 & Tier 3 -> Generator
ax.annotate("", xy=(8.5, 2.7), xytext=(6.5, 3.0), arrowprops=arrow_style)
ax.annotate("", xy=(8.5, 2.5), xytext=(6.5, 1.15), arrowprops=arrow_style)

plt.tight_layout()
plt.savefig('fig1_architecture.png', dpi=300)
plt.close()

print("Successfully generated fig1_architecture.png!")
