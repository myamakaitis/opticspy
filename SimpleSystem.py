import numpy as np
import matplotlib.pyplot as pyp

import RayOpticsClasses as roc

class ObjMLA:
    def __init__(self, fobj, fMLA, pMLA,
                       dAS = np.inf, dFS = np.inf, ):
        self.fobj = fobj
        self.fMLA, self.pMLA = fMLA, pMLA

        self.zObj = 0

        self.A()



    def A(self):
        """Recomputes all objects using parameters in the function"""
        self.OBJ  = roc.ThinLens(self.fobj, loc = self.zObj)
        self.OBJf = roc.Distance(self.fobj)

        self.MLA  = roc.ThinLensMLA(self.fMLA, self.pMLA)
        self.MLAf = roc.Distance(self.fMLA)

        self.elements = [self.OBJ,  self.OBJf,
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

    t_max = .075

    pm2 = roc.PointSource(-1,-.2, .05, num = 21, color='#008080')
    pm1 = roc.PointSource(-1.1,  0, .01, num = 21, color='#00FF00')
    p0  = roc.PointSource(-.9,  0, t_max, num = 111, color = '#0000FF')
    p1  = roc.PointSource( -.9,  0, .031, num = 21, color = '#FF0000')
    p2  = roc.PointSource( -80, .2, .005, num = 21, color = '#808000')
    ps = [pm2, pm1, p0, p1, p2]
    ps = [pm1, p0, p1]
    ps = [p0]

    FLFM = ObjMLA(1,1,pmla)
    Sensor = roc.Image(.04, .0002, intensity=.02)

    fig, ax = pyp.subplots(dpi = 200)
    ax.grid(True)

    ax.hlines([-pmla/2,pmla/2,3/2 * pmla],-1.5,2, color = 'k')
    ax.hlines([pmla +.2* .0375],-1.5,2)

    for p in ps:
        FLFM @ p
        p.plot(ax, {'alpha':.3})

        Sensor + p

    fig.show()
#%%
    Sensor.Display(width = 100)


    cm1 = roc.CollimatedSource(.05, num = 25, theta =-.012, cmap = 'autumn',zstart=-1)
    c0  = roc.CollimatedSource(.05, num = 25, theta =  0,  cmap = 'winter',zstart=-1)
    c1  = roc.CollimatedSource(.05, num = 25, theta = .01, cmap = 'cool',zstart=-1)

    cs = [cm1, c0, c1]

    Sensor = roc.Image(.1, .002, intensity=.2)

    pyp.rcParams.update({"font.family":"serif"})
    fig, ax = pyp.subplots(dpi = 200)

    for c in cs:
        FLFM @ c
        c.plot(ax, {'alpha':.8})
        Sensor + c


    ax.tick_params(axis = 'x', direction = 'inout')
    fig.show()

    Sensor.Display(width=100)