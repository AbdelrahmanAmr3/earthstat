def get_retrieve_params(parameter, area=[71, -31, 34.5, 40], start_year=None, end_year=None):

    # Set end_year to start_year if not provided
    if end_year is None:
        end_year = start_year

    # AgERA5 Dictionary
    AgERA5_parm = {
        'Maximum_Temperature': {'2m_temperature': '24_hour_maximum'},
        'Minimum_Temperature': {'2m_temperature': '24_hour_minimum'},
        'Mean_Temperature': {'2m_temperature': '24_hour_mean'},
        'Solar_Radiation_Flux': {'solar_radiation_flux': None},
        'Precipitation_Flux': {'precipitation_flux': None},
        'Wind_Speed': {'10m_wind_speed': '24_hour_mean'},
        'Vapour_Pressure': {'vapour_pressure': '24_hour_mean'}
    }

    # Check if the parameter is in the AgERA5_parm dictionary
    if parameter in AgERA5_parm:
        # Extract the variable and statistic
        variable_statistic_pair = AgERA5_parm[parameter]
        variable, statistic = list(variable_statistic_pair.items())[0]

        # Construct the return dictionary
        retrieve_params = {
            'version': '1_1',
            'format': 'zip',
            'area': area,
            'variable': variable,
            'year': [str(year) for year in range(start_year, end_year + 1)],
            'month': ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12'],
            'day': [
                '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12',
                '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24',
                '25', '26', '27', '28', '29', '30', '31',
            ]
        }

        # Add 'statistic' to the dictionary if it's not None
        if statistic is not None:
            retrieve_params['statistic'] = statistic

        return retrieve_params
    else:
        raise ValueError(
            "parameter not found. The Right parameters are:\n Maximum Temperature, Minimum Temperature, Mean Temperature, Solar Radiation Flux, Precipitation Flux, Wind Speed")
