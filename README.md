# 3D Satellite Orbits

## This application is split into 3 parts:

#### orbit.py
reads satellite data from an online database

possible bugs:
- return type of satellite_position()

#### visualisation.py
version 1: use plotly to render Earth with an Earth texture. Orbits and satellite positions create with Scatter3d

future versions:
- add Earth texture
- make sure satellite position corresponds to earth texture
- add Earth rotation (already implemented since ECET coordinat system is used)
- add information box with satellite information (Name, etc.) - aka. legend
- add area from which satellite is visible on earth
- plot multiple satellites at once (different colors for each)
- create map for specific location with satellite transition

#### app.py
For satellite selection menu






Goal (v0): Plot a single satellite orbit around earth in 3D using python
Goal (v1): add earth surface with correct orientation and change background color
- earth rotation
- earth atmosphere?
- zoom function?
Goal (v2): turn line into dotted line and add moving satellite
Gaol (v3): 


Goal (v): add current satellite position from online database
Goal

Goal(...): Have database of satellites to choose from to plot
Goal(...): Make sure database uses up to date information found online
Goal(...): Let database update itself with new satellites/ remove old ones

