def print_issue(issue_type, details, suggestion):
    print(f"ISSUE: {issue_type}")
    print("#"*60)
    for detail in details:
        print(detail)
    print("#"*60)
    print(f"WARNING: {suggestion}\n")


def print_no_issue(issue_type, detail):
    print(f"NO ISSUE: {issue_type}: {detail}")


def checkPixelSize(crop_mask, raster_data):
    if crop_mask.res != raster_data.res:
        print_issue("PIXEL SIZE MISMATCH",
                    [f"Mask Pixel Size        : {crop_mask.res}",
                        f"Predicotr Pixel Size   : {raster_data.res}"],
                    "Resampling The Mask Is Required.")
    else:
        print_no_issue(
            "The pixel sizes of the mask and predictor are identical", crop_mask.res)


def checkProjection(crs_name1, crs_name2, data1_name, data2_name):
    if crs_name1 != crs_name2:
        print_issue(f"The projections of the {data1_name} and {data2_name} are not identical",
                    [f"{data1_name} CRS: {crs_name1}",
                        f"{data2_name} CRS: {crs_name2}"],
                    f"Consider reprojecting the {data1_name} to match the projection of the {data2_name}.")
    else:
        print_no_issue(
            f"The projections of the {data1_name} and {data2_name} are identical", crs_name1)
