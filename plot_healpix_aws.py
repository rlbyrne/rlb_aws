#!/home/ubuntu/miniconda2/bin/python

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
import sys
import surveyview


obsids = [1131478056, 1131564464, 1131477936, 1130787784, 1131477816,
          1131733672, 1131562544, 1131733552, 1130785864, 1131475896,
          1131559064, 1131558944, 1131731752, 1130782264, 1130783824,
          1131470736, 1131557144, 1131470616, 1130780464, 1131470496,
          1131468936, 1131553544, 1131726352, 1130778664, 1131468696,
          1131724672, 1131551744, 1131465216, 1130776864, 1130776624,
          1131463536, 1131549944, 1131463416, 1130773264, 1131463296,
          1131461616, 1131548024, 1131461496, 1130773264, 1131461376,
          1131717352, 1131544424, 1131717232, 1131717232, 1131459576,
          1131456216, 1131542624, 1131456096, 1131456096, 1131715312,
          1131711952, 1131540824, 1131454296, 1131454296, 1131454176,
          1131710152, 1131537224, 1131710032, 1131710032, 1131709912,
          1131535544, 1131535424, 1131535304, 1131710032, 1131709912]


def download_data():

    obs_to_download = list(set(obsids))
    for obs in obs_to_download:
        os.system('aws s3 cp s3://mwatest/diffuse_survey/fhd_rlb_GLEAM+Fornax_cal_decon_Nov2016/output_data/{}_uniform_Residual_I_HEALPix.fits /Healpix_fits/{}_uniform_Residual_I_HEALPix.fits'.format(obs, obs))


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

    data = []
    for i, obs in enumerate(obsids):
        print 'Gathering pixels from obsid {} of {}.'.format(i+1, len(obsids))
        obs_data, nside, nest = load_map('{}/{}_{}_{}_HEALPix.fits'.format(data_dir, obs, normalization, data_type))
        tile_bounds_radec = [[tile_center_ras[i]-5, tile_center_decs[i]-5],
                             [tile_center_ras[i]-5, tile_center_decs[i]+5],
                             [tile_center_ras[i]+5, tile_center_decs[i]+5],
                             [tile_center_ras[i]+5, tile_center_decs[i]-5]]
        tile_bounds_vec = np.array([hp.pixelfunc.ang2vec(corner[0], corner[1], lonlat=True) for corner in tile_bounds_radec])
        use_pixels = hp.query_polygon(nside, tile_bounds_vec, nest=nest)
        data.extend([data_point for data_point in obs_data if data_point.pixelnum in use_pixels])

    # Collect Healpix pixels to plot
    print 'Gathering pixel corners.'
    patches = []
    colors = []
    for point in data:
        point.get_pixel_corners(nside, nest)
        polygon = Polygon(zip(point.pix_corner_ras, point.pix_corner_decs))
        patches.append(polygon)
        colors.append(point.signal)

    print 'Plotting.'
    collection = PatchCollection(patches, cmap='Greys_r', lw=0.04)
    collection.set_array(np.array(colors))  # set the data colors
    collection.set_clim(vmin=-.035, vmax=.035)  # set the colorbar min and max
    collection.set_edgecolor('face')  # make the face and edge colors match

    fig, ax = plt.subplots(figsize=(24, 8), dpi=1000)
    ax.add_collection(collection)  # plot data

    # plot lines between tiles
    line_width = 2
    color = 'gray'
    order = 8
    plt.plot([130, -45], [-10, -10], lw=line_width, c=color, zorder=order)
    plt.plot([130, -45], [-20, -20], lw=line_width, c=color, zorder=order)
    plt.plot([130, -45], [-30, -30], lw=line_width, c=color, zorder=order)
    plt.plot([130, -45], [-40, -40], lw=line_width, c=color, zorder=order)
    plt.plot([130, -45], [-50, -50], lw=line_width, c=color, zorder=order)
    plt.plot([95, 95], [-75, 20], lw=line_width, c=color, zorder=order)
    plt.plot([85, 85], [-75, 20], lw=line_width, c=color, zorder=order)
    plt.plot([75, 75], [-75, 20], lw=line_width, c=color, zorder=order)
    plt.plot([65, 65], [-75, 20], lw=line_width, c=color, zorder=order)
    plt.plot([55, 55], [-75, 20], lw=line_width, c=color, zorder=order)
    plt.plot([45, 45], [-75, 20], lw=line_width, c=color, zorder=order)
    plt.plot([35, 35], [-75, 20], lw=line_width, c=color, zorder=order)
    plt.plot([25, 25], [-75, 20], lw=line_width, c=color, zorder=order)
    plt.plot([15, 15], [-75, 20], lw=line_width, c=color, zorder=order)
    plt.plot([5, 5], [-75, 20], lw=line_width, c=color, zorder=order)
    plt.plot([-5, -5], [-75, 20], lw=line_width, c=color, zorder=order)
    plt.plot([-15, -15], [-75, 20], lw=line_width, c=color, zorder=order)

    plt.xlabel('RA (deg)')
    plt.ylabel('Dec (deg)')
    plt.axis('equal')
    ax.set_facecolor('gray')  # make plot background gray
    plt.axis([110, -30, -50, 0])
    cbar = fig.colorbar(collection, ax=ax, extend='both')  # add colorbar
    cbar.ax.set_ylabel('Flux Density (Jy/sr)', rotation=270)  # label colorbar

    plt.savefig('/home/ubuntu/MWA/mosaicplot.png', format='png', dpi=1000)


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
