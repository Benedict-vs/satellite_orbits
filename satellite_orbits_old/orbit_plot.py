import numpy as np
import pyvista as pv
from astropy import constants as const
from astropy import units as u

# Earth data
earth = pv.examples.planets.load_earth(radius=6378.1)
earth_texture = pv.examples.load_globe_texture()

# Background data
cubemap = pv.examples.download_cubemap_space_4k()

# Light (sun)
light = pv.Light()
light.set_direction_angle(30, 160)

# Orbit data
r_earth = const.R_earth.to(u.km).value   # Earth's radius in meters
altitude_satellite = 500  # km
r_orbit = r_earth + altitude_satellite
theta = np.linspace(0, 2*np.pi, 360)
points = np.column_stack((r_orbit * np.cos(theta),
                          r_orbit * np.sin(theta),
                          np.zeros_like(theta)))
orbit_line = pv.Spline(points, 360)


# --- Prepare plotter ---
plotter = pv.Plotter()
plotter = pv.Plotter(lighting='none')
_ = plotter.add_actor(cubemap.to_skybox())
plotter.set_environment_texture(cubemap, is_srgb=True)
plotter.add_light(light)
earth_actor = plotter.add_mesh(earth, texture=earth_texture, smooth_shading=True)
earth_actor.rotate_x(23.5)
plotter.add_mesh(orbit_line, line_width=4)


plotter.show()
