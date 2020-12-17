from queue import PriorityQueue
import math
import numpy as np
import random
from PIL import Image
from PIL import ImageStat
from PIL import ImageDraw
import itertools


def sampling(original, xSz, ySz, bxSz):
    sites = []
    colors = []
    pix_color = original.load()
    for x in itertools.product(range(0, xSz - int(bxSz / 2), bxSz), range(0, ySz - int(bxSz / 2), bxSz)):
        box = (x[0], x[1], x[0] + 1, x[1] + 1)
        region = original.crop(box)
        if (ImageStat.Stat(region).mean[0] / 255 < random.random()):
            sites.append((x[0] + int(bxSz / 2), x[1] + int(bxSz / 2)))
            colors.append(pix_color[x[0] + int(bxSz / 2), x[1] + int(bxSz / 2)])
    return sites, colors


def create(sites, size):
    pixel_assign = np.array([[-1 for x in range(size[1])] for y in range(size[0])])
    queue = PriorityQueue()
    for i in range(len(sites)):
        if check(sites[i], size):
            queue.put((0, sites[i], i))
    while not queue.empty():
        item = queue.get()
        site = item[1]
        assign = item[2]
        if pixel_assign[site[0]][site[1]] == -1:
            pixel_assign[site[0]][site[1]] = assign
            for neighbor in find_neighbors(site):
                if check(neighbor, size) and pixel_assign[neighbor[0]][neighbor[1]] == -1:
                    distance = distance_calculation(sites[assign], neighbor)
                    queue.put((distance, neighbor, assign))
    return pixel_assign


def distance_calculation(site1, site2):
    return math.sqrt((site1[0] - site2[0]) ** 2 + (site1[1] - site2[1]) ** 2)


def find_neighbors(site):
    neighbors = []
    neighbors.append((site[0] + 0, site[1] + 1))
    neighbors.append((site[0] + 1, site[1] + 0))
    neighbors.append((site[0] + 0, site[1] - 1))
    neighbors.append((site[0] - 1, site[1] + 0))
    return neighbors


def check(site, size):
    return (site[0] >= 0) and (site[0] < size[0]) and (site[1] >= 0) and (site[1] < size[1])


def show_Sampling_pic(original, sites):
    Sampling_pic = ImageDraw.Draw(original)
    for site in sites:
        Sampling_pic.ellipse([(site[0] - 0.5, site[1] - 0.5), (site[0] + 0.5, site[1] + 0.5)])
    original.show()


def load_pic(filename):
    original = Image.open(filename)
    size = original.size
    return original, size


# showSampling=True: Pop out the sample points. Set false to block.
# dense: Larger than 1. The smaller the value, the denser the Voronoi diagram.
# withBoundary=True: Black boundary between each cell. Set false to remove the boundary.
# colorful = True: Assign site pixel color to cell color. Set false to view black and white Voronoi diagram.
def draw_voronoi(filename, showSampling, dense=6, withBoundary=True, colorful=True):
    # Load pic
    original, size = load_pic(filename)
    # Sample pic
    sites, colors = sampling(original, size[0], size[1], dense)
    # Generate pixel matrix
    pixel_assign = create(sites, size)
    if colorful:
        # Show sampling
        if showSampling:
            show_Sampling_pic(original, sites)
        # Draw voronoi art
        voronoi_art = Image.new('RGB', (size[0], size[1]), (255, 255, 255))
        voronoi_draw = ImageDraw.Draw(voronoi_art)
        for pixel in itertools.product(range(size[0]), range(size[1])):
            x = pixel[0]
            y = pixel[1]
            if withBoundary:
                try:
                    if (pixel_assign[x][y] != pixel_assign[x][y + 1]) or (
                            pixel_assign[x + 1][y] != pixel_assign[x][y]):
                        voronoi_draw.rectangle([pixel, pixel], (0, 0, 0), (0, 0, 0))
                    else:
                        voronoi_draw.rectangle([pixel, pixel], colors[pixel_assign[x][y]], (0, 0, 0))
                except IndexError:
                    voronoi_draw.rectangle([pixel, pixel], colors[pixel_assign[x][y]], (0, 0, 0))
            else:
                voronoi_draw.rectangle([pixel, pixel], colors[pixel_assign[x][y]], (0, 0, 0))
        voronoi_art.show()
    else:
        pixel_matrix = np.array([[0 for i in range(size[1])] for j in range(size[0])])
        for i in range(size[0]):
            for j in range(size[1]):
                try:
                    if (pixel_assign[i][j] != pixel_assign[i][j + 1]) or (pixel_assign[i + 1][j] != pixel_assign[i][j]):
                        pixel_matrix[i][j] = 1
                except IndexError:
                    pixel_matrix[i][j] = 1
        pixel_matrix = pixel_matrix.T
        img = Image.fromarray((1 - pixel_matrix) * 255)
        img.show()


draw_voronoi("flower.png", showSampling=True, dense=6, withBoundary=True, colorful=True)
draw_voronoi("flower.png", showSampling=False, dense=6, withBoundary=False, colorful=True)
draw_voronoi("flower.png", showSampling=False, dense=6, withBoundary=True, colorful=False)
