import numpy as np
import pyvista as pv
from astropy import constants as const
from astropy import units as u

r_earth = const.R_earth.to(u.km).value   # Earth's radius in meters
altitude_satellite = 500  # km
r_orbit = r_earth + altitude_satellite


# Earth data
earth_sphere = pv.Sphere(radius=r_earth, theta_resolution=100, phi_resolution=100)

# Orbit data
theta = np.linspace(0, 2*np.pi, 360)
points = np.column_stack((r_orbit * np.cos(theta),
                          r_orbit * np.sin(theta),
                          np.zeros_like(theta)))
orbit_line = pv.Spline(points, 360)

plotter = pv.Plotter()
plotter.add_mesh(earth_sphere, smooth_shading=True)
plotter.add_mesh(orbit_line, line_width=4)
plotter.show()