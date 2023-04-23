"""
Author: Wenyu Ouyang
Date: 2023-04-22 15:43:44
LastEditTime: 2023-04-23 09:07:33
LastEditors: Wenyu Ouyang
Description: 
FilePath: \CatchmentForcings\catchmentforcings\app\daymet4basins\trans_daymet_to_camels_format.py
Copyright (c) 2023-2024 Wenyu Ouyang. All rights reserved.
"""
import argparse
import os

import numpy as np
import sys

import pandas as pd

from pathlib import Path

sys.path.append(os.path.dirname(Path(os.path.abspath(__file__)).parent.parent.parent))
import definitions
from catchmentforcings.daymet4basins.basin_daymet_process import (
    insert_daymet_value_in_leap_year,
    trans_daymet_to_camels_format,
)
from catchmentforcings.data.data_gages import Gages


def choose_gages_in_dict(gage_dict, given_ids):
    """given a list of gage ids, return the gage dict with only the given ids"""
    all_ids = gage_dict["STAID"]
    if not set(given_ids).issubset(set(all_ids)):
        raise ValueError("The given id is not in the gage dict")
    else:
        index = np.where(np.isin(all_ids, given_ids))[0]
    chosen_df = pd.DataFrame(gage_dict).iloc[index]
    return chosen_df.to_dict(orient="list")


def trans_daymet(args):
    daymet_dir = args.input_dir
    output_dir = args.output_dir
    if not os.path.isdir(daymet_dir):
        raise NotADirectoryError(
            "The input directory "
            + daymet_dir
            + " is not a directory! Please check the input directory."
        )
    if not os.path.isdir(output_dir):
        os.makedirs(output_dir)
    gage_id_file = args.gage_file
    assert int(args.year_range[0]) < int(args.year_range[1])
    years = list(range(int(args.year_range[0]), int(args.year_range[1])))

    gage_ids_chosen = (
        pd.read_csv(gage_id_file, dtype={"GAUGE_ID": str}).iloc[:, 0].values.tolist()
    )
    gages_dir = os.path.join(definitions.DATASET_DIR, "hydro-dl-reservoir-data")
    gages = Gages(gages_dir)
    gage_dict = gages.gages_sites
    chosen_gage_dict = choose_gages_in_dict(gage_dict, gage_ids_chosen)
    region = "NorthEast"
    for year in years:
        trans_daymet_to_camels_format(
            daymet_dir, output_dir, chosen_gage_dict, region, year
        )
        insert_daymet_value_in_leap_year(
            output_dir,
            t_range=[f"{str(year)}-01-01", f"{str(year + 1)}-01-01"],
        )
    print("Trans finished")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Trans Daymet data to CAMELS format")
    parser.add_argument(
        "--input_dir",
        dest="input_dir",
        help="The directory of downloaded Daymet data",
        default=os.path.join(
            definitions.DATASET_DIR,
            "hydro-dl-reservoir-data",
            "gagesII_forcing",
            "daymet",
        ),
        type=str,
    )
    parser.add_argument(
        "--output_dir",
        dest="output_dir",
        help="The directory of transformed data",
        default=os.path.join(
            definitions.ROOT_DIR, "test", "test_data", "basin_mean_forcing"
        ),
        type=str,
    )
    parser.add_argument(
        "--gage_file",
        dest="gage_file",
        help="The file of gages ids, it must contain a column called 'GAUGE_ID' and the column is the gage ids",
        default=os.path.join(
            definitions.ROOT_DIR, "catchmentforcings", "app", "gage_id.csv"
        ),
        type=str,
    )
    parser.add_argument(
        "--year_range",
        dest="year_range",
        help="The start and end years (right open interval)",
        default=[1980, 2020],
        nargs="+",
    )
    the_args = parser.parse_args()
    trans_daymet(the_args)
