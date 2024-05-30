"""
Transform the data format of NLDAS to the camels'
"""

import argparse
import os
import sys

import pandas as pd
from tqdm import tqdm

from pathlib import Path
from hydrodataset.camels import Camels

sys.path.append(os.path.dirname(Path(os.path.abspath(__file__)).parent.parent.parent))
import definitions
from catchmentforcings.app.app_utils import _2ndprocess
from catchmentforcings.nldas4basins.basin_nldas_process import (
    trans_daily_nldas_to_camels_format,
)


def main(args):
    nldas_dir = args.input_dir
    output_dir = args.output_dir
    if not os.path.isdir(nldas_dir):
        raise NotADirectoryError(
            "Please download the data manually and unzip it as you wanna!!!"
        )
    if not os.path.isdir(output_dir):
        os.makedirs(output_dir)
    region = args.name
    gage_file = args.gage_file
    sta_id_str = args.staid_str
    huc_str = args.huc02_str
    assert int(args.year_range[0]) < int(args.year_range[1])
    years = list(range(int(args.year_range[0]), int(args.year_range[1])))

    if region == "camels":
        camels = Camels(os.path.join(definitions.DATASET_DIR, "camels", "camels_us"))
        gage_dict = camels.read_site_info()
    elif os.path.isfile(gage_file):
        gage_dict = pd.read_csv(gage_file, dtype={sta_id_str: str, huc_str: str})
    else:
        raise FileNotFoundError("Please give it a gage_dict file")
    for i in tqdm(range(len(years)), leave=False):
        trans_daily_nldas_to_camels_format(
            nldas_dir, output_dir, gage_dict, region, years[i]
        )
    _2ndprocess(
        camels,
        gage_dict["gauge_id"].values,
        gage_dict,
        output_dir,
        one_grid_area=13.915**2,
        grids_num_file=os.path.join(
            definitions.ROOT_DIR,
            "catchmentforcings",
            "app",
            "nldas4basins",
            "NLDAS_camels_mean_basinlist.csv",
        ),
        var_lst=[
            "convective_fraction(-)",
        ],
        file_name="nldas_forcing_leap",
        table_sep=" ",
    )
    print("Trans finished")


# python trans_nldas_to_camels_format.py --input_dir /mnt/sdc/owen/datasets/NLDAS --output_dir /mnt/sdc/owen/datasets/NLDAS_DO --name do --gage_file /mnt/data/owen411/code/HydroBench/test/example_data/site_nobs_DO.csv --staid_str STAID --huc02_str HUC02 --year_range 1980 2021
# python trans_nldas_to_camels_format.py --input_dir /mnt/sdc/owen/datasets/NLDAS --output_dir /mnt/sdc/owen/datasets/NLDAS_CAMELS --name camels --year_range 1990 2019
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Trans NLDAS data to CAMELS format")
    parser.add_argument(
        "--input_dir",
        dest="input_dir",
        help="The directory of downloaded NLDAS data",
        default="C:\\Users\\wenyu\\Downloads\\drive-download-20240530T055402Z-001",
        type=str,
    )
    parser.add_argument(
        "--output_dir",
        dest="output_dir",
        help="The directory of transformed data",
        default="C:\\Users\\wenyu\\Downloads\\nldas4camels\\basin_mean_forcing",
        type=str,
    )
    parser.add_argument(
        "--name",
        dest="name",
        help="All files are named nldas_xx_avg/sum_mean_xxx, where xx is the NAME and xxx is the year",
        default="camels",
        type=str,
    )
    parser.add_argument(
        "--gage_file",
        dest="gage_file",
        help="The dict of gages",
        default=None,
        type=str,
    )
    parser.add_argument(
        "--staid_str",
        dest="staid_str",
        help="The name of gage id column, e.g. gauge_id, STAID",
        default="STAID",
        type=str,
    )
    parser.add_argument(
        "--huc02_str",
        dest="huc02_str",
        help="The name of huc02 column, e.g. huc02, HUC02",
        default="HUC02",
        type=str,
    )
    parser.add_argument(
        "--year_range",
        dest="year_range",
        help="The start and end years (right open interval)",
        default=[1990, 1992],
        nargs="+",
    )
    the_args = parser.parse_args()
    main(the_args)
