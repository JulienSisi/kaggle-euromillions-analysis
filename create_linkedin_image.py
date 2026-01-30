"""
Create a professional LinkedIn post image for EuroMillions Analysis project.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import numpy as np

# Create figure
fig = plt.figure(figsize=(12, 8))
fig.patch.set_facecolor('#FFFFFF')

# Main title section (top)
ax_title = plt.subplot2grid((4, 2), (0, 0), colspan=2, rowspan=1)
ax_title.axis('off')

# Title
ax_title.text(0.5, 0.7, 'EuroMillions Analysis',
             ha='center', va='center', fontsize=32, fontweight='bold',
             color='#1a1a1a')
ax_title.text(0.5, 0.3, '8 Analytical Methods vs Random Selection',
             ha='center', va='center', fontsize=18, color='#4a4a4a')

# ROI Comparison (center-left)
ax_roi = plt.subplot2grid((4, 2), (1, 0), colspan=1, rowspan=2)

categories = ['Analytical\nMethods', 'Random\nSelection']
roi_values = [-89.63, -89.86]
colors = ['#FF6B6B', '#4ECDC4']

bars = ax_roi.bar(categories, roi_values, color=colors, alpha=0.8,
                  edgecolor='black', linewidth=2)

# Add value labels on bars
for i, (bar, value) in enumerate(zip(bars, roi_values)):
    height = bar.get_height()
    ax_roi.text(bar.get_x() + bar.get_width()/2., height - 5,
                f'{value:.2f}%',
                ha='center', va='top', fontsize=16, fontweight='bold',
                color='white')

# Reference line at -50%
ax_roi.axhline(y=-50, color='red', linestyle='--', linewidth=2,
               alpha=0.7, label='Theoretical ROI')
ax_roi.text(1.5, -48, 'Theoretical: -50%', fontsize=11,
            color='red', ha='center')

ax_roi.set_ylabel('ROI (%)', fontsize=14, fontweight='bold')
ax_roi.set_title('Return on Investment', fontsize=16, fontweight='bold', pad=15)
ax_roi.set_ylim(-100, 0)
ax_roi.grid(True, alpha=0.3, axis='y')
ax_roi.spines['top'].set_visible(False)
ax_roi.spines['right'].set_visible(False)
ax_roi.tick_params(labelsize=12)

# Key Findings (center-right)
ax_findings = plt.subplot2grid((4, 2), (1, 1), colspan=1, rowspan=2)
ax_findings.axis('off')

# Key finding box
finding_box = FancyBboxPatch((0.05, 0.6), 0.9, 0.35,
                            boxstyle="round,pad=0.02",
                            facecolor='#FFF3E0',
                            edgecolor='#FF9800',
                            linewidth=3)
ax_findings.add_patch(finding_box)

ax_findings.text(0.5, 0.85, '🔬 Key Finding',
                ha='center', va='center', fontsize=16, fontweight='bold',
                color='#E65100')

ax_findings.text(0.5, 0.73, 'Difference: 0.23%',
                ha='center', va='center', fontsize=20, fontweight='bold',
                color='#1a1a1a')

ax_findings.text(0.5, 0.65, 'p = 0.973 (NOT significant)',
                ha='center', va='center', fontsize=14,
                color='#d32f2f', fontweight='bold')

# Statistics box
ax_findings.text(0.5, 0.48, '📊 Sample Statistics',
                ha='center', va='center', fontsize=14, fontweight='bold',
                color='#1565C0')

stats_text = """
Real Games: 134
Simulations: 1,000 per method
Investment: 469 CHF
Period: 2020-2023
"""

ax_findings.text(0.5, 0.25, stats_text,
                ha='center', va='center', fontsize=11,
                color='#424242', linespacing=1.6)

# Conclusion section (bottom)
ax_conclusion = plt.subplot2grid((4, 2), (3, 0), colspan=2, rowspan=1)
ax_conclusion.axis('off')

# Conclusion box
conclusion_box = FancyBboxPatch((0.05, 0.15), 0.9, 0.7,
                               boxstyle="round,pad=0.02",
                               facecolor='#E8F5E9',
                               edgecolor='#4CAF50',
                               linewidth=3)
ax_conclusion.add_patch(conclusion_box)

ax_conclusion.text(0.5, 0.7, '💡 Conclusion: Math Cannot Beat Math',
                  ha='center', va='center', fontsize=16, fontweight='bold',
                  color='#1B5E20')

conclusion_text = 'Analytical methods create cognitive bias but provide NO statistical advantage'
ax_conclusion.text(0.5, 0.45, conclusion_text,
                  ha='center', va='center', fontsize=13,
                  color='#2E7D32', style='italic')

# Footer
ax_conclusion.text(0.5, 0.15, 'Full Analysis: github.com/JulienSisi/kaggle-euromillions-analysis',
                  ha='center', va='center', fontsize=11,
                  color='#1976D2', weight='bold')

plt.tight_layout()
plt.savefig('outputs/linkedin_post_image.png', dpi=300, bbox_inches='tight',
            facecolor='white', edgecolor='none')
print("✅ LinkedIn image created: outputs/linkedin_post_image.png")
print("   Size: 1200x800 pixels (optimized for LinkedIn)")
