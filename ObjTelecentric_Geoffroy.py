import RayOpticsClasses as roc
import matplotlib.pyplot as pyp
import numpy as np

ObjLoc = -81.5

dx1 = 40.6
dx2 = 54.6

fFL = 65.9
fRL1 = -36.9
fRL2 = 200
fMLA = 17.5
# img_distance = 58.814

dimg = 219.9
dRL = 258.814#400
dMLA = 694.8

xticks = (ObjLoc, 0, dx1, dx1 + fFL,dx1 + fFL + dx2 , dimg, dx1 + fFL + dx2 + dRL,
          dx1 + fFL + dx2 + dRL + dMLA)
labels = [f"{tick:.1f}" for tick in xticks]


FL  = roc.ThinLens(fFL, loc=dx1, diameter=43)
AS  = roc.Stop(5, loc = dx1 + fFL)
RL1 = roc.ThinLens(fRL1, diameter=33, loc = dx1 + fFL + dx2)
FS  = roc.Stop(15.5, loc=dimg)
RL2 = roc.ThinLens(fRL2, diameter=50, loc = dx1 + fFL + dx2 + dRL)
MLA = roc.ThinLensMLA(fMLA, pitch=2, loc = dx1 + fFL + dx2 + dRL + dMLA)

TelecentricLens = roc.OpticsSystem([FL, AS, RL1, FS, RL2, MLA], propagate= fMLA)

ps = roc.PointSource(ObjLoc, 0, .1, color='winter', num=51)
ps7 = roc.PointSource(ObjLoc, 5, .1, color='autumn', num=51)
cs00 = roc.CollimatedSource(6, theta=.00, num=71, zstart=-150, color = 'PiYG')
cs05 = roc.CollimatedSource(6 - (150+ObjLoc)*.05, r_min= -6-(150+ObjLoc)*.05, theta=.05, num=71, zstart=-150, color = 'coolwarm')

TelecentricLens @ ps
TelecentricLens @ ps7
TelecentricLens @ cs00
TelecentricLens @ cs05


plot_params = {'alpha' : .3}

#%%
fig, (axp, axc) = pyp.subplots(2, figsize = (12,8), sharex = True, sharey=True, dpi=120)


ps.plot(axp, plot_params)
ps7.plot(axp, plot_params)
cs00.plot(axc, plot_params)
cs05.plot(axc, plot_params)

for ax in (axp, axc):
    TelecentricLens.plot(ax)
    ax.set_ylabel('R [mm]')
axc.set_xlabel('Z [mm]')

axp.set_title("Point Sources at Working Distance")
axc.set_title("Collimated Sources")
axc.set_xticks(xticks, labels)
axc.tick_params(axis='x', direction='inout', labelrotation=45)

SystemABCD = TelecentricLens.SYS @ roc.Distance(-ObjLoc + dx1).SYS
M = SystemABCD[0,0]

axc.set_xlim(-140,1150)
fig.suptitle(f"Fourier Plenoptic Camera with Object Space Telecentric Lens\nM = {M:.2f}")

fig.show()
#%%
axp.set_xlim(200,240)


fig.show()