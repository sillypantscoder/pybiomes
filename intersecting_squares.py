import math

def get_intersecting_unit_squares(circle_x: float, circle_y: float, circle_radius: float) -> list[tuple[int, int]]:
    intersecting_squares: list[tuple[int, int]] = []

    # Calculate the bounding box of the circle
    min_x = math.floor(circle_x - circle_radius)
    max_x = math.ceil(circle_x + circle_radius) + 1
    min_y = math.floor(circle_y - circle_radius)
    max_y = math.ceil(circle_y + circle_radius) + 1

    # Iterate over all unit squares within the bounding box
    for x in range(min_x, max_x):
        for y in range(min_y, max_y):
            # Check if the square intersects the circle
            if math.dist((x, y), (circle_x, circle_y)) <= 1.5 + circle_radius:
                intersecting_squares.append((x, y))

    return intersecting_squares
