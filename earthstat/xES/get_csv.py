import glob
import pandas as pd
from datetime import datetime


def get_merged_csv(area_name, workflow, kelvin_to_celsius=False, output_name=None):

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    files_to_merge = glob.glob(f'{area_name}_Aggregated_{workflow}_csv/*.csv')

    common_columns = _common_columns_csvs(files_to_merge)
    merged_df = pd.read_csv(files_to_merge[0])

    for file in files_to_merge[1:]:
        temp_df = pd.read_csv(file)
        merged_df = pd.merge(merged_df, temp_df,
                             on=common_columns, how='outer')

    # modify the date
    merged_df['date'] = pd.to_datetime(merged_df['date'])

    if kelvin_to_celsius:
        temperature_columns = ['Temperature_Air_2m_Max_24h',
                               'Temperature_Air_2m_Min_24h', 'Temperature_Air_2m_Mean_24h']
        conversion_factor = 273.15

        for column in temperature_columns:
            if column in merged_df.columns:
                merged_df[column] -= conversion_factor
            else:
                print(f"Column {column} does not exist in the DataFrame.")

    # make the date column the first column
    merged_columns = merged_df.columns.tolist()
    merged_columns.remove('date')
    merged_df = merged_df[['date'] + merged_columns]

    if output_name:
        filename = f'{output_name}_{workflow}_{timestamp}.csv'
        merged_df.to_csv(filename, index=False)

    else:
        filename = f'AgERA5_{area_name}_merged_parameters_{workflow}_{timestamp}.csv'
        merged_df.to_csv(filename, index=False)


def _common_columns_csvs(file_paths):
    dataframes = [pd.read_csv(file_path) for file_path in file_paths]
    common_cols = list(set.intersection(
        *[set(df.columns) for df in dataframes]))
    return common_cols
