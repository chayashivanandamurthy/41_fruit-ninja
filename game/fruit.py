import math

class Fruit:
    def __init__(self, x, y, vx, vy, gravity, radius=28, kind="fruit"):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.gravity = gravity
        self.radius = radius
        self.kind = kind  # "fruit" or "bomb"
        self.sliced = False

    def update(self):
        self.vy += self.gravity
        self.x += self.vx
        self.y += self.vy

    def contains_point(self, x, y):
        # Checks whether a single point is inside the fruit.
        return math.hypot(self.x - x, self.y - y) <= self.radius

    def intersects_segment(self, start, end):
        """Return True if the line segment passes through the fruit."""
        x1, y1 = start
        x2, y2 = end

        dx = x2 - x1
        dy = y2 - y1

        # If both mouse positions are the same, fall back to point check.
        if dx == 0 and dy == 0:
            return self.contains_point(x1, y1)

        # Project the fruit centre onto the mouse movement segment.
        t = ((self.x - x1) * dx + (self.y - y1) * dy) / (dx * dx + dy * dy)

        # Keep the closest point on the segment, not the infinite line.
        t = max(0, min(1, t))

        closest_x = x1 + t * dx
        closest_y = y1 + t * dy

        # Check whether that closest point is inside the fruit.
        return math.hypot(self.x - closest_x, self.y - closest_y) <= self.radius

    def off_screen(self, height):
        return self.y - self.radius > height
