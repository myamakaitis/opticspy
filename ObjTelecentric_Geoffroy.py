import RayOpticsClasses as roc
import matplotlib.pyplot as pyp

ObjLoc = -81.5

dx1 = 40.6
dx2 = 54.6

fFL = 65.9
fRL1 = -36.9
fRL2 = 200
fMLA = 17.5
img_distance = 58.814


FL  = roc.ThinLens(fFL, loc=dx1, diameter=43)
AS  = roc.Stop(10, loc = dx1 + fFL)
RL1 = roc.ThinLens(fRL1, diameter=33, loc = dx1 + fFL + dx2)
RL2 = roc.ThinLens(fRL2, diameter=50, loc = dx1 + fFL + dx2 + img_distance + fRL2)
MLA = roc.ThinLensMLA(fMLA, pitch=2, loc = dx1 + fFL + dx2 + img_distance + fRL2 + fRL2)

TelecentricLens = roc.OpticsSystem([FL, AS, RL1], propagate = img_distance)
PlenopticCam = roc.OpticsSystem([FL, AS, RL1, RL2, MLA], propagate= fMLA)

ps = roc.PointSource(ObjLoc, 0, .03, color='winter', num=25)
cs = roc.CollimatedSource(5, num=21, zstart=ObjLoc, color = 'autumn')

PlenopticCam @ ps
TelecentricLens @ cs



plot_params = {'alpha' : .5}
fig, (axp, axc) = pyp.subplots(2, figsize = (12,5))#, sharex = True)


ps.plot(axp, plot_params)
cs.plot(axc, plot_params)

PlenopticCam.plot(axp)
TelecentricLens.plot(axc)

fig.show()