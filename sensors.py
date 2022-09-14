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