import numpy as np
import matplotlib.pyplot as pyp


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

    return f"#{int(rgb[0]):02x}{int(rgb[1]):02x}{int(rgb[2]):02x}"


def hex2rgb(hex_str):
    if len(hex_str) != 7:
        raise ValueError("Hex String must be 7 characters")

    r, g, b = '0x' + hex_str[1:3], '0x' + hex_str[3:5], '0x' + hex_str[5:]
    r, g, b = int(r,0), int(g,0), int(b,0)

    return r,g,b



class Ray:
    def __init__(self, theta, r, n_current = 1, color = '#FFFFFF'):
        self.t = theta
        self.r = r
        self.n = n_current

        self.rt = np.array([self.r, self.t])
        
        self.dx, self.dy = np.cos(theta), np.sin(theta)
        self.slope = np.array([self.dx, self.dy])

        self.color = color

    def get_rgb(self):
        return hex2rgb(self.color)


class Path(Ray):
    def __init__(self, theta, r, z = -np.inf, n_current = 1, color = '#FFFFFF'):
        super().__init__(theta, r, n_current = n_current, color = color)

        self.z = z
        self.Pstates = []
        self.tstates = []

    @property
    def rt(self):
        return self._rt

    @rt.setter
    def rt(self, value):
        self.rt = value
        self.tstates.append(self.rt[1])
        P = np.array(self.r, self.z)
        self.Pstates.append(P)

    """same as ray, but it keeps a record of all changes everytime rt is changed"""

class Bundle:
    pass


class ThinLens:
    def __init__(self, focal_length, diameter = np.inf, loc = None):
        self.f = focal_length
        self.R = np.array([[1,  0],
                           [1, -1/self.f]],
                          dtype = np.float64)
        self.d = diameter

        self.z = None


    def __matmul__(self, ray):
        ray.rt = self.R @ ray.rt


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
        ray.rt = self.T @ ray.rt


class Stop:
    def __init__(self, diameter):
        self.d = diameter
        self.r = diameter / 2




class Image:
    def __init__(self, array1d = None):
        self.img = array1d


    def Make(self, rays, sampling = 2.0):

        n_rays = len(rays)
        img_size = int(n_rays / sampling)
        if img_size % 2 == 0:
            img_size += 1

        self.img = np.zeros((img_size, 3), dtype = np.float64)

        r_max = np.max([np.abs(ray.r) for ray in rays])

        #for better results could blur each ray using a kernel
        for ray in rays:
            pos_frac = ray.r / r_max

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

    #class CollimatedSource:
    
#class PointSource:


