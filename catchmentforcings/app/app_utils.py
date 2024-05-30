"""
Author: Wenyu Ouyang
Date: 2024-05-30 17:34:38
LastEditTime: 2024-05-30 22:09:37
LastEditors: Wenyu Ouyang
Description: some utils used in app
FilePath: \CatchmentForcings\catchmentforcings\app\app_utils.py
Copyright (c) 2023-2024 Wenyu Ouyang. All rights reserved.
"""

import pandas as pd
from tqdm import tqdm


import os
import definitions


def process_var_with_area_as_unit(
    gee_df_with_lst,
    output_dir,
    gage_dict,
    unit_grid_area,
    var_lst=["sm_surface"],
    file_name="smap",
    table_sep=",",
):
    """
    Process the variables with area as the unit.
    we should divide the variables by the area of the basin.
    """
    # Function to get gage and huc keys
    gage_key, huc02_key = get_gage_huc_keys(gage_dict)
    # Ensure variables in var_lst are evaluated as lists
    for var in var_lst:
        var_wo_unit = var.split("(")[0]
        gee_df_with_lst[var_wo_unit] = gee_df_with_lst[var_wo_unit].apply(eval)

    # Calculate grid_count for the first variable as an example
    gee_df_with_lst["grid_count"] = gee_df_with_lst[var_wo_unit].apply(
        lambda x: 1 if len(x) == 0 else len(x)
    )
    # Ensure both DataFrames are sorted by gage_key
    gee_df_with_lst = gee_df_with_lst.sort_values(by=gage_key).reset_index(drop=True)
    gage_dict = gage_dict.sort_values(by=gage_key).reset_index(drop=True)
    # Add grid_count to gage_dict
    gage_dict["grid_count"] = gee_df_with_lst["grid_count"]

    # Calculate conversion_ratio
    gage_dict["conversion_ratio"] = (
        gage_dict["grid_count"] * unit_grid_area
    ) / gage_dict["area_gages2"]

    for gage_id in tqdm(gage_dict[gage_key]):
        huc_id = gage_dict[gage_dict[gage_key] == gage_id][huc02_key].values[0]
        output_huc_dir = os.path.join(output_dir, huc_id)
        the_file = os.path.join(output_huc_dir, f"{gage_id}_lump_{file_name}.txt")

        # Read the existing data file
        the_data = pd.read_csv(the_file, sep=table_sep)

        # Apply conversion ratio to specified variables
        conversion_ratio = gage_dict[gage_dict[gage_key] == gage_id][
            "conversion_ratio"
        ].values[0]
        the_data[var_lst] = the_data[var_lst].multiply(conversion_ratio, axis="index")

        # Save the processed data back to the file
        the_data.to_csv(
            the_file, header=True, index=False, sep=table_sep, float_format="%.4f"
        )


def get_gage_huc_keys(gage_dict):
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
    return gage_id_key, huc02_key


def _2ndprocess(
    camels,
    basins_id,
    gage_dict,
    output_dir,
    one_grid_area=121,
    grids_num_file=os.path.join(
        definitions.ROOT_DIR,
        "catchmentforcings",
        "app",
        "smap4basins",
        "smap_camels591_meandaily_basinlist.csv",
    ),
    var_lst=["sm_surface"],
    file_name="smap",
    table_sep=",",
):
    # one day tolist file from gee to see the grids number of each basin
    df = pd.read_csv(grids_num_file, dtype={"gage_id": str})
    df["gage_id"] = df["gage_id"].str.zfill(8)
    area_dataset = camels.read_area(basins_id)
    # Convert the xarray dataset to a pandas dataframe
    area_df = area_dataset.to_dataframe().reset_index()
    merged_df_corrected = pd.merge(
        gage_dict, area_df, left_on="gauge_id", right_on="basin", how="left"
    ).drop(columns=["basin"])
    gage_key, huc02_key = get_gage_huc_keys(gage_dict)
    df = df.rename(columns={"gage_id": gage_key})
    process_var_with_area_as_unit(
        df,
        output_dir,
        merged_df_corrected,
        one_grid_area,
        var_lst,
        file_name,
        table_sep,
    )
