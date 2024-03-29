# Ladsweb downloader

This is a set of scripts to download remote sensing products from LADSWEB/ modwebsrv
API.

We split the download into two steps:
* Retrieve file URLs
* Retrieving files

## Retrieving URLs:
For usage:
	python3 get_urls.py -h

We need to define the product, the timespan and the region.
We define the region in the bbox.config file as:

	[REGION]	
	north = lat_north
	south = lat_sout
	east = lon_east
	west = lon_west

Dates are specified as yyyy-mm-dd

The urls are saved into a textfile named $REGION_$PRODUCT.csv

Examplary usage:
	python3 get_urls.py --region Africa --product VNP02DNB --collection 5110 --start 2019-09-01 --end 2019-09-03

Note: Calls to the API are bundled into increments of 100 days
Note: Upon error, verify that product + collection is specified correctly

## Filtering file list

ladsweb seems to somtimes return tiles that do not intersect the ROI;
Filter the file list with sed:

```bash
sed '/h08v05/!d' unfiltered_file.csv > filtered_file.csv
sed -i '/h08v05/!d' unfiltered_file.csv 
```


## Downloading data
The download scrip will download all urls from a file list (generated by get_urls.py). It verifies if files already have been downloaded and verifies checksums.

Example usage:
	python3 download.py --file_list Africa_CLDMSK_L2_VIIRS_SNPP.csv --folder /download/viirs/cldmsk/

Note: The script will remove urls form the file list for files that have been successfully downloaded


# Background

In theory, modwebsrv should provide the richest API to access the data.
https://ladsweb.modaps.eosdis.nasa.gov/tools-and-services/lws-classic/api.php
https://ladsweb.modaps.eosdis.nasa.gov/tools-and-services/lws-classic/quick-start.php

We can list products with
https://modwebsrv.modaps.eosdis.nasa.gov/axis2/services/MODAPSservices/listProducts

To get.
https://modwebsrv.modaps.eosdis.nasa.gov/axis2/services/MODAPSservices/searchForFiles?
product={product}&collection={collection}&
start={start}&stop={stop}&
north={north}&south={south}&west={west}&east={east}&
coordsOrTiles=coords&
dayNightBoth={dnb}

E.g.
https://modwebsrv.modaps.eosdis.nasa.gov/axis2/services/MODAPSservices/searchForFiles?
product=MOD09&collection=6&
start=2020-04-01&stop=2020-04-18&
north=35&south=30&west=-122&east=-118&
coordsOrTiles=coords&
dayNightBoth=D



I however noticed, that some products are not showing up here.

I therefore usually query the ladsweb webinterface (https://ladsweb.modaps.eosdis.nasa.gov/search/). This has the benifit to be able to explore through the GUI first. AFAIK, the api is not documented, but you can get the ladsweb urls of the files through.

https://ladsweb.modaps.eosdis.nasa.gov/api/v1/files/?
product={product}&
collection={collection}&
dateRanges={start}..{stop}&
areaOfInterest=x{west}y{north},x{east}y{south}&
nightCoverage={nigt_coverage}

You need to set header: 'X-Requested-With': 'XMLHttpRequest

This needs revision and documentation, but here is what I am working with:
https://github.com/NiklasPhabian/ladsweb_downloader
