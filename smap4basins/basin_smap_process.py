"""
Author: Wenyu Ouyang
Date: 2022-01-18 20:04:58
LastEditTime: 2022-01-19 00:39:51
LastEditors: Wenyu Ouyang
Description: Process SMAP data for basins
FilePath: /HydroBench/hydrodataset/smap4basins/basin_smap_process.py
Copyright (c) 2021-2022 Wenyu Ouyang. All rights reserved.
"""
import datetime
import fnmatch
import os
import numpy as np
import pandas as pd


def trans_nasa_usda_smap_to_camels_format(
        source_dir, output_dir, gage_dict, region, year
):
    """
    Transform 3-day SMAP data downloaded from GEE to the format in CAMELS.

    Parameters
    ----------
    source_dir
        the original data's directory
    output_dir
        the transformed data's directory
    gage_dict
        a dict containing gage's ids and the correspond HUC02 ids
    region
        we named the file downloaded from GEE as NASA_USDA_HSL_SMAP10KM_soil_moisture__<region>_mean_<year>.csv,
        because we use GEE code to generate data for each year for each shape file (region) containing some basins.
        For example, if we use the basins' shpfile in CAMELS, the region is "camels".
    year
        we use GEE code to generate data for each year, so each year for each region has one data file.
    Returns
    -------
    None

    """
    # you can add features or delete features, or change the order, which depends on your txt content
    smap_dataset = [
        "hru_id",
        "system:time_start",
        "ssm",
        "susm",
        "smp",
        "ssma",
        "susma",
    ]
    camels_format_index = [
        "Year",
        "Mnth",
        "Day",
        "Hr",
        "ssm(mm)",
        "susm(mm)",
        "smp(-)",
        "ssma(-)",
        "susma(-)",
    ]

    if "STAID" in gage_dict.keys():
        gage_id_key = "STAID"
    elif "gauge_id" in gage_dict.keys():
        gage_id_key = "gauge_id"
    elif "gage_id" in gage_dict.keys():
        gage_id_key = "gage_id"
    else:
        raise NotImplementedError("No such gage id name")

    if "HUC02" in gage_dict.keys():
        huc02_key = "HUC02"
    elif "huc_02" in gage_dict.keys():
        huc02_key = "huc_02"
    else:
        huc02_key = None

    # because this function only work for one year and one region, it's better to chose avg and sum files at first
    for f_name in os.listdir(source_dir):
        if fnmatch.fnmatch(
                f_name,
                "NASA_USDA_HSL_SMAP10KM_soil_moisture_"
                + region
                + "_mean_"
                + str(year)
                + "*.csv",
        ):
            smap_data_file = os.path.join(source_dir, f_name)

    data_temp = pd.read_csv(smap_data_file, sep=",", dtype={smap_dataset[0]: str})
    for i_basin in range(len(gage_dict[gage_id_key])):
        basin_data = data_temp[
            data_temp[smap_dataset[0]].values.astype(int)
            == int(gage_dict[gage_id_key][i_basin])
            ]
        if basin_data.shape[0] == 0:
            raise ArithmeticError("chosen basins' number is zero")
        # get Year,Month,Day,Hour info
        csv_date = pd.to_datetime(basin_data[smap_dataset[1]].values)
        # the hour is set to 12, as 12 is the average hour of a day
        year_month_day_hour = pd.DataFrame(
            [[dt.year, dt.month, dt.day, 12] for dt in csv_date],
            columns=camels_format_index[0:4],
        )
        data_df = pd.DataFrame(
            basin_data.iloc[:, 2:].values, columns=camels_format_index[4:]
        )
        # concat
        new_data_df = pd.concat([year_month_day_hour, data_df], axis=1)
        # output the result
        if huc02_key is None:
            output_huc_dir = output_dir
        else:
            huc_id = gage_dict[huc02_key][i_basin]
            output_huc_dir = os.path.join(output_dir, huc_id)
        if not os.path.isdir(output_huc_dir):
            os.makedirs(output_huc_dir)
        output_file = os.path.join(
            output_huc_dir, str(gage_dict[gage_id_key][i_basin]) + "_lump_nasa_usda_smap.txt"
        )
        print("output SMAP data of", gage_dict[gage_id_key][i_basin], "year", str(year))
        if os.path.isfile(output_file):
            data_old = pd.read_csv(output_file)
            years = np.unique(data_old[camels_format_index[0]].values)
            if year in years:
                continue
            else:
                os.remove(output_file)
                new_data_df = pd.concat([data_old, new_data_df]).sort_values(
                    by=camels_format_index[0:3]
                )
        new_data_df.to_csv(
            output_file, header=True, index=False, sep=",", float_format="%.4f"
        )
