"""Figure 5. Illustrative declarative business-logic translation rule."""
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9})
fig,ax=plt.subplots(figsize=(11,5.4)); ax.set_xlim(0,11); ax.set_ylim(0,5.4); ax.axis('off')
def panel(x,y,w,h,title,body,color):
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.05,rounding_size=.08',facecolor=color,edgecolor='#1F2937',lw=1.25))
    ax.text(x+w/2,y+h-.35,title,ha='center',va='center',fontweight='bold',fontsize=10)
    ax.text(x+w/2,y+h/2-.2,body,ha='center',va='center',fontsize=8.3,linespacing=1.45,family='DejaVu Sans Mono')
def arr(a,b): ax.add_patch(FancyArrowPatch(a,b,arrowstyle='-|>',mutation_scale=14,lw=1.3,color='#374151'))
ax.text(5.5,4.95,'Illustrative Declarative Business-Logic Translation Rule',ha='center',fontsize=13,fontweight='bold')
panel(.45,1.5,2.6,2.45,'Input predicates','Flow.Type = Approval\nPlatform = Fabric\nPermission =\nSingleAuthority', '#DBEAFE')
panel(4.1,1.15,2.8,3.1,'Rule evaluation','IF Flow.Type = Approval\nAND Platform = Fabric\nTHEN generate platform\nartifact for the workflow-\ndefined permission rule', '#FEF3C7')
panel(7.95,1.5,2.6,2.45,'Generated artifact','Fabric:\nOR(\'CommerceMSP.admin\')\n\nFISCO BCOS:\nCorresponding RBAC rule', '#D1FAE5')
arr((3.05,2.72),(4.1,2.72)); arr((6.9,2.72),(7.95,2.72))
ax.text(5.5,.55,'For a multi-party workflow, the same abstract policy supplies an explicit threshold that is translated to the applicable platform constraint.',ha='center',fontsize=8,color='#4B5563')
plt.tight_layout(); plt.savefig('figure5.png',dpi=300,bbox_inches='tight'); plt.savefig('figure5.pdf',bbox_inches='tight')
