import numpy as np
import matplotlib.pyplot as pyp
from matplotlib import cm
from functools import lru_cache


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
    """
    Converts a hex number string representing color into rgb values
    :param hex_str: 7 character string with the first character being ignored
    :return: unsigned 8 bit integer array of red green and blue values
    """
    if len(hex_str) != 7:
        raise ValueError("Hex String must be 7 characters")

    r, g, b = '0x' + hex_str[1:3], '0x' + hex_str[3:5], '0x' + hex_str[5:]
    r, g, b = int(r, 0), int(g, 0), int(b, 0)

    return np.array([r, g, b], dtype = np.uint8)


class Ray:
    def __init__(self, theta, r, n_current = 1, color = '#FFFFFF'):
        # self.t = theta
        # self.r = r
        self.n = n_current
        self.stopped = False  # has to be done before self.rt

        self.rt = np.array([r, theta])
        # self.dx, self.dy = np.cos(theta), np.sin(theta)
        # self.slope = np.array([self.dx, self.dy])

        self.color = color

    def get_rgb(self):
        return hex2rgb(self.color)


class Path(Ray):
    """keeps a record of past states everytime rt is changed"""
    def __init__(self, theta, r, z = -np.inf, n_current = 1, color = '#000000'):
        # These lists must be created before the other init since it sets rt and set rt has calls to these
        self.Pstates = []
        self.tstates = []
        self.z = z
        super().__init__(theta, r, n_current=n_current, color=color)

    def __repr__(self):
        return f"Path - Current state: r = {self.rt[0]:.3f}, theta =  {self.rt[1]:.3f}, z = {self.z:.3f}"

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

    def plot(self, ax, kwargs = {}):
        Parray = np.array(self.Pstates).T
        r = Parray[0]
        z = Parray[1]

        ax.plot(z, r, color = self.color, **kwargs)


class ABCD:
    def __init__(self, A=1, B=0, C=0, D=1, loc=0.0):
        self.A, self.B = A, B
        self.C, self.D = C, D

        self.z = loc

        self.SYS = np.array([[A, B],
                             [C, D]],
                            dtype = np.float64)

    def __matmul__(self, ray):
        if hasattr(ray, 'z'):
            ray.z += self.B
        ray.rt = self.SYS @ ray.rt

    def __repr__(self):
        return f"ABCD Optical Element: [{self.A}, {self.B}];[{self.C}, {self.D}]"

    @lru_cache
    def Reverse(self):
        MatInv = np.linalg.inv(self.SYS)
        Ainv, Binv, Cinv, Dinv = MatInv.ravel()
        RevSys = ABCD(Ainv,Binv,Cinv,Dinv,loc=self.z+self.B)
        return RevSys

    def plot(self, ax, ylims):

        if self.B == 0:
            ax.vlines(self.z, ylims[0], ylims[1], color = 'k')


class Distance(ABCD):
    def __init__(self, dist, start=0):
        self.dz = dist

        super().__init__(B = self.dz, loc=start)


class Interface(ABCD):
    def __init__(self, n2, n1 = 1, loc = 0.0):
        self.n1 = n1
        self.n2 = n2
        self.z = loc
        super().__init__(D = n1/n2,loc = loc)


class ThinLens(ABCD):
    def __init__(self, focal_length, diameter = np.inf, loc = None):
        self.f = focal_length
        super().__init__(C = -1/self.f)
        self.d = diameter
        self.z = loc


class Slab:
    def __init__(self, n, thickness, diameter = np.inf, loc = None):
        self.n = n
        self.t = thickness
        self.R = np.array([[1, self.t / n],
                           [0, 1]],
                          dtype = np.float64)
        self.d = diameter
        self.z = loc


class ThinLensMLA(ThinLens):
    def __init__(self, focal_length, pitch, diameter = np.inf, loc = None):
        super().__init__(focal_length, diameter = diameter, loc = loc)
        # self.f = focal_length
        self.p = pitch
        # self.R = np.array([[1,  0],
        #                    [-1/self.f, 1]],
        #                   dtype = np.float64)
        # self.d = diameter
        # self.z = loc

    def __matmul__(self, ray):
        r, t = ray.rt

        lens_num = np.around(r/self.p)
        shift = -lens_num*self.p
        rp = r + shift

        rpt = self.SYS @ np.array([rp, t])

        ray.rt = np.array([r, rpt[1]])


class Stop(ABCD):
    def __init__(self, r_max, r_min=None, loc=None):
        super().__init__(loc=loc)

        self.r_max = r_max
        if r_min is None:
            self.r_min = -self.r_max
        else:
            self.r_min = r_min

    def __matmul__(self, ray):
        r = ray.rt[0]
        if r > self.r_max or r < self.r_min:
            ray.stopped = True
        else:
            pass


class ThickLens:
    def __init__(self, WD, f, thickness, loc = 0, diameter = np.inf):
        self.z  = loc
        self.t = thickness

        B = thickness
        C = -1 / np.sqrt(f * WD)

        A = -f * C
        D = -WD * C

        self.R = np.array([[A, B],
                           [C, D]])

    def __matmul__(self, ray):
        if hasattr(ray, 'z'):
            ray.z += self.t
        ray.rt = self.R @ ray.rt


class OpticsSystem(list):
    """
    Define an optical system using a list of elements
    Distances between elements are found, and distance elements don't need to be added
    """
    def __init__(self, element_list, propagate = 0):
        super().__init__(element_list)

        # Add a distance element to the system between defined elements using the difference in z positions
        for i, (prev_element, next_element) in enumerate(zip(self[:-1],self[1:])):
            dz = next_element.z - prev_element.z
            dist = Distance(dz)

            self.insert(1 + 2*i, dist) # Inserts distances between elements
        self.append(Distance(propagate))

        self.SYS = self[0].SYS
        for element in self[1:]:
            self.SYS = self.SYS @ element.SYS

    def __repr__(self):
        rep = ''
        for element in self:
            rep += f" -> {type(element).__name__}"

        return rep

    def calcPath(self, ray, first_element = 0):
        dobj = Distance(self[0].z - ray.z)
        dobj @ ray

        for element in self:
            element @ ray

    def __matmul__(self, rays):
        if hasattr(rays, '__iter__'):
            for ray in rays:
                self.calcPath(ray)
        else: self.calcPath(rays)

    def Reverse(self, propagate = None):
        if propagate is None: propagate = -self[-1].dz

        reversed_order = self[-2::-2] # reverse the list and drop the distance matrices
        reverse = [element.Reverse() for element in reversed_order]

        optics_system_rev = OpticsSystem(reverse, propagate=propagate) #create a new optics system using the original element list reversed

        return optics_system_rev # return the reversed system

    def plot(self, ax):
        ylims = ax.get_ylim()
        for elem in self:
            elem.plot(ax, ylims)


class Bundle:

    @staticmethod
    def getCmap(color, MPL_grades=11):
        if callable(color):
            cmap = color  # if a function is passed assume it's already a colormap that returns a hex string
        elif color[0] == '#':
            def cmap(_):
                return color                      # make a function that takes an argument but always returns the color
        else:
            mpl_cmap = cm.get_cmap(color, MPL_grades)

            def cmap(x):                          # grab the callable matplotlib colormap
                return rgb2hex(mpl_cmap(x)[:-1])  # make the colormap drop the alpha component

        return cmap

    def __init__(self, num, color):
        self.bundle = []
        self.num = num
        self.cmap = self.getCmap(color)

    def __len__(self):
        return self.num

    def __getitem__(self, item):
        return self.bundle[item]

    def __iter__(self):
        self.ii = 0
        return self

    def __next__(self):
        if self.ii < self.num:
            ray = self[self.ii]
            self.ii += 1
            return ray
        else:
            raise StopIteration

    def __repr__(self):
        return type(self).__name__

    def plot(self, ax, kwargs = {}):
        for ray in self.bundle:
            ray.plot(ax, kwargs)


class CollimatedSource(Bundle):
    def __init__(self, r_max, r_min = None, num = 51, zstart = -100, theta = 0, n_ior = 1,
                 color = 'viridis'):
        """
        :param r_max: maximum height of collimated source
        :param r_min: minimum height of collimated source
                      if not given the opposite of r_max is used
        :param num:   number of discrete paths to use
        :param zstart: axial position of source, default = -100
        :param theta:  angle in radians of the light source
        :param n_ior: starting index of refraction
        """
        super().__init__(num, color)

        self.z = zstart
        self.n_ior = n_ior
        self.t = theta
        self.r_max = r_max
        if r_min is None:
            self.r_min = -r_max
        else:
            self.r_min = r_min

        self.r_array = np.linspace(self.r_min, self.r_max, self.num)

        for ii, r in enumerate(self.r_array):

            c_hex = self.cmap(ii / self.num)
            self.bundle.append(Path(self.t, r, z = self.z, n_current=self.n_ior, color= c_hex))


class PointSource(Bundle):
    def __init__(self, z, r, theta_max, theta_min = None, num = 51, n_ior = 1,
                 color = '#FF0000'):
        super().__init__(num, color)

        self.z = z
        self.r = r
        self.t_max = theta_max
        if theta_min is None:
            self.t_min = -theta_max
        else:
            self.t_min = theta_min
        self.n_ior = n_ior
        self.color = color

        self.t_array = np.linspace(self.t_min, self.t_max, self.num)
        for ii, t in enumerate(self.t_array):
            c_hex = self.cmap(ii / self.num)
            self.bundle.append(Path(t, self.r, z=self.z, n_current=self.n_ior, color=c_hex))

    def __getitem__(self, item):
        return self.bundle[item]

    def __len__(self):
        return self.num


class Image:
    def __init__(self, extent, sens_size, intensity = .1):
        self.r_max = extent
        self.n_px = int(1 + 2 * ((self.r_max // sens_size)+1))
        self.img = np.zeros((self.n_px, 3), dtype = np.float64)
        self.intensity = intensity

    def Add(self, ray):
        """Creates an image using a sample of rays using their color and """
        if ray.stopped:
            return
        # for better results could blur each ray using a kernel
        r = ray.rt[0]
        pos_frac = r / self.r_max

        if pos_frac > 1 or pos_frac < -1:
            return

        img_idx = .5*(1 - pos_frac)*(self.n_px-1)

        img_idx_l = int(np.floor(img_idx))
        img_idx_u = int(np.ceil(img_idx))

        idx_frac = img_idx - img_idx_l

        self.img[img_idx_u] += ray.get_rgb() * idx_frac * self.intensity
        self.img[img_idx_l] += ray.get_rgb() * (1 - idx_frac) * self.intensity

    def __add__(self, ray):
        if hasattr(ray, '__getitem__'):
            for ii in range(len(ray)):
                self.Add(ray[ii])
        else: self.Add(ray)

    def cap(self, max = 255):
        over = self.img > max
        self.img[over] = 255

    def Display(self, show = True, ax = None, width = 10, title = ''):
        if ax is None:
            fig, ax = pyp.subplots(dpi = 200, figsize = (.015 * width, .015 * self.n_px))

        self.img2d = np.array(width * [self.img], dtype = np.float64)
        self.img2d = np.swapaxes(self.img2d, 0, 1)
        self.img2d /= np.max(self.img2d)

        ax.imshow(self.img2d)
        ax.set_title(title)

        if show:
            fig.show()


if __name__ == '__main__':

    Obj = ThinLens(100, loc = 0)
    Lens1 = ThinLens(50, loc = 150)
    Lens2 = ThinLens(50, loc = 250)
    MLA = ThinLensMLA(25, .05, loc = 300)

    ColLight = CollimatedSource(.5)
    PointLight = PointSource(-100, 0, .005, num = 501, color = 'autumn')

    FLFM = OpticsSystem([Obj, Lens1, Lens2, MLA], propagate = 50)

    fig, ax = pyp.subplots()
    FLFM @ ColLight
    ColLight.plot(ax)
    fig.show()

    fig, ax = pyp.subplots()
    FLFM @ PointLight
    PointLight.plot(ax, {'alpha': .1})
    fig.show()