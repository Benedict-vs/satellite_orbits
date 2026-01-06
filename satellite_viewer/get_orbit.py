from skyfield.api import Loader, EarthSatellite
from skyfield.framelib import itrs
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
                                 local_only: bool = False,
                                 ) -> str:
    """
    Downloads TLE data from CelesTrak based on query parameters
    if not already present or older than max_days.

    For exact usage, see
        https://www.celestrak.org/NORAD/documentation/gp-data-formats.php

    Format:
        https://celestrak.org/NORAD/elements/gp.php?{QUERY}=VALUE[&FORMAT=VALUE]

    :param VALUE: For QUERY "GROUP": GP Data set, such as "stations" for
        Space Stations, "weather" for weather satellites,
        "GNSS" for Global Navigation Satellite Systems, etc.
    :type VALUE: str
    :param FORMAT: Desired format, one of "TLE", "CSV", "JSON", "XML", etc.
    :type FORMAT: str
    :param QUERY: Catalog Number (1 to 9 digits) "CATNR", International
        Designator (yyyy-nnn) "INTDES", "GROUP", Satellite Name "NAME",
        "SPECIAL"
    :type QUERY: str
    :return: Filename where data is stored
    :rtype: str
    """

    max_days = 7.0         # download again once 7 days old
    name = f'{VALUE}.{FORMAT_VALUE}'  # custom filename

    base = 'https://celestrak.org/NORAD/elements/gp.php'

    url = base + f'?{QUERY}={VALUE}&FORMAT={FORMAT_VALUE}'

    if local_only:
        return name

    if not load.exists(name) or load.days_old(name) >= max_days:
        load.download(url, filename=name)

    return name


def load_tles_from_celestrak(group: str = "GNSS",
                             QUERY: str = "GROUP",
                             local_only: bool = False,
                             ) -> list[Any]:
    """
    Loads TLE data from CelesTrak based on group and query parameters.

    :param QUERY: default = "GROUP". Other options: Catalog Number (1 to 9
        digits) "CATNR", International Designator (yyyy-nnn) "INTDES", "GROUP",
        Satellite Name "NAME", "SPECIAL"
    :type QUERY: str
    :param group: if QUERY = GROUP then GP Data set, such as "stations" for
        Space Stations, "weather" for weather satellites, "GNSS" for Global
        Navigation Satellite Systems, etc.
    :type group: str
    :return: satellites
    :rtype: list[Any]
    """
    path = download_tles_from_celestrak(group, QUERY, "CSV", local_only)

    with load.open(path, mode='r') as f:
        data = list(csv.DictReader(f))

    ts = load.timescale()

    sats = [EarthSatellite.from_omm(ts, fields) for fields in data]
    print('Loaded', len(sats), 'satellites')

    return sats


def satellite_ecef_position(sat: EarthSatellite, time) -> tuple[Any, Any, Any]:
    """Return satellite position in an Earth-centered Earth-fixed frame (ECEF/ITRS).

    Skyfield's `sat.at(time)` returns a geocentric position in the GCRS (ECI) frame.
    Calling `.frame_xyz(itrs)` rotates that position into the ITRS frame, which is
    Earth-fixed (it rotates with the Earth and is anchored to the Earth's crust).

    Parameters
    ----------
    sat : EarthSatellite
        Satellite whose position is requested.
    time : skyfield.timelib.Time
        Skyfield time at which to evaluate the satellite position.

    Returns
    -------
    (x, y, z) : tuple[float, float, float]
        ECEF/ITRS Cartesian coordinates in kilometers.

    Notes
    -----
    This result *does* depend on the provided `time`: both because the satellite
    moves along its orbit and because the GCRS→ITRS transformation includes the
    Earth's rotation (and optionally polar motion if available in the Timescale).
    """

    geocentric = sat.at(time)
    x, y, z = geocentric.frame_xyz(itrs).km
    return x, y, z


def satellite_eci_position(sat: EarthSatellite, time) -> tuple[Any, Any, Any]:
    """Return satellite position in the Geocentric Celestial Reference System (GCRS).

    This is an Earth-centered inertial (ECI-like) frame that does not rotate with
    the Earth. For Skyfield Earth satellites, `sat.at(time)` produces a geocentric
    GCRS position, and `.xyz.km` returns its Cartesian coordinates.

    Parameters
    ----------
    sat : EarthSatellite
        Satellite whose position is requested.
    time : skyfield.timelib.Time
        Skyfield time at which to evaluate the satellite position.

    Returns
    -------
    (x, y, z) : tuple[float, float, float]
        GCRS Cartesian coordinates in kilometers.

    Notes
    -----
    This result depends on the provided `time` because the satellite state is
    propagated from its TLE to that epoch.
    """

    geocentric = sat.at(time)
    x, y, z = geocentric.xyz.km
    return x, y, z


# tests
# sats = load_tles_from_celestrak(group="weather")
# print(satellite_position(sats[0], load.timescale().now()))
