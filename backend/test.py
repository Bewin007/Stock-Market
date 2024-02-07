from shapely.geometry import Point, Polygon

def is_inside_geo_fence(latitude, longitude, fence_coordinates):
    """
    Check if a point is inside a geo-fencing area.

    Args:
    latitude (float): Latitude of the point.
    longitude (float): Longitude of the point.
    fence_coordinates (list of tuples): List of (latitude, longitude) tuples representing the vertices of the geo-fencing area.

    Returns:
    bool: True if the point is inside the geo-fencing area, False otherwise.
    """
    # Create a shapely Point object representing the given coordinates
    point = Point(longitude, latitude)

    # Create a shapely Polygon object from the fence coordinates
    polygon = Polygon(fence_coordinates)

    # Check if the point is inside the polygon
    return polygon.contains(point)

# Example usage
fence_coordinates = [(42.0, -71.0), (42.5, -71.5), (42.5, -70.5), (42.0, -70.0)]  # Example fence coordinates

latitude = 42.3  # Example latitude of the point
longitude = -71.2  # Example longitude of the point

inside_fence = is_inside_geo_fence(latitude, longitude, fence_coordinates)
print("Is the point inside the geo-fencing area?", inside_fence)
