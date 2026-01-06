# 3D Satellite Orbits

*Simple setup:*
All comands to be run from root folder 

pip install -r requirements.txt
streamlit run satellite_viewer/app.py

## Python files + explanation

### get_orbit.py
reads satellite data from an online database

*possible bugs:*
- return type of satellite_position()

### visualisation.py
Uses plotly to render Earth, orbits and satellite positions.

future versions:
- (implemented) add Earth texture 
- (implemented) hightlight current position
- (implemented) make sure satellite position corresponds to earth texture
- (implemented) add Earth rotation (updated every 60s)
- add information box with satellite information (Name, etc.) - aka. legend
- add area from which satellite is visible on earth
- plot multiple satellites at once (different colors for each)
- create map for specific location with satellite transition

### app.py
runs web gui (using streamlit) with various plot related options

