import numpy as np
from skyfield.api import Loader, EarthSatellite, wgs84
from astropy import constants as const
import csv

from typing import Any

load = Loader('satellite_viewer/data')


def load_tles_from_file(path) -> dict[Any, Any]:
    lines = open(path, 'r').read().strip().splitlines()
    sats = {}
    for i in range(0, len(lines), 3):
        name = lines[i].strip()
        l1 = lines[i + 1].strip()
        l2 = lines[i + 2].strip()
        sats[name] = EarthSatellite(l1, l2, name, load.timescale())
    return sats


def download_tles_from_celestrak(VALUE: str,
                                 QUERY: str = "GROUP",
                                 FORMAT_VALUE: str = "CSV",
                                 ) -> str:
    """
    Downloads TLE data from CelesTrak based on query parameters if not already present or older than max_days.

    For exact usage, see https://www.celestrak.org/NORAD/documentation/gp-data-formats.php

    Format: https://celestrak.org/NORAD/elements/gp.php?{QUERY}=VALUE[&FORMAT=VALUE]

    :param VALUE: For QUERY "GROUP": GP Data set, such as "stations" for Space Stations, "weather" for weather satellites, "GNSS" for Global Navigation Satellite Systems, etc.
    :type VALUE: str
    :param FORMAT: Desired format, one of "TLE", "CSV", "JSON", "XML", etc.
    :type FORMAT: str
    :param QUERY: Catalog Number (1 to 9 digits) "CATNR", International Designator (yyyy-nnn) "INTDES", "GROUP", Satellite Name "NAME", "SPECIAL"
    :type QUERY: str
    :return: Filename where data is stored
    :rtype: str
    """

    max_days = 7.0         # download again once 7 days old
    name = f'{VALUE}.{FORMAT_VALUE}'  # custom filename, not 'gp.php'

    base = 'https://celestrak.org/NORAD/elements/gp.php'

    url = base + f'?{QUERY}={VALUE}&FORMAT={FORMAT_VALUE}'

    if not load.exists(name) or load.days_old(name) >= max_days:
        load.download(url, filename=name)

    return name


def load_tles_from_celestrak(group: str = "GNSS",
                             QUERY: str = "GROUP"
                             ) -> list[Any]:
    """
    Loads TLE data from CelesTrak based on group and query parameters.

    :param group: if QUERY = GROUP then GP Data set, such as "stations" for Space Stations, "weather" for weather satellites, "GNSS" for Global Navigation Satellite Systems, etc.
    :type group: str
    :param QUERY: defautl = "GROUP". Other options: Catalog Number (1 to 9 digits) "CATNR", International Designator (yyyy-nnn) "INTDES", "GROUP", Satellite Name "NAME", "SPECIAL"
    :type QUERY: str
    :return: satellites
    :rtype: list[Any]
    """
    path = download_tles_from_celestrak(group, QUERY, "CSV")

    with load.open(path, mode='r') as f:
        data = list(csv.DictReader(f))

    ts = load.timescale()

    sats = [EarthSatellite.from_omm(ts, fields) for fields in data]
    print('Loaded', len(sats), 'satellites')

    return sats


def satellite_ecet_position(sat: EarthSatellite, time) -> tuple[Any, Any, Any]:
    """
    Returns the satellite position in an Earth fixed frame (WGS84),
    as (x,y,z) in km where Earth is centered at (0,0,0) and non-rotating in
    that frame.

    :param sat: EarthSatellite object
    :type sat: EarthSatellite
    :param time: time object from skyfield
    :type time: skyfield.timelib.Time
    :return: position (x,y,z) in km
    :rtype: np.ndarray
    """

    geocentric = sat.at(time)

    # For each time get subpoint (lat, lon, elevation) on Earth

    la, lo = wgs84.latlon_of(geocentric)
    lat = la.radians
    lon = lo.radians
    alt_km = wgs84.height_of(geocentric).km

    EARTH_RADIUS_KM = const.R_earth.to('km').value
    r_orbit = EARTH_RADIUS_KM + alt_km

    x = r_orbit * np.cos(lat) * np.cos(lon)
    y = r_orbit * np.cos(lat) * np.sin(lon)
    z = r_orbit * np.sin(lat)

    return x, y, z


# tests
# sats = load_tles_from_celestrak(group="weather")
# print(satellite_position(sats[0], load.timescale().now()))
