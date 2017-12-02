#!/home/ubuntu/miniconda2/bin/python

from mpl_toolkits.basemap import Basemap
from astropy.io import fits
import numpy as np
import healpy as hp
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib as mpl
import os
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection
from scipy.interpolate import griddata
import sys
import surveyview


def healpix_converter(data_filename):
    data_array = radcos_fio.data()
    # file pixels may be organized as ring or nest. Currently on nest
    ra = (np.pi * 2 / 360) * data_array[:, 0]
    dec = (np.pi * 2 / 360) * data_array[:, 1]
    flux = data_array[:, 2]
    ra[np.where(ra > np.pi)] -= 2 * np.pi
    pixel_refs = hp.pixelfunc.ang2pix(32, ra, dec, nest=False, lonlat=False)
    print pixel_refs

    return

    if nest_or_ring is 'ring':
        ra, dec = hp.pixelfunc.pix2ang(int(nside), pixelnum, nest=False, lonlat=True)
    if nest_or_ring is 'nest':
        ra, dec = hp.pixelfunc.pix2ang(int(nside), pixelnum, nest=True, lonlat=True)

    # plot of Galactic gas with coordinate projection
    min_ra = np.min(ra)
    print min_ra
    max_ra = np.max(ra)
    print max_ra
    mean_ra = np.mean(ra)
    min_dec = np.min(dec)
    print min_dec
    max_dec = np.max(dec)
    print max_dec
    mean_dec = np.mean(dec)

    fig = plt.figure()
    ax = fig.add_axes([0.1, 0.1, 0.8, 0.8])
    # llc and urc are x & y ranges, and are specific to a location.
    # The latitude and longitude settings are part of basemap.
    m = Basemap(projection='hammer', llcrnrlon=-11, llcrnrlat=-15, urcrnrlon=13.5, urcrnrlat=-37, resolution='h', epsg=5520)
    # m = Basemap(projection='hammer', lon_0=mean_ra, lat_0=mean_dec, llcrnrlon=min_ra, llcrnrlat=min_dec, urcrnrlon=max_ra, urcrnry=max_dec, resolution='h', epsg=5520)
    x, y = m(ra, dec)
    # draw parallels and meridians. Labels are 1/0 as [Top,bottom,right,left]
    m.drawparallels(np.arange(-90., 120., 10.), labels=[1, 0, 0, 0])
    m.drawmeridians(np.arange(0., 420., 10.), labels=[0, 0, 0, 1])
    # creates a scatter plot of the selected data on a globe.
    m.scatter(x, y, 3, marker='o', linewidths=.1, c=data, cmap=plt.cm.coolwarm)
    m.colorbar()
    plt.show()


def plot_healpix_file(data_filename, save_filename):

    data, nside, nest = load_map(data_filename)
    plot_filled_pixels(data, nside, nest, save_filename)


def plot_healpix_tiling():

    data_type = 'Residual_I'
    normalization = 'uniform'
    data_dir = '/Healpix_fits'

    tile_center_ras = [100, 100, 100, 100, 100,
                       90, 90, 90, 90, 90,
                       80, 80, 80, 80, 80,
                       70, 70, 70, 70, 70,
                       60, 60, 60, 60, 60,
                       50, 50, 50, 50, 50,
                       40, 40, 40, 40, 40,
                       30, 30, 30, 30, 30,
                       20, 20, 20, 20, 20,
                       10, 10, 10, 10, 10,
                       0, 0, 0, 0, 0,
                       -10, -10, -10, -10, -10,
                       -20, -20, -20, -20, -20]

    tile_center_decs = [-5, -15, -25, -35, -45,
                        -5, -15, -25, -35, -45,
                        -5, -15, -25, -35, -45,
                        -5, -15, -25, -35, -45,
                        -5, -15, -25, -35, -45,
                        -5, -15, -25, -35, -45,
                        -5, -15, -25, -35, -45,
                        -5, -15, -25, -35, -45,
                        -5, -15, -25, -35, -45,
                        -5, -15, -25, -35, -45,
                        -5, -15, -25, -35, -45,
                        -5, -15, -25, -35, -45,
                        -5, -15, -25, -35, -45]

    #obsids = [1131478056, 1131472536, 1131468936, 1131463536, 1131717352,
    #          1131711952, 1131535544,
    #          1131477936, 1131472416, 1131468816, 1131463416, 1131457896,
    #          1131454296, 1131710032,
    #          1131477816, 1131731632, 1130778424, 1131463296, 1131459576,
    #          1131713512, 1131709912]

    obsids = [1131478056, 1131564464, 1131477936, 1130787784, 1131477816,
              1131733672, 1131562544, 1131733552, 1130785864, 1131475896,
              1131559064, 1131558944, 1131731752, 1130782264, 1130783824,
              1131470736, 1131557144, 1131470616, 1130780464, 1131470496,
              1131468936, 1131553544, 1131726352, 1130778664, 1131468696,
              1131724672, 1131551744, 1131465216, 1130776864, 1130776624,
              1131463536, 1131549944, 1131463416, 1130773264, 1131463296,
              1131461616, 1131548024, 1131461496, 1130773144, 1131461376,
              1131717352, 1131544424, 1131717232, 1131459696, 1131459576,
              1131456216, 1131542624, 1131456096, 1131715432, 1131715312,
              1131711952, 1131540824, 1131454296, 1131713632, 1131454176,
              1131710152, 1131537224, 1131710032, 1131710032, 1131709912,
              1131535544, 1131535424, 1131535304, 1131710032, 1131709912]
    obsids = list(set(obsids))  # remove duplicates

    data = []
    for i, obs in enumerate(obsids):
        print 'Gathering pixels from obsid {} of {}.'.format(i, len(obsids))
        obs_data, nside, nest = load_map('{}/{}_{}_{}_HEALPix.fits'.format(data_dir, obs, normalization, data_type))
        tile_bounds_radec = [[tile_center_ras[i]-5, tile_center_decs[i]-5],
                             [tile_center_ras[i]-5, tile_center_decs[i]+5],
                             [tile_center_ras[i]+5, tile_center_decs[i]+5],
                             [tile_center_ras[i]+5, tile_center_decs[i]-5]]
        tile_bounds_vec = np.array([hp.pixelfunc.ang2vec(corner[0], corner[1], lonlat=True) for corner in tile_bounds_radec])
        use_pixels = hp.query_polygon(nside, tile_bounds_vec, nest=nest)
        data.extend([data_point for data_point in obs_data if data_point.pixelnum in use_pixels])

    # Collect Healpix pixels to plot
    patches = []
    colors = []
    for point in data:
        point.get_pixel_corners(nside, nest)
        polygon = Polygon(zip(point.pix_corner_ras, point.pix_corner_decs))
        patches.append(polygon)
        colors.append(point.signal)

    collection = PatchCollection(patches, cmap='Greys_r', lw=0.04)
    collection.set_array(np.array(colors))  # set the data colors
    collection.set_edgecolor('face')  # make the face and edge colors match

    fig, ax = plt.subplots(figsize=(48, 16), dpi=500)
    ax.add_collection(collection)  # plot data

    # plot lines between tiles
    line_width = 2.0
    color = 'gray'
    order = 8
    plt.plot([130, -45], [-10, -10], lw=line_width, c=color, zorder=order)
    plt.plot([130, -45], [-20, -20], lw=line_width, c=color, zorder=order)
    plt.plot([130, -45], [-30, -30], lw=line_width, c=color, zorder=order)
    plt.plot([130, -45], [-40, -40], lw=line_width, c=color, zorder=order)
    plt.plot([130, -45], [-50, -50], lw=line_width, c=color, zorder=order)
    plt.plot([95, 95], [-75, -20], lw=line_width, c=color, zorder=order)
    plt.plot([85, 85], [-75, -20], lw=line_width, c=color, zorder=order)
    plt.plot([75, 75], [-75, -20], lw=line_width, c=color, zorder=order)
    plt.plot([65, 65], [-75, -20], lw=line_width, c=color, zorder=order)
    plt.plot([55, 55], [-75, -20], lw=line_width, c=color, zorder=order)
    plt.plot([45, 45], [-75, -20], lw=line_width, c=color, zorder=order)
    plt.plot([35, 35], [-75, -20], lw=line_width, c=color, zorder=order)
    plt.plot([25, 25], [-75, -20], lw=line_width, c=color, zorder=order)
    plt.plot([15, 15], [-75, -20], lw=line_width, c=color, zorder=order)
    plt.plot([5, 5], [-75, -20], lw=line_width, c=color, zorder=order)
    plt.plot([-5, -5], [-75, -20], lw=line_width, c=color, zorder=order)
    plt.plot([-15, -15], [-75, -20], lw=line_width, c=color, zorder=order)

    plt.xlabel('RA (deg)')
    plt.ylabel('Dec (deg)')
    plt.axis('equal')
    ax.set_facecolor('black')  # make plot background black
    plt.axis([130, -45, -75, 20])
    plt.grid(which='both', lw=1.0, zorder=10)
    cbar = fig.colorbar(collection, ax=ax)  # add colorbar
    cbar.ax.set_ylabel('Flux Density (Jy/sr)', rotation=270)  # label colorbar

    plt.savefig('/home/ubuntu/MWA/mosaicplot.png', format='png', dpi=500)


def plot_healpix_mosaic(data_dir, obs_array, save_filename):

    data_type = 'Residual_I'
    normalization = 'uniform'
    obs_info_file = '/Users/ruby/EoR/sidelobe_survey_obsinfo.txt'
    boundary_width = 0.1

    if data_dir.endswith('/'):
        data_dir = data_dir[:-1]

    observations = surveyview.load_survey(obs_info_file)
    observations = [obs for obs in observations if obs.obsid in obs_array]

    data_files = os.listdir(data_dir)
    for i, use_obsid in enumerate(obs_array):
        obsid_list = [obs.obsid for obs in observations]
        heal_file = '{}_{}_{}_HEALPix.fits'.format(use_obsid, normalization,
                                                   data_type)
        if heal_file in data_files:
            observations[obsid_list.index(use_obsid)].heal_data, \
                nside_new, nest_new \
                = load_map('{}/{}'.format(data_dir, heal_file))
            if i != 0:
                if nside_new != nside:
                    print 'ERROR: HEALPix nsides do not match. Exiting.'
                    sys.exit(1)
                if nest_new != nest:
                    print 'ERROR: HEALPix ordering conventions do not match. Exiting.'
                    sys.exit(1)
            nside = nside_new
            nest = nest_new
        else:
            print 'WARNING: Data file {} not found.'.format(heal_file)
            del observations[obsid_list.index(use_obsid)]

    pixel_vals = []
    for obs in observations:
        pixel_vals.extend(
            [data_point.pixelnum for data_point in obs.heal_data]
            )
    pixel_vals = list(set(pixel_vals))

    use_data = [0]*len(pixel_vals)
    for i, pixel in enumerate(pixel_vals):
        if i % 100 == 0:
            print i
        pixel_dist = [float('inf')]*len(observations)
        pixel_ra, pixel_dec = hp.pixelfunc.pix2ang(nside, pixel, nest=nest,
                                                   lonlat=True)
        for j, obs in enumerate(observations):
            if pixel in [data_point.pixelnum for data_point in obs.heal_data]:
                ra_dist = min([abs(obs.ra - pixel_ra + delta) for delta in
                              [-360., 0, 360]])
                pixel_dist[j] = (ra_dist)**2 + (obs.dec-pixel_dec)**2

        pixel_dist_sorted = sorted(pixel_dist)
        obs_use_data = observations[pixel_dist.index(pixel_dist_sorted[0])].heal_data
        use_data[i] = obs_use_data[([data_point.pixelnum for data_point in obs_use_data]).index(pixel)]
        if pixel_dist_sorted[1]-pixel_dist_sorted[0] < boundary_width**2:
            use_data[i].signal = 0

    print nside
    plot_filled_pixels(use_data, nside, nest, save_filename)


def plot_filled_pixels(data, nside, nest, save_filename):

    fig, ax = plt.subplots()

    # Collect Healpix pixels to plot
    patches = []
    colors = []
    for point in data:
        point.get_pixel_corners(nside, nest)
        polygon = Polygon(zip(point.pix_corner_ras, point.pix_corner_decs))
        patches.append(polygon)
        if point.signal < 0.04:
            colors.append(point.signal)
        else:
            colors.append(0.04)

    collection = PatchCollection(patches, cmap='Greys_r', lw=0.04)
    collection.set_array(np.array(colors))  # set the data colors
    collection.set_edgecolor('face')  # make the face and edge colors match
    ax.add_collection(collection)  # plot data
    plt.xlabel('RA (deg)')
    plt.ylabel('Dec (deg)')
    plt.axis('equal')
    ax.set_facecolor('black')  # make plot background black
    plt.axis([14, -11, -37, -16])
    plt.grid(which='both', zorder=10)
    cbar = fig.colorbar(collection, ax=ax, extend='max')  # add colorbar
    cbar.ax.set_ylabel('Flux Density (Jy/sr)', rotation=270)  # label colorbar

    plt.savefig(save_filename, format='png', dpi=2000)


def load_map(data_filename):

    contents = fits.open(data_filename)
    nside = int(contents[1].header['nside'])
    ordering = contents[1].header['ordering']
    data = contents[1].data
    contents.close()

    pixel_vals = data.field('PIXEL')
    signal_vals = data.field('SIGNAL')

    if ordering.lower() == 'ring':
        nest = False
    elif ordering.lower() == 'nested':
        nest = True
    else:
        print 'ERROR: Invalid ordering parameter.'
        print 'Ordering must be "ring" or "nested". Exiting.'
        sys.exit(1)


    if len(pixel_vals) != len(signal_vals):
        print 'ERROR: Pixel index and data lengths do not match. Exiting.'
        sys.exit(1)

    pixel_data = []
    for i in range(len(pixel_vals)):
        data_point = HealpixPixel(pixel_vals[i], signal_vals[i])
        pixel_data.append(data_point)

    return pixel_data, nside, nest


class HealpixPixel:

    def __init__(self, pixelnum, signal):
        self.pixelnum = int(pixelnum)
        self.signal = float(signal)

    def get_ra_dec(self, nside, nest):
        ra, dec = hp.pixelfunc.pix2ang(nside, self.pixelnum,
                                       nest=nest, lonlat=True)
        if ra > 270:
            self.ra = ra
        else:
            self.ra = ra - 360.
        self.dec = dec

    def get_pixel_corners(self, nside, nest):
        coords = hp.boundaries(nside, self.pixelnum, step=1,
                               nest=nest)
        ras, decs = hp.pixelfunc.vec2ang(np.transpose(coords), lonlat=True)
        for i, ra in enumerate(ras):
            if ra > 270:
                ras[i] -= 360.
        self.pix_corner_ras = ras
        self.pix_corner_decs = decs


if __name__ == '__main__':
    plot_healpix_tiling()
