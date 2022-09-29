x, y, t, p, z = 0, 0, 0, 0, 0
test_path = Path(x, y, t, p, z)

dz = 1
D = Distance(dz)

D.Tform(test_path)

import matplotlib.pyplot as pyp

fig = pyp.figure()
ax = fig.add_subplot(111, projection='3d')

test_path.plot(ax)