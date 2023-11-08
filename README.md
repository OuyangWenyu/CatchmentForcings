# CatchmentForcings

Forcing data downloader and processor for Watershed Hydrologic Modeling

**Note: this repository is still developing! and this readme file didn't cover all code**

This is a repository similar with CatchmentAttributes.

CatchmentAttributes is a repository to compile attributes data for hydrological modeling, while CatchmentForcings is for forcing data.

The source data we used include the following datasets:

- Daymet
- ECMWF ERA5-Land
- GHS
- MODIS ET
- NEX-GDDP-CMIP5/6
- NLDAS

## Set up conda environment

Run the following commands to install the dependencies:

```Shell
# conda 安装太慢，换mamba安装了，如果没有mamba，在base下安装一个
conda install mamba -c conda-forge
# base下没有jupyterlab的话，也要安装
conda install -c conda-forge jupyterlab jupyter_contrib_nbextensions ipyleaflet
# 然后安装环境
mamba env create -f environment.yml
```

There are some jupyter notebooks (.ipynb files). We recommend you to run them in jupyterlab:

```Shell
# 激活环境
conda activate CatchmentForcings
# 把hydroGIS的kernel显示到base的jupyterlab里
python -m ipykernel install --user --name CatchmentForcings --display-name "CatchmentForcings"
# 打开jupyterlab，如果你本来就是打开jupyterlab后，在终端里执行的这些操作，就不用再打开了
jupyter lab
```

## Source data

### Daymet

We download and process Daymet data for the 671 basins in [CAMELS(-US)](https://ral.ucar.edu/solutions/products/camels).

#### Download Daymet V4 dataset for basins in CAMELS

Use hydrobench/app/download/download_daymet_camels_basin.py to download daymet grid data for the boundaries of basins in
CAMELS.

#### Process the raw Daymet V4 data

We provided some scripts to process the Daymet grid data for basins:

- Regrid the raw data to the required resolutions (hydrobench/app/daymet4basins/regrid_daymet_nc.py)
- calculate_basin_mean_forcing_include_pet.py and calculate_basin_mean_values.pyin hydrobench/app/daymet4basins can be
  used for getting basin mean values
- If you want to get P (precipitation), PE (potential evapotranspiration), Q (streamflow) and Basin areas, please use
  hydrobench/app/daymet4basins/pbm_p_pe_q_basin_area.py

### ECMWF ERA5-Land

#### Download ERA5-Land data

Although we provide tools to use cds toolbox from ECMWF to retrieve ERA5-land data, it seems it didn't work well (even
when data is MB level). Hence, we recommend a manual way to download the ERA5-land data archive
from https://cds.climate.copernicus.eu/cdsapp#!/dataset/reanalysis-era5-land?tab=form

If we directly compile forcing data in GEE, we can directly run notebook in catchmentforcings\ecmwf4basins\download_era5land4basins_gee.ipynb

#### Process the downloaded ERA5-Land data

TODO: Regrid the raw data to the required resolutions (src/regrid.py from https://github.com/pangeo-data/WeatherBench)

### GHS

The dataset's full name is "Geospatial attributes and Hydrometeorological forcings of gages for Streamflow modeling".

"GHS" is an extension for [the CAMELS dataset](https://ral.ucar.edu/solutions/products/camels). It contains geospatial
attributes, hydrometeorological forcings and streamflow data of 9067 gages over the Contiguous United States (CONUS)
in [the GAGES-II dataset](https://water.usgs.gov/GIS/metadata/usgswrd/XML/gagesII_Sept2011.xml).

Now we have not provided an online way to download the data. You can refer to the following paper to learn about how to
get it.

Wenyu Ouyang, Kathryn Lawson, Dapeng Feng, Lei Ye, Chi Zhang, & Chaopeng Shen (2021). Continental-scale streamflow
modeling of basins with reservoirs: Towards a coherent deep-learning-based
strategy. https://doi.org/10.1016/j.jhydrol.2021.126455

### MODIS ET

#### Download basin mean ET data from GEE

We provided [Google Earth Engine](https://earthengine.google.com/) scripts to download the PML V2 and MODIS MOD16A2_105
product for given basins:

TODO: provide a link -- [Download basin mean values of ET data]()

#### Process ET data to CAMELS format

Use hydrobench\app\modis4basins\trans_modis_et_to_camels_format.py to process the downloaded ET data from GEE to the
format of forcing data in CAMELS

### NEX-GDDP-CMIP5/6

#### Download

NEX-GDDP-CMIP5 data for basins could be downloaded from Google Earth Engine. The code
is [here](https://code.earthengine.google.com/5edfca6263bea36f5c093fc6b80a68aa)

For NEX-GDDP-CMIP6, data should be downloaded
from [this website](https://www.nccs.nasa.gov/services/data-collections/land-based-products/nex-gddp-cmip6)

#### Process

Use hydrodataset/app/climateproj4basins/trans_nexdcp30_to_camels_format.py to process NEX-GDDP-CMIP5 data for basins

We will provide tool for NEX-GDDP-CMIP6 data soon

### NLDAS

#### Download basin mean NLDAS data from GEE

The GEE script is [here](https://code.earthengine.google.com/72cb2661f2206b4f986e24af3560c000)

#### Download NLDAS grid data from NASA Earth data

Use hydrobench/app/download/download_nldas_hourly.py to download them.

Notice: you should finish some necessary steps (see the comments in hydrobench/nldas4basins/download_nldas.py) before
using the script

#### Process NLDAS basin mean forcing

Use hydrobench/app/nldas4basins/trans_nldas_to_camels_format.py to transform the data to the format of forcing data in
CAMELS.

TODO: more processing scripts are needed for NLDAS grid data.

## Acknowledgement

- [HyRiver](https://github.com/cheginit/HyRiver)
- [WeatherBench](https://github.com/pangeo-data/WeatherBench)
