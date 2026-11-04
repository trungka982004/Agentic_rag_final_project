import matplotlib.pyplot as plt
import numpy as np

# Set standard IEEE publication typography and style
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['Times New Roman', 'DejaVu Serif', 'STIXGeneral']
plt.rcParams['mathtext.fontset'] = 'stix'
plt.rcParams['axes.edgecolor'] = '#333333'
plt.rcParams['axes.linewidth'] = 0.85

# Single-column IEEE width proportion (~3.5 in wide, proportioned for 300 DPI)
fig, ax = plt.subplots(figsize=(6.8, 4.3), dpi=300)

# Exact empirical values from Table I of the paper
# Distinct geometric markers for clear black-and-white print readability
models = [
    {
        'name': 'Naive RAG',
        'cost': 0.00,
        'faith': 0.49,
        'err': 0.05,
        'marker': 's',       # Square
        'mfc': '#E2E8F0',
        'mec': '#334155',
        'ms': 7.5,
        'label_pos': (0.12, 0.470),
        'ha': 'left',
        'va': 'center'
    },
    {
        'name': 'Advanced RAG',
        'cost': 0.00,
        'faith': 0.51,
        'err': 0.04,
        'marker': '^',       # Triangle up
        'mfc': '#94A3B8',
        'mec': '#1E293B',
        'ms': 8.0,
        'label_pos': (0.12, 0.520),
        'ha': 'left',
        'va': 'center'
    },
    {
        'name': 'Adaptive-RAG',
        'cost': 1.50,
        'faith': 0.53,
        'err': 0.04,
        'marker': 'D',       # Diamond
        'mfc': '#C7D2FE',
        'mec': '#3730A3',
        'ms': 7.0,
        'label_pos': (1.50, 0.465),
        'ha': 'center',
        'va': 'top'
    },
    {
        'name': 'CRAG',
        'cost': 3.20,
        'faith': 0.54,
        'err': 0.04,
        'marker': 'X',       # X / Cross
        'mfc': '#FDE68A',
        'mec': '#92400E',
        'ms': 8.0,
        'label_pos': (3.26, 0.54),
        'ha': 'left',
        'va': 'center'
    },
    {
        'name': 'Self-RAG',
        'cost': 1.80,
        'faith': 0.58,
        'err': 0.04,
        'marker': 'o',       # Circle
        'mfc': '#BAE6FD',
        'mec': '#0369A1',
        'ms': 7.5,
        'label_pos': (1.92, 0.58),
        'ha': 'left',
        'va': 'center'
    },
    {
        'name': 'Proposed Agentic RAG (Ours)',
        'cost': 0.90,
        'faith': 0.62,
        'err': 0.04,
        'marker': '*',       # Star
        'mfc': '#B91C1C',
        'mec': '#000000',
        'ms': 13.0,
        'label_pos': (0.90, 0.685),
        'ha': 'center',
        'va': 'bottom'
    },
]

# Discrete subtle grid
ax.grid(True, linestyle=':', linewidth=0.6, alpha=0.6, color='#94A3B8', zorder=1)

# Stepped Pareto optimal frontier (Advanced RAG at (0, 0.51) and Proposed at (0.9, 0.62))
pareto_x = [0.00, 0.90, 3.85]
pareto_y = [0.51, 0.62, 0.62]
ax.step(pareto_x, pareto_y, where='post', color='#1E3A8A', linestyle='--', linewidth=1.8, 
        label='Empirical Non-dominated Frontier', zorder=2)

# Plot points and error bars
for m in models:
    is_ours = 'Ours' in m['name']
    
    # Error bars: standard deviation on faithfulness across 5 runs
    ax.errorbar(m['cost'], m['faith'], yerr=m['err'], fmt='none',
                ecolor='#64748B' if not is_ours else '#991B1B', 
                elinewidth=1.1 if not is_ours else 1.3, 
                capsize=3.5, capthick=1.1, zorder=3)
    
    # Marker plot
    ax.plot(m['cost'], m['faith'], marker=m['marker'], markersize=m['ms'],
            markerfacecolor=m['mfc'], markeredgecolor=m['mec'], markeredgewidth=1.1 if is_ours else 0.9,
            linestyle='none', zorder=4)
    
    # Direct label with cost and score - enhanced font size for readability
    weight = 'bold' if is_ours else 'normal'
    fontcolor = '#0F172A'
    fontsize = 8.8 if is_ours else 8.2
    
    txt = f"{m['name']}\n(${m['cost']:.2f}, {m['faith']:.2f})"
    
    if is_ours:
        bbox_props = dict(boxstyle='square,pad=0.25', facecolor='#FEF2F2', edgecolor='#991B1B', linewidth=0.85)
    else:
        bbox_props = None
        
    ax.annotate(txt,
                xy=(m['cost'], m['faith']),
                xytext=m['label_pos'],
                fontsize=fontsize,
                fontweight=weight,
                color=fontcolor,
                ha=m['ha'],
                va=m['va'],
                bbox=bbox_props,
                zorder=5)

# Axis labels & ranges: X-axis strictly non-negative (cost cannot be negative)
ax.set_xlabel('Marginal API Cost per 1,000 Queries (USD $)', fontsize=9.2, fontweight='bold', labelpad=6)
ax.set_ylabel('Faithfulness (RAGAS Metric, [0, 1])', fontsize=9.2, fontweight='bold', labelpad=6)
ax.set_xlim(-0.08, 3.85)
ax.set_ylim(0.42, 0.73)

# Professional ticks with clean start from 0
ax.set_xticks([0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5])
ax.tick_params(axis='both', which='major', labelsize=8.2, direction='in', top=True, right=True)

# Clean, single-item legend for the frontier line only
ax.legend(loc='lower right', frameon=True, edgecolor='#CBD5E1', facecolor='white', framealpha=0.95, fontsize=8.2)

plt.tight_layout()

# Save to destination
output_path = 'science_paper_assets/science_paper_images/fig4_pareto_chart.png'
plt.savefig(output_path, dpi=300, bbox_inches='tight')
print(f"Successfully generated clean academic Pareto chart at: {output_path}")
