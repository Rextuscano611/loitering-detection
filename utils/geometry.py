import numpy as np


def point_in_polygon(point, polygon):
    """
    Check if a point (x, y) is inside a polygon.
    polygon: list of (x, y) tuples
    Uses ray casting algorithm.
    """
    x, y = point
    n = len(polygon)
    inside = False

    px, py = polygon[0]
    for i in range(1, n + 1):
        qx, qy = polygon[i % n]
        if ((py > y) != (qy > y)) and (x < (qx - px) * (y - py) / (qy - py) + px):
            inside = not inside
        px, py = qx, qy

    return inside


def get_feet_point(x1, y1, x2, y2):
    """
    Returns the bottom-center point of a bounding box.
    This is the ground contact point — more accurate than centroid for zone checks.
    """
    fx = int((x1 + x2) / 2)
    fy = int(y2 - (y2 - y1) * 0.05)   # 5% inset from bottom edge
    return (fx, fy)


def get_three_feet_points(x1, y1, x2, y2):
    """
    Returns 3 ground-level points for robust zone entry check.
    center-bottom, left-bottom, right-bottom
    """
    inset_y = int(y2 - (y2 - y1) * 0.05)
    return [
        (int((x1 + x2) / 2), inset_y),   # center
        (int(x1 + (x2 - x1) * 0.2), inset_y),   # left foot
        (int(x1 + (x2 - x1) * 0.8), inset_y),   # right foot
    ]


def iou(boxA, boxB):
    """
    Intersection over Union of two bounding boxes.
    boxes format: (x1, y1, x2, y2)
    Used for ID inheritance when track ID switches.
    """
    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[2], boxB[2])
    yB = min(boxA[3], boxB[3])

    interW = max(0, xB - xA)
    interH = max(0, yB - yA)
    interArea = interW * interH

    if interArea == 0:
        return 0.0

    areaA = (boxA[2] - boxA[0]) * (boxA[3] - boxA[1])
    areaB = (boxB[2] - boxB[0]) * (boxB[3] - boxB[1])

    return interArea / float(areaA + areaB - interArea)