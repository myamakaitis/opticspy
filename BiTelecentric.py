import matplotlib.pyplot as pyp

from RayOpticsClasses import *

Obj = ThickLens(120, 180, 15, loc = 0)
AS  = Stop(.5, loc = 180)
Lens1 = ThinLens(50, loc = 230)
Lens2 = ThinLens(50, loc = 330)
MLA = ThinLensMLA(25, .05, loc = 380)

ColLight = CollimatedSource(.5)
PointLight = PointSource(-350, 1, .005, num = 501, color = 'autumn')

FLFM = OpticsSystem([Obj, AS, Lens1, Lens2, MLA], propagate = 50)

fig, ax = pyp.subplots()
FLFM @ ColLight
ColLight.plot(ax)
fig.show()

fig, ax = pyp.subplots()
FLFM @ PointLight
PointLight.plot(ax, {'alpha': .1})
fig.show()