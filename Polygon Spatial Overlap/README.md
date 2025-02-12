# Spatial Overlap of Polygons
In this project, I designed a PyQGIS-based processing script for QGIS that calculates the spatial overlap of two polygon datasets. I measured the spatial overlap using the [Jaccard index](https://en.wikipedia.org/wiki/Jaccard_index), which calculates the percentage of area shared between two polygons divided by the total area of those polygons.

This script matches polygon features based on if their names are identical, and outputs those features with their corresponding Jaccard index. One process optimization I implemented was to use [dictionaries](https://docs.python.org/3/library/stdtypes.html#mapping-types-dict) when iteratively accessing feature geometries, which reduces the associated operations from an $O(n)$ runtime to an $O(1)$ runtime. Access the code [here!]()

Below is a map of those results, which displays spatial changes in ZIP Code Tabulation Areas in the United States between 2010 and 2020.

## Skills
Geospatial Data Analysis, Cartography

## Tools
QGIS, Python, PyQGIS

## Datasets
* [ZIP Code Tabulation Areas, U.S. Census Bureau (2010, 2020)](https://www.census.gov/programs-surveys/geography/guidance/geo-areas/zctas.html)
* [National Weather Service (2025)](https://www.weather.gov/gis/USStates)

## Map
