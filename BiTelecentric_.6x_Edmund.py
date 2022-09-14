import RayOpticsClasses as roc
import matplotlib.pyplot as pyp
import numpy as np

WD = -103.0
fOBJ = 97.5

locAS = fOBJ

fRL1 = .6 * fOBJ
locRL1 = fOBJ + fRL1

locFS = locRL1 + fRL1

fRL2 = 200
locRL2 = locFS + fRL2

fMLA = 17.5
pMLA = 2.0
locMLA = locRL2 + fRL2


xticks = (WD, 0, fOBJ, locAS, locRL1, locFS, locRL2, locMLA, locMLA + fMLA)
labels = [f"{tick:.1f}" for tick in xticks]


FL  = roc.ThickLens(abs(WD), fOBJ, 0, loc=0, diameter=40)
AS  = roc.Stop(3, loc =locAS)
RL1 = roc.ThinLens(fRL1, diameter=25, loc=locRL1)
FS  = roc.Stop(6, loc=locFS)
RL2 = roc.ThinLens(fRL2, diameter=50, loc=locRL2)
MLA = roc.ThinLensMLA(fMLA, pitch=pMLA, loc=locMLA, diameter=5*pMLA)

TelecentricLens = roc.OpticsSystem([FL, AS, RL1, FS, RL2, MLA], propagate= fMLA)

ps0 = roc.PointSource(WD, 0, .05, color='winter', num=51)
ps5 = roc.PointSource(WD, 6, .05, color='autumn', num=51)
cs00 = roc.CollimatedSource(6, theta=.00, num=71, zstart=-150, color = 'PiYG')
cs05 = roc.CollimatedSource(6 - (150+WD)*.049, r_min= -6-(150+WD)*.05, theta=.02, num=71, zstart=-150, color = 'coolwarm')

TelecentricLens @ ps0
TelecentricLens @ ps5
TelecentricLens @ cs00
TelecentricLens @ cs05


plot_params = {'alpha' : .3}

#%%
fig, (axp, axc) = pyp.subplots(2, figsize = (12,8), sharex = True, sharey=True, dpi=120)


ps0.plot(axp, plot_params)
ps5.plot(axp, plot_params)
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

SystemABCD = TelecentricLens.SYS @ roc.Distance(WD).SYS
M = SystemABCD[0,0]
print(SystemABCD)

axc.set_ylim(-15,15)
axc.set_xlim(-140,650)
fig.suptitle(f"Fourier Plenoptic Camera with Object Space Telecentric Lens\nM = {M:.2f}")

fig.show()
#%%
# axp.set_xlim(200,240)


# fig.show()