import numpy as np
from dataclasses import dataclass
from functools import lru_cache

@dataclass(frozen=True)
class Ray():
    x: float
    y: float
    t: float
    p: float
    z: float

    n : float = 1.0
    color : str = '#00FF00'

    @lru_cache()
    def state(self):
        return np.array([self.x,
                         self.t,
                         self.y,
                         self.p,
                         self.z,
                         1],
                        dtype=np.float64)


class Path(np.ndarray):

    def __new__(cls, *ray_args, ray_kwargs, max_size=25):
        return super().__new__(cls, shape=(max_size), dtype=Ray)

    def __init__(self, *ray_args, ray_kwargs = {}, max_size=25):
        self.n_seg = 0 # number of straight path segments
        self.state = Ray(*ray_args, **ray_kwargs)
        self.halt = False
        self.max_size = max_size

    def __len__(self):
        return self.n_seg

    @property
    def state(self):
        return self[self.n_seg - 1].state(),

    @property
    def color(self):
        return self[self.n_seg - 1].color

    @state.setter
    def state(self, ray):
        if not self.halt:
            self[self.n_seg] = ray
            self.n_seg += 1

        if self.n_seg == self.max_size:
            self.halt = True

    def plot(self, ax3d):
        ax3d.plot(self[:,0], self[:,1], self[:,2], color = self.color)


if __name__ == '__main__':
    TR = Ray(1, .2, .05, .02, 1)
    TR2 = Ray(0, .4,.05, .01, 2)

    Path(0, 0, 0, 0, 0)

    print(TR)
