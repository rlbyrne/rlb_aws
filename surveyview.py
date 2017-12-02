#!/home/ubuntu/miniconda2/bin/python

# Tools for characterizing a survey


class Observation:

    def __init__(self, info):
        self.obsid = info[0]
        self.lst = float(info[1])
        self.ra = float(info[2])
        self.dec = float(info[3])
        self.az = float(info[4])
        self.el = float(info[5])


class KnownSource:

    def __init__(self, name, ra, dec):
        self.name = name
        self.ra = float(ra)
        self.dec = float(dec)


def load_survey(obs_info_file):

    obsfile = open(obs_info_file, "r")
    obsinfo = [line.split("\n") for line in obsfile.readlines()]
    obsfile.close()
    obsinfo = [obs[0] for obs in obsinfo]
    obsinfo = obsinfo[1:]  # remove header
    obsinfo = list(set(obsinfo))
    obsinfo.sort()

    observations = []
    for info in obsinfo:
        info = info.split(", ")
        observations.append(Observation(info))

    return observations


def get_pointings(observations):

    # Note that this code likely doesn't work for surveys other than the
    # diffuse survey.

    # Round the declinations to the nearest 6th to clump them in bands
    decs_round = [int(obs.dec/6.)*6 for obs in observations]
    decs_set = list(set(decs_round))
    decs_set.sort()

    Azimuths = [round(obs.az) for obs in observations]
    Elevations = [round(obs.el) for obs in observations]

    dec_pointings_options = [3, 2, 1, 0, -1, -2, -3]
    azimuth_pointings_options = [2, 1, 0, -1, -2]
    for band_index, dec_band in enumerate(decs_set):
        Azimuths_band = []
        Elevations_band = []
        for obs_index in range(len(observations)):
            if decs_round[obs_index] == dec_band:
                Azimuths_band.append(Azimuths[obs_index])
                Elevations_band.append(Elevations[obs_index])
        AzEls_band = zip(Azimuths_band, Elevations_band)
        AzEls_band_set = list(set(AzEls_band))
        Azimuth_band_set = [value[0] for value in AzEls_band_set]
        Elevations_band_set = [value[1] for value in AzEls_band_set]
        Az_zero = Azimuth_band_set[
            Elevations_band_set.index(max(Elevations_band_set))]
        Azimuth_band_set_sort = list(sorted(Azimuth_band_set))
        Az_wrap = 0
        for Az in Azimuth_band_set_sort:
            if Az > Az_zero + 180:
                Az_wrap += 1
        if Az_wrap > 0:
            Azimuth_band_set_sort = (Azimuth_band_set_sort[
                len(Azimuth_band_set_sort)-Az_wrap:]
                + Azimuth_band_set_sort[:len(Azimuth_band_set_sort)-Az_wrap])

        for obs_index in range(len(observations)):
            if decs_round[obs_index] == dec_band:
                observations[obs_index].pointing = '({}, {})'.format(
                    azimuth_pointings_options[
                        Azimuth_band_set_sort.index(Azimuths[obs_index])],
                    dec_pointings_options[band_index]
                    )

    return observations


def get_a_team_sources():

    a_team_ras = [
        83.6331, 79.9572, 139.524, 201.365,
        252.784, 187.706, 299.868, 350.858,
        50.6738, 128.836, 83.8221
        ]
    a_team_decs = [
        22.0145, -45.7788, -12.0956, -43.0192,
        4.9925, 12.3911, 40.7339, 58.8,
        -37.2083, -45.1764, -5.3911
        ]
    a_team_names = [
        'Crab', 'Pic A', 'Hydra A', 'Cen A',
        'Her A', 'Vir A', 'Cygnus A', 'Cas A',
        'Fornax A', 'Vela', 'Orion'
        ]

    a_teams = []
    for i in range(len(a_team_names)):
        a_teams.append(KnownSource(a_team_names[i], a_team_ras[i],
                                   a_team_decs[i]))

    return a_teams
