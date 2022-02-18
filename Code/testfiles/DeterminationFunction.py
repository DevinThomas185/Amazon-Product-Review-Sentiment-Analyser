import random
from math import sqrt
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon

# Multiply the transformation matrix to form 2D plot
def matrixMultiplication(pos, neu, neg):
    x = (-sqrt(2) / 2) * pos + (sqrt(2) / 2) * neu
    y = (sqrt(6) / 2) * neg
    return round(x, 3), round(y, 3)


def checkRegion(pos, neu, neg):
    # Convert 3D Coordinates to 2D Shapely coordinate
    coords = Point(matrixMultiplication(pos, neu, neg))

    # Define the important points
    centre = (-0.44, 0.45)
    bottomwall = (-0.3, -0.01)
    leftwall = (-0.45, 0.45)
    rightwall = (0.65, 0.11)

    # Constant points
    leftcorner = (-0.72, -0.01)
    rightcorner = (0.72, -0.01)
    topcorner = (0, 1.23)

    # Defining regions/polygons
    buy = Polygon([centre, bottomwall, leftcorner, leftwall])
    neutral = Polygon([centre, bottomwall, rightcorner, rightwall])
    nobuy = Polygon([centre, rightwall, topcorner, leftwall])

    # Determine which region the point lies in and return outcome
    if buy.contains(coords):
        return "buy"
    elif neutral.contains(coords):
        return "neutral"
    elif nobuy.contains(coords):
        return "nobuy"
    else:
        return "error"


for i in range(100):
    pos = float(random.randint(0, 100))
    neg = float(random.randint(0, 100 - pos))
    neu = 100 - pos - neg
    pos = pos / 100
    neg = neg / 100
    neu = neu / 100
    print(i+1, (pos, neu, neg), checkRegion(pos, neu, neg), matrixMultiplication(pos, neu, neg), )