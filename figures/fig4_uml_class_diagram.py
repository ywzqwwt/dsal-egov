"""Figure 4. UML class diagram of the e-government domain conceptual model.

Entities and attributes are aligned with the tuple definitions of Section 4.2,
and all five core concepts of that section are represented.
"""
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrowPatch

plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9})
fig, ax=plt.subplots(figsize=(10.5,6.3)); ax.set_xlim(0,10.5); ax.set_ylim(0,6.3); ax.axis('off')

def klass(x,y,w,h,name,attrs,color):
    ax.add_patch(Rectangle((x,y),w,h,facecolor='white',edgecolor='#1F2937',linewidth=1.25))
    ax.add_patch(Rectangle((x,y+h-.48),w,.48,facecolor=color,edgecolor='#1F2937',linewidth=1.25))
    ax.text(x+w/2,y+h-.24,name,ha='center',va='center',fontweight='bold',fontsize=9)
    ax.plot([x,x+w],[y+h-.48,y+h-.48],color='#1F2937',lw=1)
    ax.text(x+.15,y+h-.66,'\n'.join(attrs),ha='left',va='top',fontsize=8,linespacing=1.45)

def rel(a,b,label,where):
    ax.add_patch(FancyArrowPatch(a,b,arrowstyle='-|>',mutation_scale=12,lw=1.2,color='#374151'))
    ax.text(where[0],where[1],label,ha='center',va='center',fontsize=8,color='#374151')

klass(.55,4.05,2.35,1.35,'Organization',['id','name','roleSet'],'#DBEAFE')
klass(4.05,4.25,2.45,1.55,'IsolationDomain',['orgSet','ledgerConfig','accessPolicy'],'#D1FAE5')
klass(4.05,.75,2.45,1.75,'BusinessFlow',['V, E','roleMap','policySet'],'#FEF3C7')
klass(7.6,2.4,2.35,1.75,'PermissionPolicy',['resource','action','roleSet','constraint'],'#FCE7F3')
klass(.55,1.05,2.6,1.30,'Unified Smart Contract',['interface','stateVars','events'],'#E0E7FF')

rel((2.9,4.72),(4.05,4.98),'participates in',(3.47,5.28))
rel((5.25,4.25),(5.25,2.55),'contains / scopes',(6.0,3.4))
rel((6.5,1.65),(7.6,2.9),'uses',(7.1,2.0))
rel((6.5,4.9),(7.6,3.7),'governs access in',(7.05,4.5))
rel((4.05,1.30),(3.15,1.55),'invokes',(3.60,1.22))
ax.text(5.25,5.95,'E-Government Domain Conceptual Model Used by the DSAL Prototype',ha='center',fontsize=12,fontweight='bold')
ax.text(5.25,.12,'Entities and attributes correspond to the tuple definitions given in Section 4.2.',ha='center',fontsize=8,color='#4B5563')
plt.tight_layout(); plt.savefig('figure4.png',dpi=300,bbox_inches='tight'); plt.savefig('figure4.pdf',bbox_inches='tight')
