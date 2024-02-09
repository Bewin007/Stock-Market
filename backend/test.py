import math

def is_point_in_fence(lat, long):
    fence_points = [(10.933942, 76.737375), (10.943666, 76.737467), (10.944398, 76.748322), (10.932758, 76.747158)]

    if not isinstance(lat, (float, int)):
        raise ValueError("Latitude must be a number.")
    if not isinstance(long, (float, int)):
        raise ValueError("Longitude must be a number.")
    if not isinstance(fence_points, list) or not all(isinstance(point, tuple) for point in fence_points):
        raise ValueError("Fence points must be a list of tuples.")

    lat_rad = lat * math.pi / 180
    long_rad = long * math.pi / 180

    num_intersections = 0
    for i in range(len(fence_points)):
        start_point = fence_points[i]
        start_lat_rad = start_point[0] * math.pi / 180
        start_long_rad = start_point[1] * math.pi / 180

        next_point = fence_points[(i + 1) % len(fence_points)]
        next_lat_rad = next_point[0] * math.pi / 180
        next_long_rad = next_point[1] * math.pi / 180

        dx = next_long_rad - start_long_rad
        dy = next_lat_rad - start_lat_rad

        if (dy > 0) != (dy * (long_rad - start_long_rad) - dx * (lat_rad - start_lat_rad) > 0):
            if start_lat_rad <= lat_rad <= next_lat_rad or next_lat_rad <= lat_rad <= start_lat_rad:
                num_intersections += 1
    return num_intersections % 2 == 1

point_to_check = (10.941, 76.744) 
in_fence = is_point_in_fence(point_to_check[0], point_to_check[1])
print(in_fence)  
