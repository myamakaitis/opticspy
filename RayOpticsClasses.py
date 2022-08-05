import numpy as np
import matplotlib.pyplot as pyp
from matplotlib import cm


def rgb2hex(rgb):
    """
    Converts from array rgb values to hex string
    :param rgb: Array of rbg values
    :return: String of hex values
    """

    if len(rgb) != 3:
        raise ValueError("RBG Array wrong size")
    elif max(rgb) > 255:
        raise ValueError("Maximum RBG value is 255")
    elif np.mean(rgb) < 1:
        rgb = [255*v for v in rgb]

    return f"#{int(rgb[0]):02x}{int(rgb[1]):02x}{int(rgb[2]):02x}"


def hex2rgb(hex_str):
    if len(hex_str) != 7:
        raise ValueError("Hex String must be 7 characters")

    r, g, b = '0x' + hex_str[1:3], '0x' + hex_str[3:5], '0x' + hex_str[5:]
    r, g, b = int(r,0), int(g,0), int(b,0)

    return r,g,b



class Ray:
    def __init__(self, theta, r, n_current = 1, color = '#FFFFFF'):
        #self.t = theta
        #self.r = r
        self.n = n_current
        self.stopped = False #has to be done before self.rt

        self.rt = np.array([r, theta])
        
        self.dx, self.dy = np.cos(theta), np.sin(theta)
        self.slope = np.array([self.dx, self.dy])

        self.color = color


    def get_rgb(self):
        return hex2rgb(self.color)


class Path(Ray):
    def __init__(self, theta, r, z = -np.inf, n_current = 1, color = '#000000'):
        self.Pstates = []
        self.tstates = []
        self.z = z
        super().__init__(theta, r, n_current=n_current, color=color)



    @property
    def rt(self):
        return self._rt

    @rt.setter
    def rt(self, value):
        if self.stopped:
            return

        self._rt = value
        self.tstates.append(self._rt[1])
        P = np.array([self._rt[0], self.z])
        self.Pstates.append(P)

    def plot(self, ax, plot_kwargs = {}):
        Parray = np.array(self.Pstates).T
        r = Parray[0]
        z = Parray[1]

        ax.plot(z,r, color = self.color, **plot_kwargs)

    """same as ray, but it keeps a record of all changes everytime rt is changed"""

class Bundle:
    pass


class ThinLens:
    def __init__(self, focal_length, diameter = np.inf, loc = None):
        self.f = focal_length
        self.R = np.array([[1,  0],
                           [-1/self.f, 1]],
                          dtype = np.float64)
        self.d = diameter

        self.z = loc


    def __matmul__(self, ray):
        ray.rt = self.R @ ray.rt



class ThinLensMLA:
    def __init__(self, focal_length, pitch, diameter = np.inf, loc = None):
        self.f = focal_length
        self.p = pitch
        self.R = np.array([[1,  0],
                           [-1/self.f, 1]],
                          dtype = np.float64)
        self.d = diameter

        self.z = loc


    def __matmul__(self, ray):
        r, t = ray.rt

        lens_num = np.around(r/self.p)
        shift = -lens_num*self.p
        rp = r + shift

        rpt = self.R @ np.array([rp, t])

        ray.rt = np.array([r, rpt[1]])


    def refract(self, rays):
        if hasattr(rays, '__iter__'):
            for ray in rays:
                ray.rt = self.R @ ray.rt
        else:
            rays.rt = self.R @ rays.rt


class Distance:
    def __init__(self, dist):
        self.dz = dist
        self.T = np.array([[1, self.dz],
                           [0, 1      ]]
                          , dtype = np.float64)

    def __matmul__(self, ray):
        if hasattr(ray, 'z'):
            ray.z += self.dz
        ray.rt = self.T @ ray.rt


class Stop:
    def __init__(self, r_max, r_min = None, loc = None):
        self.r_max = r_max
        if r_min is None:
            self.r_min = -self.r_max
        else:
            self.r_min = r_min

        self.z = loc

    def __matmul__(self, ray):
        r = ray.rt[0]
        if r > self.r_max or r <  self.r_min:
            ray.stopped = True
        else:
            pass

class Image:
    def __init__(self, array1d = None):
        self.img = array1d

    def Make(self, rays, sampling = 2.0):
        """Creates an image using a sample of rays using their color and """

        n_rays = len(rays)
        img_size = int(n_rays / sampling)
        if img_size % 2 == 0:
            img_size += 1

        self.img = np.zeros((img_size, 3), dtype = np.float64)

        self.r_max = np.max([np.abs(ray.r) for ray in rays])

        #for better results could blur each ray using a kernel
        for ray in rays:
            pos_frac = ray.r / self.r_max

            img_index = int(.5*(1 - pos_frac)*img_size)

            self.img[img_index] += ray.get_rgb()

    def Display(self, show = False, ax = None, width = 10, title = ''):
        if ax is None:
            fig, ax = pyp.subplots()

        self.img2d = np.array(width * [self.img])
        self.img2d = np.swapaxes(self.img2d, 0, 1)

        ax.imshow(self.img2d)
        ax.set_title(title)

        if show:
            fig.show()

class CollimatedSource:
    def __init__(self, r_max, r_min = None, num = 51, zstart = -100, theta = 0, n_ior = 1,
                 cmap = 'viridis'):
        """
        :param r_max: maximum height of collimated source
        :param r_min: minimum height of collimated source
                      if not given the opposite of r_max is used
        :param num:   number of discrete paths to use
        :param zstart: axial position of source, default = -100
        :param theta:  angle in radians of the light source
        :param n_ior: starting index of refraction
        """
        self.z = zstart
        self.n_ior = n_ior
        self.num = num
        self.t = theta
        self.r_max = r_max
        if r_min is None:
            self.r_min = -r_max
        else:
            self.r_min = r_min

        self.r_array = np.linspace(self.r_min, self.r_max, self.num)
        self.bundle = []
        self.cmap = cm.get_cmap(cmap,8)
        for ii, r in enumerate(self.r_array):

            c_hex = rgb2hex(self.cmap(ii / self.num)[:-1])
            self.bundle.append(Path(self.t, r, z = self.z, n_current=self.n_ior, color= c_hex))

    def __getitem__(self, item):
        return self.bundle[item]

    def __len__(self):
        return self.num

    def plot(self, ax, kwargs):
        for ray in self.bundle:
            ray.plot(ax, kwargs)


    
class PointSource:
    def __init__(self, z, r, theta_max, theta_min = None, num = 51, n_ior = 1,
                 color = '#FF0000'):
        self.z = z
        self.r = r
        self.t_max = theta_max
        if theta_min is None:
            self.t_min = -theta_max
        else:
            self.t_min = theta_min
        self.num = num
        self.n_ior = n_ior
        self.color = color

        self.t_array = np.linspace(self.t_min, self.t_max, self.num)
        self.bundle = []
        for ii, t in enumerate(self.t_array):
            self.bundle.append(Path(t, self.r, z=self.z, n_current=self.n_ior, color=self.color))

    def __getitem__(self, item):
        return self.bundle[item]

    def __len__(self):
        return self.num

    def plot(self, ax, kwargs):
        for ray in self.bundle:
            ray.plot(ax, kwargs)


if __name__ == '__main__':

    Lens1 = ThinLens(100)
    Dist100 = Distance(100)
    Dist150 = Distance(150)
    Lens2 = ThinLens(50)
    MLA = ThinLensMLA(25,.05)

    ColLight = CollimatedSource(.5)
    PointLight = PointSource(-100, 0, .005, num = 501)

    fig,ax = pyp.subplots()

    f_obj = 100
    f_rl  = 50

    fig, ax = pyp.subplots()
    for ii in range(len(ColLight)):
        Distance(f_obj) @ ColLight[ii]
        ThinLens(f_obj) @ ColLight[ii]
        Distance(f_obj + f_rl) @ ColLight[ii]
        ThinLens(f_rl)  @ ColLight[ii]
        Distance(2 * f_rl) @ ColLight[ii]
        ThinLens(f_rl) @ ColLight[ii]
        Distance(f_rl) @ ColLight[ii]
        ThinLensMLA(25, .05) @ ColLight[ii]
        Distance(f_rl) @ ColLight[ii]

        ColLight[ii].plot(ax)
    fig.show()

    fig, ax = pyp.subplots(dpi = 200)
    for ii in range(len(PointLight)):
        Distance(f_obj) @ PointLight[ii]
        ThinLens(f_obj) @ PointLight[ii]
        Distance(f_obj) @ PointLight[ii]
        Stop(.3) @ PointLight[ii]
        Distance(f_rl) @ PointLight[ii]
        ThinLens(f_rl)  @ PointLight[ii]
        Distance(2 * f_rl) @ PointLight[ii]
        ThinLens(f_rl) @ PointLight[ii]
        Distance(f_rl) @ PointLight[ii]
        ThinLensMLA(25, .1) @ PointLight[ii]
        Distance(f_rl) @ PointLight[ii]

        PointLight[ii].plot(ax, {'alpha':.1})


    fig.show()