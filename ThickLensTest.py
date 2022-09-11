import numpy as np
import matplotlib.pyplot as pyp

import RayOpticsClasses as roc

f1 = 120
f2 = 180
zlens = 15

A = 1
B = zlens
C = -1/f1
D = f2 / f1

B = zlens
C = -1/np.sqrt(f1*f2)
D = -f1 * C
A = -f2 * C

Test = roc.ABCD(A,B,C,D)
TestRev = roc.ABCD(D,B,C,A)
TestRev = Test

# ThickLens = roc.ThickLens(f1, f2, zlens, loc = 0.0)
# ThickLensRev = roc.ThickLens(f2, f1, zlens, loc = 0.0)

# LensSystem    = roc.OpticsSystem([ThickLens], propagate=100)
# LensSystemRev = roc.OpticsSystem([ThickLensRev], propagate=100)
TestSystem    = roc.OpticsSystem([Test], propagate=200+zlens)
TestSystemRev = TestSystem.Reverse()

# ps12 = roc.PointSource(-f1,0,.3, num = 25)
# ps18 = roc.PointSource(-(.01365741)**-1,0,.2, color = '#00FF00')
# csf = roc.CollimatedSource(r_max = 25, zstart = -50)
# csr = roc.CollimatedSource(r_max = 25, zstart = -50)
cstm  = roc.CollimatedSource(r_max = 25, zstart = -200)
cstmr = roc.CollimatedSource(r_max = 25, theta=0, zstart = 200)

pstm  = roc.PointSource(-f1, 0, .2, num =25)
pstmr = roc.PointSource( f2, 0, .1, num = 25)

fig, ((ax1, ax2), (ax3, ax4)) = pyp.subplots(2, 2, sharex=True, sharey=True)

# LensSystem @ ps12
# LensSystem @ ps18
# ps12.plot(ax1)
# ps18.plot(ax2)

# LensSystem @ csf
# LensSystemRev @ csr
TestSystem @ cstm
TestSystemRev @ cstmr

TestSystem @ pstm
TestSystemRev @ pstmr
# csf.plot(ax1)
# csr.plot(ax2)
cstm.plot(ax1)
cstmr.plot(ax2)
pstm.plot(ax3)
pstmr.plot(ax4)

for ax in (ax1, ax2, ax2, ax4):
    ax.set_xticks([-f2, -f1, 0, zlens, f1+zlens, f2+zlens])
    ax.grid('True')

fig.show()

print(TestSystem[0].__class__.__name__)
