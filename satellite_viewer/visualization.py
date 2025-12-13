import numpy as np
import plotly.graph_objects as go

EARTH_RADIUS_KM = 6371.0


def make_earth_surface():
    # Parameterize the sphere
    lat = np.linspace(-np.pi / 2, np.pi / 2, 181)   # phi
    lon = np.linspace(-np.pi, np.pi, 361)           # theta
    lon_grid, lat_grid = np.meshgrid(lon, lat)

    x = EARTH_RADIUS_KM * np.cos(lat_grid) * np.cos(lon_grid)
    y = EARTH_RADIUS_KM * np.cos(lat_grid) * np.sin(lon_grid)
    z = EARTH_RADIUS_KM * np.sin(lat_grid)

    earth = go.Surface(
        x=x, y=y, z=z,
        surfacecolor=np.clip(lat_grid, -np.pi/2, np.pi/2),
        colorscale="Viridis",
        showscale=False,
        opacity=0.9,
    )
    return earth


def satellite_trace(x, y, z, name, show_path=True):
    return go.Scatter3d(
        x=x, y=y, z=z,
        mode='lines+markers' if show_path else 'markers',
        marker=dict(size=3),
        name=name
    )


def build_figure(earth_surface, sat_traces):
    fig = go.Figure(data=[earth_surface] + sat_traces)
    fig.update_layout(
        scene=dict(
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            zaxis=dict(visible=False),
            aspectmode='data',
        ),
        margin=dict(l=0, r=0, t=0, b=0)
    )
    return fig
