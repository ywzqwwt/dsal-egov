"""Figure 7. Sequence of a cross-platform invocation through DSAL."""
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrowPatch

plt.rcParams.update({'font.family':'DejaVu Sans','font.size':8})
actors=['Application','DSAL API /\nCoordinator','Concept\nMapping','Business Logic\nTranslator','Fabric\nAdapter/Network','FISCO BCOS\nAdapter/Network','etcd\nlog']
x=[.8,2.4,4.0,5.6,7.25,8.95,10.65]
fig,ax=plt.subplots(figsize=(12,8)); ax.set_xlim(.2,11.3); ax.set_ylim(0,10); ax.axis('off')
for xi,a in zip(x,actors):
    ax.add_patch(Rectangle((xi-.62,9.25),1.24,.52,facecolor='#E5E7EB',edgecolor='#374151',lw=1))
    ax.text(xi,9.51,a,ha='center',va='center',fontweight='bold')
    ax.plot([xi,xi],[.55,9.25],ls='--',lw=.8,color='#9CA3AF')
def msg(y,fr,to,text,style='-'):
    i=actors.index(fr); j=actors.index(to)
    ax.add_patch(FancyArrowPatch((x[i],y),(x[j],y),arrowstyle='-|>',mutation_scale=10,lw=1.05,color='#1F2937',linestyle=style))
    ax.text((x[i]+x[j])/2,y+.14,text,ha='center',va='bottom',fontsize=7.3,wrap=True)
msg(8.55,'Application','DSAL API /\nCoordinator','1. invokeCrossDomainTransaction(flow)')
msg(7.85,'DSAL API /\nCoordinator','Concept\nMapping','2. map abstract concepts')
msg(7.15,'Concept\nMapping','DSAL API /\nCoordinator','3. mapped platform constructs',':')
msg(6.45,'DSAL API /\nCoordinator','Business Logic\nTranslator','4. translate workflow and policy')
msg(5.75,'Business Logic\nTranslator','DSAL API /\nCoordinator','5. native execution plan',':')
msg(5.05,'DSAL API /\nCoordinator','Fabric\nAdapter/Network','6. Phase 1: prepare / lock')
msg(4.35,'DSAL API /\nCoordinator','FISCO BCOS\nAdapter/Network','7. Phase 1: prepare / lock')
msg(3.65,'DSAL API /\nCoordinator','etcd\nlog','8. persist coordinator state')
msg(2.95,'DSAL API /\nCoordinator','Fabric\nAdapter/Network','9. Phase 2: commit or abort')
msg(2.25,'DSAL API /\nCoordinator','FISCO BCOS\nAdapter/Network','10. Phase 2: commit or abort')
msg(1.55,'DSAL API /\nCoordinator','etcd\nlog','11. record final state')
msg(.85,'DSAL API /\nCoordinator','Application','12. success / failure response')
ax.text(5.75,.25,'The sequence depicts the documented prepare, persistent-state, and commit/abort behavior; recovery details remain bounded by Section 5.2.',ha='center',fontsize=7.4,color='#4B5563')
plt.tight_layout(); plt.savefig('figure7.png',dpi=300,bbox_inches='tight'); plt.savefig('figure7.pdf',bbox_inches='tight')
