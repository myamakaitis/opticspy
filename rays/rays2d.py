import numpy as np
from ..colors import rgb2hex, hex2rgb

class Ray:

    def __init__(self, theta, r, n_current = 1, color = '#FFFFFF'):
        # self.t = theta
        # self.r = r
        self.n = n_current
        self.halt = False  # has to be done before self.rt

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
        if self.halt:
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