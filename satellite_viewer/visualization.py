import numpy as np
import plotly.graph_objects as go
from PIL import Image


EARTH_RADIUS_KM = 6371.0


def make_earth_surface(
        texture_path: str = "satellite_viewer/bluemarble-2048.png"
        ) -> go.Mesh3d:

    # Parameterize the sphere
    n_lat = 360
    n_lon = 720
    lat = np.linspace(-np.pi / 2, np.pi / 2, n_lat)     # phi
    lon = np.linspace(-np.pi, np.pi, n_lon, endpoint=False)     # theta
    lat_grid, lon_grid = np.meshgrid(lat, lon, indexing="ij")

    x = EARTH_RADIUS_KM * np.cos(lat_grid) * np.cos(lon_grid)
    y = EARTH_RADIUS_KM * np.cos(lat_grid) * np.sin(lon_grid)
    z = EARTH_RADIUS_KM * np.sin(lat_grid)

    img = Image.open(texture_path).convert("RGB")
    img = img.resize((n_lon, n_lat), resample=Image.Resampling.LANCZOS)
    tex = np.asarray(img)  # shape (H, W, 3)

    # Image origin is at top (north) but our lat grid runs
    # from -90 to 90, so flip vertically
    rgb = np.flipud(tex)

    # Flatten vertices
    xv = x.reshape(-1)
    yv = y.reshape(-1)
    zv = z.reshape(-1)
    rgbv = rgb.reshape(-1, 3)
    vertex_colors = [f"rgb({r},{g},{b})" for r, g, b in rgbv]

    # --- Triangulate the lat/lon grid (wrap in longitude) ---
    def vid(i_lat, i_lon):
        return i_lat * n_lon + i_lon

    I, J, K = [], [], []
    for i_lat in range(n_lat - 1):
        for i_lon in range(n_lon):
            j_lon = (i_lon + 1) % n_lon
            a = vid(i_lat, i_lon)
            b = vid(i_lat + 1, i_lon)
            c = vid(i_lat + 1, j_lon)
            d = vid(i_lat, j_lon)
            I += [a, a]
            J += [b, c]
            K += [c, d]

    earth = go.Mesh3d(
        x=xv, y=yv, z=zv,
        i=I, j=J, k=K,
        vertexcolor=vertex_colors,
        flatshading=False,
        lighting=dict(ambient=0.9, diffuse=0.9, specular=0.05, roughness=0.6),
        name="Earth"
    )
    return earth


def satellite_trace(x, y, z, name, show_path=True) -> go.Scatter3d:
    return go.Scatter3d(
        x=x, y=y, z=z,
        mode='lines+markers' if show_path else 'markers',
        marker=dict(size=3),
        name=name
    )


def build_figure(earth_surface, sat_traces) -> go.Figure:
    fig = go.Figure(data=[earth_surface] + sat_traces)
    fig.update_layout(
        scene=dict(
            aspectmode="data",
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            zaxis=dict(visible=False),
        ),
        margin=dict(l=0, r=0, t=0, b=0)
    )
    return fig
