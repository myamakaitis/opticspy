import numpy as np
import lin2d
from ..rays.rays4d import Ray, Path

class mat4d():
    def __init__(self, z: float, n : float = 1):
        self.SYS = np.identity(6, dtype=np.float64)
        self.z = z
        self.n = n

    def __matmul__(self, element):
        return self.SYS @ element.SYS

    def Tform(self, path: Path):
        if self.TformCondition(path):
            new_state = self.SYS @ path.state
            return Ray(*new_state, n=self.n, color=path.color)

    def TformCondition(self, _: Path):
        return True

class ABCD4d(mat4d):
    def __init__(self, sys2d: lin2d.ABCD):
        super().__init__(self, sys2d.z)
        self.set_ABCD(sys2d.SYS)

    def set_ABCD(self, sys2d_mat):
        self.set_ABCD1(sys2d_mat)
        self.set_ABCD2(sys2d_mat)
        self.SYS[4,5] = sys2d_mat[0,1]

    def set_ABCD1(self, sys2d_mat):
        self.SYS[:2,:2] = sys2d_mat

    def set_ABCD2(self, sys2d_mat):
        self.SYS[2:5, 2:5] = sys2d_mat



class ThinLens(ABCD4d):
    def __init__(self, f, d, loc):
        thinlens = lin2d.ThinLens(f, d, loc)
        super().__init__(thinlens)
        self.f = f
        self.d = d


class Distance(ABCD4d):
    def __init__(self, dz):
        distance = lin2d.Distance(dz)
        super().__init__(distance)


class Prism(mat4d):
    def __init__(self, angle, loc):
        super().__init__(loc)
        self.SYS[(1,3),5] = angle


class StopCirc(mat4d):
    def __init__(self, r, loc=None):
        super().__init__(loc)
        self.R2 = r**2

    def TformCondition(self, path: Path):
        x, y, _, _ = path.state
        r = x**2 + y**2
        if r > self.R2:
            path.halt = True
            return False
        else:
            return True

class ThinLensMLA(ThinLens):
    def __init__(self, f, pitch, d, pattern: str,  loc: np.float64):
        super().__init__(f, d, loc=loc)
        self.p = pitch
        self.pattern = pattern

        if pattern == 'hex':
            self.hex_centers()
        elif pattern == 'rect':
            self.rect_centers()
        else:
            raise ValueError("Invalid Pattern")

    def hex_centers(self):
        r_limit = (self.d + self.p) / 2
        y, x = 0, 0

        centers = []

        ii = 0
        while y < r_limit:
            while (x**2 + y**2) < r_limit**2:
                centers.append(( x,  y))
                centers.append((-x, -y))
                centers.append((-x,  y))
                centers.append(( x, -y))
                x += self.p

            y += np.cos(np.deg2rad(30))*self.pitch
            if ii % 2:
                x = .5*self.p
            else:
                x = 0

        self.centers = np.array(centers)

    def rect_centers(self):
        r_limit = (self.d + self.p) / 2
        y, x = 0, 0

        centers = []


        while y < r_limit:
            while (x ** 2 + y ** 2) < r_limit ** 2:
                centers.append((x, y))
                centers.append((-x, -y))
                centers.append((-x, y))
                centers.append((x, -y))
                x += self.p

            y += self.pitch
            x = 0

        self.centers = np.array(centers)

    def Tform(self, path: Path):
        if self.TformCondition(path):
            #              ray x        lenslet x
            lens_idx = ((path.state[0] - self.centers[:,0])**2 + (path.state[1] - self.centers[:,2])**2).argmin()
            sx, sy = self.centers[lens_idx] # shift x , shift y


            new_state = self.SYS @ path.state + np.array([0, sx / self.f, 0, sy/self.f, 0, 0, 0])
            return Ray(*new_state, n=self.n, color=path.color)




