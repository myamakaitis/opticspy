import numpy as np
import matplotlib.pyplot as pyp

import RayOpticsClasses as roc

class BiTelecentricFLFM:
    def __init__(self, fobj, frl1, frl2, fMLA, pMLA,
                       dAS = np.inf, dFS = np.inf, ):
        self.fobj, self.frl1, self.frl2, = fobj, frl1, frl2
        self.fMLA, self.pMLA = fMLA, pMLA
        self.rAS,  self.rFS = dAS/2, dFS/2

        self.zObj = 0

        self.A()



    def A(self):
        """Recomputes all objects using parameters in the function"""
        self.OBJ  = roc.ThinLens(self.fobj, loc = self.zObj)
        self.OBJf = roc.Distance(self.fobj)
        self.AS   = roc.Stop(self.rAS)
        self.RL1f = roc.Distance(self.frl1)
        self.RL1  = roc.ThinLens(self.frl1)

        self.FS   = roc.Stop(self.rFS)
        self.RL2f = roc.Distance(self.frl2)
        self.RL2  = roc.ThinLens(self.frl2)

        self.MLA  = roc.ThinLensMLA(self.fMLA, self.pMLA)
        self.MLAf = roc.Distance(self.fMLA)

        self.elements = [self.OBJ,  self.OBJf, self.AS,
                         self.RL1f, self.RL1,  self.RL1f,
                         self.FS,
                         self.RL2f, self.RL2,  self.RL2f,
                         self.MLA, self.MLAf]

    def calcPath(self, ray):
        dobj = roc.Distance(self.OBJ.z - ray.z)
        dobj @ ray

        for element in self.elements:
            element @ ray



    def __matmul__(self, ray):
        if hasattr(ray, '__getitem__'):
            for ii in range(len(ray)):
                self.calcPath(ray[ii])
        else: self.calcPath(ray)

if __name__ == '__main__':
    fmla = 60
    pmla = .05

    pm2 = roc.PointSource(-120,-.2, .005, num = 501, color='#008080')
    pm1 = roc.PointSource(-130,  0, .0031, num = 501, color='#00FF00')
    p0  = roc.PointSource(-150,  .3, .0051, num = 501, color = 'viridis')
    p1  = roc.PointSource( -70,  0, .0031, num = 501, color = '#FF0000')
    p2  = roc.PointSource( -80, .2, .005, num = 501, color = '#808000')
    ps = [pm2, pm1, p0, p1, p2]
    ps = [pm1, p0, p1]
    # ps = [p0]

    FLFM = BiTelecentricFLFM(100,40,40,fmla,pmla,dAS = .6, dFS = .1)
    Sensor = roc.Image(.4, .008, intensity=.01)

    fig, ax = pyp.subplots(dpi = 200)

    for p in ps:
        FLFM @ p
        p.plot(ax, {'alpha':.05})

        Sensor + p

    fig.show()

    Sensor.Display(width = 100)

    cm1 = roc.CollimatedSource(.2, num = 25, theta =-.004, color = 'autumn')
    c0  = roc.CollimatedSource(.4, num = 51, theta =  0,  color = 'winter',zstart=-200)
    c1  = roc.CollimatedSource(.2, num = 25, theta = .002, color = 'cool')

    cs = [cm1, c0, c1]

    FLFM = BiTelecentricFLFM(100,40,40,40,.1,dAS = .6, dFS = .1)
    Sensor = roc.Image(.4, .002, intensity=.2)

    pyp.rcParams.update({"font.family":"serif"})
    fig, ax = pyp.subplots(dpi = 200)

    for c in cs:
        FLFM @ c
        c.plot(ax, {'alpha':.3})
        Sensor + c

    ax.tick_params(axis = 'x', direction = 'inout')
    # ax.axis('off')
    fig.show()

    Sensor.Display(width=100)