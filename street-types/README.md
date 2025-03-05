# Top Street Types in the United States
In this project, I designed a Python-based processing script that identifies street types from full street names in the United States, and calculates their summed lengths and the most common street type by U.S. county. I then mapped these findings on a BI dashboard using Looker Studio.

Street types were obtained from a [Postal Service data dictionary of road suffixes](data%20sources/suffixes.csv) and from my own observations of road prefixes from county-level samples of road data from the Census Bureau; I obtained both datasets using Selenium- and FTP-based web scraping. I used Pandas to process and aggregate road names and GeoPandas to calculate road lengths, employing performance optimizations like list comprehensions. I then processed [the results](data%20outputs/street_type_statistics.csv) for use in web mapping, assigning county names using a [Census Bureau dictionary of INCITS codes](data%20sources/national_county2020.txt) and aggregating [street type lengths across the entire county](data%20outputs/street_statistics_summed.csv), and [visualized the results in Looker Studio](#data-products). Access the code [here](streettypes.ipynb)!

Note: Looker Studio does not display any features in Connecticut as Google has not updated their geos layer from counties to [county-equivalent planning regions](https://www.federalregister.gov/documents/2022/06/06/2022-12063/change-to-county-equivalents-in-the-state-of-connecticut).

## Skills
Data Analysis, Data Processing, Web Mapping

## Tools
Python (GeoPandas, FTP, Selenium), Jupyter Notebook, Looker Studio

## Datasets
* [TIGER/Line Roads, U.S. Census Bureau (2024)](https://www2.census.gov/geo/tiger/TIGER2024/ROADS/)
* [National County Codes, U.S. Census Bureau (2020)](https://www2.census.gov/geo/docs/reference/codes2020/national_county2020.txt)
* [C1 Street Suffix Abbreviations, U.S. Postal Service (2025)](https://pe.usps.com/text/pub28/28apc_002.htm)

# Data Products
You can access the visualization dashboard online at [this link](https://lookerstudio.google.com/reporting/a8965f30-21a3-4652-9ff3-2084c2ca0499).
![Map of top street types in the U.S. by county](data%20products/dashboard_1.png)
![Chart of top street types in the U.S. by mileage](data%20products/dashboard_2.png)
