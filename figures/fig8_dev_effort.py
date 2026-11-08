import matplotlib
# Use a non-interactive backend so the script can run reproducibly on servers and CI.
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

# Data from Table 7 (Raw LOC and Deployment Time Data per Scenario)
scenarios = ['License\nVerification', 'Enterprise\nQualification\nApproval', 'Real Estate\nRegistration']
native_loc = [3842, 5217, 4593]
dsal_loc = [1687, 2384, 2023]
native_deploy = [120, 185, 156]
dsal_deploy = [45, 72, 61]

loc_reduction = [(n - d) / n * 100 for n, d in zip(native_loc, dsal_loc)]
deploy_reduction = [(n - d) / n * 100 for n, d in zip(native_deploy, dsal_deploy)]

fig, axes = plt.subplots(1, 3, figsize=(14, 4.5))

x = np.arange(len(scenarios))
width = 0.35

# Chart 1: LOC Comparison
bars1 = axes[0].bar(x - width/2, native_loc, width, label='Native', color='#4472C4', edgecolor='black', linewidth=0.5)
bars2 = axes[0].bar(x + width/2, dsal_loc, width, label='DSAL', color='#ED7D31', edgecolor='black', linewidth=0.5)
axes[0].set_ylabel('Lines of Code (LOC)')
axes[0].set_title('(a) Code volume')
axes[0].set_xticks(x)
axes[0].set_xticklabels(scenarios, fontsize=8)
axes[0].legend()
axes[0].grid(axis='y', alpha=0.3)
for bar in bars1:
    axes[0].text(bar.get_x() + bar.get_width()/2., bar.get_height(), f'{int(bar.get_height()):,}',
                ha='center', va='bottom', fontsize=7)
for bar in bars2:
    axes[0].text(bar.get_x() + bar.get_width()/2., bar.get_height(), f'{int(bar.get_height()):,}',
                ha='center', va='bottom', fontsize=7)

# Chart 2: Deployment Time Comparison
bars3 = axes[1].bar(x - width/2, native_deploy, width, label='Native', color='#4472C4', edgecolor='black', linewidth=0.5)
bars4 = axes[1].bar(x + width/2, dsal_deploy, width, label='DSAL', color='#ED7D31', edgecolor='black', linewidth=0.5)
axes[1].set_ylabel('Deployment Time (min)')
axes[1].set_title('(b) Deployment Time Comparison')
axes[1].set_xticks(x)
axes[1].set_xticklabels(scenarios, fontsize=8)
axes[1].legend()
axes[1].grid(axis='y', alpha=0.3)
for bar in bars3:
    axes[1].text(bar.get_x() + bar.get_width()/2., bar.get_height(), f'{int(bar.get_height())}',
                ha='center', va='bottom', fontsize=7)
for bar in bars4:
    axes[1].text(bar.get_x() + bar.get_width()/2., bar.get_height(), f'{int(bar.get_height())}',
                ha='center', va='bottom', fontsize=7)

# Chart 3: Reduction Percentages
bars5 = axes[2].bar(x - width/2, loc_reduction, width, label='LOC Reduction', color='#5B9BD5', edgecolor='black', linewidth=0.5)
bars6 = axes[2].bar(x + width/2, deploy_reduction, width, label='Deploy Time Reduction', color='#FFC000', edgecolor='black', linewidth=0.5)
axes[2].set_ylabel('Reduction (%)')
axes[2].set_title('(c) Efficiency Improvement')
axes[2].set_xticks(x)
axes[2].set_xticklabels(scenarios, fontsize=8)
axes[2].legend()
axes[2].grid(axis='y', alpha=0.3)
axes[2].set_ylim(0, 80)
for bar in bars5:
    axes[2].text(bar.get_x() + bar.get_width()/2., bar.get_height(), f'{bar.get_height():.1f}%',
                ha='center', va='bottom', fontsize=7)
for bar in bars6:
    axes[2].text(bar.get_x() + bar.get_width()/2., bar.get_height(), f'{bar.get_height():.1f}%',
                ha='center', va='bottom', fontsize=7)

plt.tight_layout()
plt.savefig('figure8.png', dpi=300, bbox_inches='tight')
plt.savefig('figure8.pdf', bbox_inches='tight')
plt.close(fig)