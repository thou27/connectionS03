import folium
from branca.element import Figure

def create_route_map(start_coords, end_coords):
    """Create a Folium map with route visualization."""
    if not all([start_coords, end_coords]):
        return None
    
    # Calculate center point for map
    center_lat = (start_coords[0] + end_coords[0]) / 2
    center_lon = (start_coords[1] + end_coords[1]) / 2
    
    # Create map
    fig = Figure(width=800, height=400)
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=4,
        tiles='CartoDB positron'
    )
    
    # Add markers
    folium.Marker(
        start_coords,
        popup='Start',
        icon=folium.Icon(color='green', icon='info-sign')
    ).add_to(m)
    
    folium.Marker(
        end_coords,
        popup='End',
        icon=folium.Icon(color='red', icon='info-sign')
    ).add_to(m)
    
    # Draw line between points
    folium.PolyLine(
        locations=[start_coords, end_coords],
        weight=2,
        color='blue',
        opacity=0.8
    ).add_to(m)
    
    return m

