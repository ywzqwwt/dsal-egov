"""Figure 2. Formal problem definition of DSAL.
All labels follow Section 2.2 of the manuscript.
"""
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 9})
fig, ax = plt.subplots(figsize=(10.5, 5.8))
ax.set_xlim(0, 10.5); ax.set_ylim(0, 5.8); ax.axis('off')

def box(x, y, w, h, title, lines, color):
    patch = FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.04,rounding_size=0.08',
                           facecolor=color, edgecolor='#1F2937', linewidth=1.2)
    ax.add_patch(patch)
    ax.text(x+w/2, y+h-0.34, title, ha='center', va='center', fontsize=10, fontweight='bold')
    ax.text(x+w/2, y+h/2-0.15, '\n'.join(lines), ha='center', va='center', fontsize=8.3, linespacing=1.45)

def arrow(x1,y1,x2,y2,label=None,dy=0.12):
    ax.add_patch(FancyArrowPatch((x1,y1),(x2,y2),arrowstyle='-|>', mutation_scale=13,
                                 linewidth=1.25,color='#374151'))
    if label: ax.text((x1+x2)/2, (y1+y2)/2+dy, label, ha='center', va='center', fontsize=9, fontweight='bold')

box(0.35, 3.35, 2.25, 1.45, 'Fabric conceptual model',
    [r'$M_1=(C_1,R_1)$', 'Channel · Chaincode', 'Endorsement policy'], '#DBEAFE')
box(0.35, 1.0, 2.25, 1.45, 'FISCO BCOS conceptual model',
    [r'$M_2=(C_2,R_2)$', 'Group · Contract', 'RBAC / permission table'], '#D1FAE5')
box(4.0, 2.1, 2.5, 1.65, 'Unified DSAL model',
    [r'$M_{DSAL}=(C_{DSAL},R_{DSAL})$', 'Isolation Domain', 'Business Flow · Permission Policy'], '#FEF3C7')
box(7.9, 2.1, 2.25, 1.65, 'Platform-specific artifacts',
    [r'$T(B,P_j)$', 'Native workflow logic', 'Native permission artifact'], '#FCE7F3')
arrow(2.6,4.05,4.0,3.2,r'$\phi_1$',0.2); arrow(4.0,2.65,2.6,3.7,r'$\psi_1$',-0.28)
arrow(2.6,1.75,4.0,2.65,r'$\phi_2$',-0.25); arrow(4.0,2.25,2.6,1.4,r'$\psi_2$',0.22)
arrow(6.5,2.92,7.9,2.92,r'$T(B,P_j)$',0.2)
box(3.2, 0.2, 4.1, 0.95, 'Required constraints',
    ['Semantic mapping  |  Logic translation  |  Constraint satisfaction'], '#F3F4F6')
ax.text(5.25,5.35,'Formal Interoperability Problem Addressed by DSAL',ha='center',fontsize=13,fontweight='bold',color='#111827')
ax.text(5.25,0.0,'Mappings preserve stated semantics; generated artifacts must satisfy the stated security and performance constraints.',ha='center',fontsize=8,color='#4B5563')
plt.tight_layout()
plt.savefig('figure2.png', dpi=300, bbox_inches='tight')
plt.savefig('figure2.pdf', bbox_inches='tight')
