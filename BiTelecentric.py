import matplotlib.pyplot as pyp

from RayOpticsClasses import *

Obj = ThinLens(20, loc = 0)
AS  = Stop(.5, loc = 20)
Lens1 = ThinLens(200, loc = 210)
Lens2 = ThinLens(100, loc = 510)
MLA = ThinLensMLA(6.5, .5, loc = 610)

# ColLight = CollimatedSource(.5)
PointLightfa = PointSource(-20, 0,.005,num = 25, color = '#FF0000')
PointLightf1 = PointSource(-20,.1,.005,num = 25, color = '#FF0000')

PointLightoa = PointSource(-26, 0,.005,num = 25, color = '#00FF00')
PointLighto1 = PointSource(-26,.1,.005,num = 25, color = '#00FF00')

FLFM = OpticsSystem([Obj, AS, Lens1, Lens2, MLA], propagate=6.5)
Sensorf = Image(.1, .002, intensity=.5)
Sensoro = Image(.1, .002, intensity=.5)

FLFM @ PointLightfa
FLFM @ PointLightf1

FLFM @ PointLightoa
FLFM @ PointLighto1

fig, (axf, axo) = pyp.subplots(2)
PointLightfa.plot(axf)
PointLightf1.plot(axf)
Sensorf + PointLightfa
Sensorf + PointLightf1
# Sensorf.Display()

PointLightoa.plot(axo)
PointLighto1.plot(axo)
Sensorf + PointLightoa
Sensorf + PointLighto1
Sensorf.cap()
Sensorf.Display()

fig.show()