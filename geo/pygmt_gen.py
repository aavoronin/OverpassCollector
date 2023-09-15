import pygmt

def test_pygmt():

    # Load sample earth relief data
    grid = pygmt.datasets.load_earth_relief(resolution="10m", region=[-108, -103, 35, 40])

    fig = pygmt.Figure()
    fig.grdview(
        grid=grid,
        # Sets the view azimuth as 130 degrees, and the view elevation as 30 degrees
        perspective=[130, 30],
        # Sets the x- and y-axis labels, and annotates the west, south, and east axes
        frame=["xa", "ya", "WSnE"],
        # Sets a Mercator projection on a 15-centimeter figure
        projection="M15c",
        # Sets the height of the three-dimensional relief at 1.5 centimeters
        zsize="1.5c",
    )
    fig.show()