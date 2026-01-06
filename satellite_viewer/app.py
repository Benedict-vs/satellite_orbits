import streamlit as st
import numpy as np
from datetime import datetime
from zoneinfo import ZoneInfo

from skyfield.api import (
    Loader,
    wgs84,
    utc)

from skyfield.framelib import itrs

from get_orbit import (
    load_tles_from_celestrak,
    satellite_ecef_position,
    satellite_eci_position)

from visualization import (
    make_earth_surface,
    satellite_trace,
    satellite_current,
    build_figure)


load = Loader('./satellite_viewer/data')
ts = load.timescale()


@st.cache_resource
def get_satellites(group="GNSS", query="GROUP", local_only: bool = False):
    sats_list = load_tles_from_celestrak(group=group, QUERY=query, local_only=local_only)
    return {sat.name: sat for sat in sats_list}


def main():
    st.title("3D Satellite Viewer")

    local_only = st.checkbox("Dev option: local_only", value=False)

    query = st.selectbox("CelesTrak query type", ["GROUP",
                                                  "CATNR",
                                                  "INTDES",
                                                  "NAME",
                                                  "SPECIAL"
                                                  ])
    if query == "GROUP":
        group = st.selectbox("CelesTrak group/value", ["last-30-days",
                                                       "stations",
                                                       "visual",
                                                       "active",
                                                       "analyst",
                                                       "cosmos-1408-debris",
                                                       "fengyun-1c-debris",
                                                       "iridium-33-debris",
                                                       "cosmos-2251-debris",
                                                       "weather",
                                                       "noaa",
                                                       "goes",
                                                       "resource",
                                                       "sarsat",
                                                       "dmc",
                                                       "tdrss",
                                                       "argos",
                                                       "planet",
                                                       "spire",
                                                       "geo",
                                                       "gpz",
                                                       "gpz-plus",
                                                       "intelsat",
                                                       "ses",
                                                       "eutelsat",
                                                       "telesat",
                                                       "starlink",
                                                       "oneweb",
                                                       "qianfan",
                                                       "hulianwang",
                                                       "kuiper",
                                                       "iridium-NEXT",
                                                       "orbcomm",
                                                       "globalstar",
                                                       "amateur",
                                                       "satnogs",
                                                       "x-comm",
                                                       "other-comm",
                                                       "gnss",
                                                       "gps-ops",
                                                       "glo-ops",
                                                       "galileo",
                                                       "beidou",
                                                       "sbas",
                                                       "nnss",
                                                       "musson",
                                                       "science",
                                                       "geodetic",
                                                       "engineering",
                                                       "education",
                                                       "military",
                                                       "radar",
                                                       "cubesat",
                                                       "other"
                                                       ])
    elif query == "CATNR":
        group = str(st.number_input("Catalogue Number (0 to 9 digits)",
                                    0,
                                    999999999,
                                    25544
                                    )
                    )
    elif query == "INTDES":
        group = st.text_input("International Designator (yyyy-nnn)",
                              "1998-067A"
                              )
    elif query == "NAME":
        group = st.text_input("Satellite Name", "METEOSAT-10")
    elif query == "SPECIAL":
        group = st.selectbox("Special satellite groups", ["GPZ",
                                                          "GPZ-PLUS",
                                                          "DECAYING"])
    else:
        group = "temp"

    sats = get_satellites(group=group, query=query, local_only=local_only)
    sat_names = sorted(sats.keys())

    selected_name = st.selectbox("Select a satellite", sat_names)

    sat = sats[selected_name]

    # Live info box (updates every second)
    info_placeholder = st.empty()

    @st.fragment(run_every="1s")
    def live_info_box():
        # Display current local time (Europe/London)
        now_local = datetime.now(ZoneInfo("Europe/London")).strftime("%H:%M:%S")

        t0 = ts.now() if selected_time is None else selected_time

        geocentric = sat.at(t0)
        altitude_km = wgs84.height_of(geocentric).km

        # Subpoint is useful to cross-check against external trackers
        sp = wgs84.subpoint(geocentric)
        lat_deg = sp.latitude.degrees
        lon_deg = sp.longitude.degrees

        # What time is being used for the calculations?
        t0_utc_str = t0.utc_datetime().strftime("%Y-%m-%d %H:%M:%S UTC")
        time_mode_str = "Current time" if use_cur_time else "Selected time"

        # Format lat/lon as degrees with hemisphere
        lat_hem = "N" if lat_deg >= 0 else "S"
        lon_hem = "E" if lon_deg >= 0 else "W"
        lat_fmt = f"{abs(lat_deg):.4f}° {lat_hem}"
        lon_fmt = f"{abs(lon_deg):.4f}° {lon_hem}"

        info_placeholder.info(
            f"**Satellite:** {selected_name}\n\n"
            f"**Current time (Europe/London):** {now_local}\n\n"
            f"**Time used for calculations:** {time_mode_str} ({t0_utc_str})\n\n"
            f"**Subpoint (WGS84):** {lat_fmt}, {lon_fmt}\n\n"
            f"**Vertikale Distanz zur Erdoberfläche (WGS84):** {altitude_km:,.1f} km",
            icon="ℹ️",
        )

    t_orbit = st.slider(
        "Future orbit time window in minutes (max. 48 hours)",
        0,
        2*24*60) * 60  # multiply with 60 for seconds

    # generate times around t for orbit path
    orbit_seconds = (
      np.array([0.0]) if t_orbit == 0 else np.linspace(0, t_orbit, t_orbit + 1)
    )

    use_cur_time = st.checkbox("Use current time (UTC): ", value=True)

    selected_time = None
    if not use_cur_time:
        selected_datetime = st.datetime_input("Enter time (UTC)")
        if selected_datetime is not None:
            if selected_datetime.tzinfo is None:
                selected_datetime = selected_datetime.replace(tzinfo=utc)
            else:
                selected_datetime = selected_datetime.astimezone(utc)
            selected_time = ts.utc(selected_datetime)

    t0 = ts.now() if selected_time is None else selected_time
    times = t0 + orbit_seconds / (24 * 60 * 60)

    coord_system = st.selectbox("Select coordinate system",
                                ["Earth centered (ECI)",
                                 "Earth centered & fixed (ECEF)"]
                                )

    if coord_system == "Earth centered (ECI)":
        x, y, z = satellite_eci_position(sat, times)
        earth_surface = make_earth_surface(
            rotation_matrix=itrs.rotation_at(times[0]))
    else:
        x, y, z = satellite_ecef_position(sat, times)
        earth_surface = make_earth_surface()

    chart_placeholder = st.empty()

    # Get 3d Scatter plot of satellite trace
    sat_tr = satellite_trace(x, y, z, selected_name)

    @st.fragment(run_every="60s")
    def live_plot():
        t_marker = ts.now() if selected_time is None else times[0]
        if coord_system == "Earth centered (ECI)":
            x_cur, y_cur, z_cur = satellite_eci_position(sat, t_marker)
        else:
            x_cur, y_cur, z_cur = satellite_ecef_position(sat, t_marker)

        # Get 3d Scatter plot of current satellite position
        sat_cur = satellite_current(x_cur, y_cur, z_cur, selected_name)

        if use_cur_time:
            fig = build_figure(earth_surface, sat_tr, sat_cur)
        else:
            fig = build_figure(earth_surface, sat_tr)
        chart_placeholder.plotly_chart(fig, width="stretch")

    live_plot()
    live_info_box()


if __name__ == "__main__":
    main()
