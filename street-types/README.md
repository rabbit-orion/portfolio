# Top Street Types in the United States
In this project, I designed a Python-based processing script that identifies street types from full street names in the United States, and calculates their summed lengths and the most common street type by U.S. county. I then mapped these findings on a BI dashboard using Looker Studio.

Street types were obtained from a [Postal Service data dictionary of road suffixes]() and from observations of road prefixes from county-level samples of road data from the Census Bureau; I obtained both datasets using Selenium- and FTP-based web scraping. I used Pandas to process and aggregate road names and GeoPandas to calculate road lengths, employing performance optimizations such as vectorization and list comprehension. I then processed [the results]() for use in web mapping, assigning county names using a [Census Bureau dictionary of INCITS codes]() and aggregating [street type lengths across the entire county](), and [visualized the results in Looker Studio](). Access the code [here]()!

## Skills
Data Analysis, Data Processing, Web Mapping

## Tools
Python (GeoPandas, FTP, Selenium), Looker Studio

## Datasets
* [TIGER/Line Roads, U.S. Census Bureau (2024)](https://www2.census.gov/geo/tiger/TIGER2024/ROADS/)
* [National County Codes, U.S. Census Bureau (2020)](https://www2.census.gov/geo/docs/reference/codes2020/national_county2020.txt)
* [C1 Street Suffix Abbreviations, U.S. Postal Service (2025)](https://pe.usps.com/text/pub28/28apc_002.htm)

# Data Products
You can access the visualization dashboard online at [this link](https://lookerstudio.google.com/u/1/reporting/a8965f30-21a3-4652-9ff3-2084c2ca0499/).
![Map of top street types in the U.S. by county]()
![Chart of top street types in the U.S. by mileage]()
