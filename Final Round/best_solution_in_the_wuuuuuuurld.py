from IO import *
import numpy as np
from collections import deque
from skimage.morphology import skeletonize, medial_axis
import matplotlib.pyplot as plt
from random import shuffle


# http://stackoverflow.com/a/39082209
def unit_circle_vectorized(r):
    mask = np.arange(-r, r + 1) ** 2
    dists = np.sqrt(mask[:, None] + mask)
    diff = (dists - r)
    ret = (diff < 0.5)
    return ret.astype(int)


def wireless_access(a, b, d):
    g = d["graph"]
    r = d["radius"]
    circle = unit_circle_vectorized(r)
    mask = circle
    for w_off in range(-r, r):
        for h_off in range(-r, r):
            # if in range of the router
            if not circle[h_off + r][w_off + r]:
                continue
            # skip router cell
            if h_off == 0 and w_off == 0:
                continue
            # transform coordinates
            x = a + h_off
            y = b + w_off
            # checking bounds
            if x not in range(0, d["height"]):
                continue
            if y not in range(0, d["width"]):
                continue
            # if this is a wireless cell
            ftype = g[x][y]
            if not ftype == Cell.Wireless:
                # set others fields to zero
                mask[h_off + r][w_off + r] = 0
                continue
            # construct smallest enclosing rectangle
            rows = range(np.min([a, x]), np.max([a, x]) + 1)
            cols = range(np.min([b, y]), np.max([b, y]) + 1)
            # loop over rectangle and check condition
            # TODO if there is at least one wall cell in closing rectangle condition is true?
            for w in rows:
                for v in cols:
                    ftype = g[w][v]
                    # if this is a wall cell
                    if not ftype == Cell.Wall:
                        continue
                    # check if wall is in 'sight'
                    if np.min([a, x]) <= w <= np.max([a, x]) and np.min([b, y]) <= v <= np.max([b, y]):
                        # ALARM!
                        mask[h_off + r][w_off + r] = 0
                        # TODO some early stopping?
    return mask


def bfs(d, start):
    dx = [-1, 0, 1]
    dy = [-1, 0, 1]

    visited = [[False] * d['width']] * d['height']
    parent = [[-1] * d['width']] * d['height']

    queue = deque()

    queue.append(start)
    visited[start[0]][start[1]] = True

    while len(queue) > 0:
        cur = queue.popleft()

        if cur != start:
            # check if we already found a connection
            if d['graph'][cur] in [2, 3]:
                # generate path from parent array
                path = []
                a = cur
                while a != start:
                    path.append(a)
                    a = parent[a[0]][a[1]]
                path.append(a)
                return path

        # check neighbors
        for ddx in dx:
            for ddy in dy:
                if ddx == 0 and ddy == 0:
                    continue

                child_x, child_y = cur[0] + ddx, cur[1] + ddy
                # only if still in the grid
                if 0 <= child_x and child_x < d['height'] and 0 <= child_y and child_y < d['width']:
                    child = (child_x, child_y)
                    # only "walkable" cells
                    if d['graph'][child] in [1, 2, 3]:
                        if not visited[child[0]][child[1]]:
                            queue.append(child)
                            visited[child[0]][child[1]] = True
                            parent[child[0]][child[1]] = cur

    return None


def place_cables(d):
    return d


def place_routers(d):
    wireless = np.where(d["graph"] == Cell.Wireless, 1, 0)
    # perform skeletonization
    skeleton = skeletonize(wireless)
    med_axis = medial_axis(wireless)

    skel = skeleton
    # get all skeleton positions
    pos = []
    for i in range(skel.shape[0]):
        for j in range(skel.shape[1]):
            if skel[i][j]:
                pos.append((i, j))

    shuffle(pos)
    a, b = pos[0]
    mask = wireless_access(a, b, d)
    router_score = np.sum(mask)

    # choose this router placement
    d["graph"][a][b] = Cell.Router

    return d


if __name__ == '__main__':
    import sys

    # fpath = sys.argv[1]
    D = read_dataset('input/example.in')
    bb = D['backbone']
    D['graph'][bb] = 2

    # set routers
    D['graph'][3, 6] = 3
    D['graph'][3, 9] = 3

    print(bfs(D, (3, 9)))

    # write_solution(sys.argv[2], D)
