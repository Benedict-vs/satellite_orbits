import streamlit as st
import numpy as np
from skyfield.api import Loader, EarthSatellite
from orbit import load_tles_from_celestrak, satellite_ecet_position
from visualization import make_earth_surface, satellite_trace, build_figure

load = Loader('satellite_viewer/data')
ts = load.timescale()


@st.cache_resource
def get_satellites(group="GNSS", query="GROUP") -> dict[str, EarthSatellite]:
    sats_list = load_tles_from_celestrak(group, query)
    return {sat.name: sat for sat in sats_list}


def main():
    st.title("3D Satellite Viewer")

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
        group = st.select_slider("Catalogue Number",
                                 options=["1", "2", "3",
                                          "4", "5", "6",
                                          "7", "8", "9"],
                                 )
    elif query == "INTDES":
        group = st.text_input("International Designator (yyyy-nnn)")
    elif query == "NAME":
        group = st.text_input("Satellite Name", "METEOSAT-10")
    elif query == "SPECIAL":
        group = st.selectbox("Special satellite groups", ["GPZ",
                                                          "GPZ-PLUS",
                                                          "DECAYING"])
    else:
        group = "temp"

    sats = get_satellites(group=group, query=query)
    sat_names = sorted(sats.keys())

    selected_name = st.selectbox("Select a satellite", sat_names)

    # Time control
    realtime = st.checkbox("Use real time", value=True)
    if realtime:
        t0 = ts.now()
    else:
        minutes = st.slider("Minutes from now", -60, 60, 0)
        t0 = ts.now() + minutes / (24 * 60)

    sat = sats[selected_name]

    t_half = int(st.slider("orbit time window in hours (max. 7 days)", 0, 7*24)/2)*60

    # generate times around t for orbit path
    orbit_minutes = np.linspace(-t_half, t_half, t_half*2+1)
    times = t0 + orbit_minutes / (24 * 60)

    x, y, z = satellite_ecet_position(sat, times)

    earth_surface = make_earth_surface()
    sat_tr = satellite_trace(x, y, z, selected_name)

    fig = build_figure(earth_surface, [sat_tr])
    st.plotly_chart(fig, use_container_width=True)


if __name__ == "__main__":
    main()
