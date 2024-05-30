"""
Author: Wenyu Ouyang
Date: 2022-01-18 23:30:01
LastEditTime: 2024-05-30 22:27:44
LastEditors: Wenyu Ouyang
Description: Trans SMAP data to CAMELS format
FilePath: \CatchmentForcings\catchmentforcings\app\smap4basins\trans_smap_to_camels_format.py
Copyright (c) 2021-2022 Wenyu Ouyang. All rights reserved.
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
from catchmentforcings.smap4basins.basin_smap_process import (
    trans_nasa_usda_smap_to_camels_format,
    trans_smap_to_camels_format,
)


def main(args):
    dataset_name = args.dataset_name
    smap_dir = args.input_dir
    output_dir = args.output_dir
    if not os.path.isdir(smap_dir):
        raise NotADirectoryError(
            "Please download the data manually and unzip it as you wanna!!!"
        )
    if not os.path.isdir(output_dir):
        os.makedirs(output_dir)
    region = args.region
    assert int(args.year_range[0]) < int(args.year_range[1])
    years = list(range(int(args.year_range[0]), int(args.year_range[1])))

    camels = Camels(os.path.join(definitions.DATASET_DIR, "camels", "camels_us"))
    gage_dict = camels.read_site_info()
    if region == "camels591":
        camels591id = pd.read_csv(
            os.path.join(
                definitions.ROOT_DIR,
                "catchmentforcings",
                "app",
                "smap4basins",
                "camels591frommtlpaper.csv",
            ),
            dtype={"GAGE_ID": str},
        )["GAGE_ID"].tolist()
        gage_dict = gage_dict.set_index("gauge_id").loc[camels591id].reset_index()
    if dataset_name == "SMAP":
        _2ndprocess(camels, camels591id, gage_dict, output_dir)
    for i in tqdm(range(len(years)), leave=False):
        if dataset_name == "NASA_USDA_SMAP":
            trans_nasa_usda_smap_to_camels_format(
                smap_dir, output_dir, gage_dict, region, years[i]
            )
        elif dataset_name == "SMAP":
            trans_smap_to_camels_format(
                smap_dir, output_dir, gage_dict, region, years[i]
            )
        else:
            raise FileNotFoundError(
                "No such data! Please check if you have chosen correctly. "
                "We only provide PML_V2 and MOD16A2_105 now!"
            )

    print("Trans finished")


# python trans_smap_to_camels_format.py --dataset_name NASA_USDA_SMAP --input_dir /mnt/sdc/owen/datasets/SMAP10KM --output_dir /mnt/sdc/owen/datasets/NASA_USDA_SMAP_CAMELS --year_range 2015 2022
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Trans SMAP data of each basin to CAMELS format"
    )
    parser.add_argument(
        "--dataset_name",
        dest="dataset_name",
        help="The downloaded SMAP data",
        default="SMAP",
        type=str,
    )
    parser.add_argument(
        "--input_dir",
        dest="input_dir",
        help="The directory of downloaded SMAP data",
        default="C:\\Users\\wenyu\\Downloads\\drive-download-20240530T055402Z-001",
        type=str,
    )
    parser.add_argument(
        "--output_dir",
        dest="output_dir",
        help="The directory of transformed data",
        default="C:\\Users\\wenyu\\Downloads\\SMAP_CAMELS",
        type=str,
    )
    parser.add_argument(
        "--year_range",
        dest="year_range",
        help="The start and end years (right open interval)",
        default=[2015, 2024],
        nargs="+",
    )
    parser.add_argument(
        "--region",
        dest="region",
        help="region name",
        default="camels591",
        type=str,
    )
    the_args = parser.parse_args()
    main(the_args)
