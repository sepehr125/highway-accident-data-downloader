# National Highway Traffic Saftey Administration - Data Downloader + Converter

The NHTSA has a treasure trove of data on highway accidents going back several decades (to 1975) in a database called FARS. Unfortunately, the data is saved in obscure file formats (DBF and SAS) on an FTP server, which makes it harder to access. 

You can use this script to download, and automatically unzip and convert to CSV, data for a given range of years. It requires the [dbf](https://pypi.python.org/pypi/dbf) package for converting the DBF files, and python3. 

The eventual goal of this project is to neatly organize the data in a PostGres database for ready analysis across time. There are serious data integrity challenges in the way. Over the years, some columns have moved between files, some fields have been discontinued or merged with others, and conventions for denoting missing data have changed. These fields must be standardized before the data can be properly housed in a database.   

I'm wading my way through this 500+ page [User Guide](ftp://ftp.nhtsa.dot.gov/fars/FARS-DOC/USERGUIDE-2014.pdf) to standardize at least the past decade of data.  

This project is in its infancy. Feel free to reach out if you'd like to get involved, or if you run into issues using the script: [@sepehr125](https://twitter.com/sepehr125)

## Overview:
- FARS data home:  
ftp://ftp.nhtsa.dot.gov/fars/
- A list of files and their content are here:  
ftp://ftp.nhtsa.dot.gov/fars/FileList.pdf

---------------
## TO DO:
- Standardize data, at least for the past decade, and place into a database. Make use of native datetime and lat/long fields to make analysis easier. 
- Make foreign key field for each accident unique across all years. Currently, the ST_CASE field is only unique to each year!
- Map codes for identifying states, etc. to actual state abbreviations. Generally give fields more readily understandable names, with reversible mapping, of course.
- 