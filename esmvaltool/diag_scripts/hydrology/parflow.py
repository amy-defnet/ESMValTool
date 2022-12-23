"""ParFlow diagnostic."""
import logging
from pathlib import Path

import dask.array as da
import iris
import numpy
import pandas

from esmvaltool.diag_scripts.shared import (ProvenanceLogger,
                                            get_diagnostic_filename,
                                            group_metadata, run_diagnostic)

logger = logging.getLogger(Path(__file__).name)


# def create_provenance_record(attributes):
#     """Create a provenance record."""
#     ancestor_file = attributes['filename']

#     record = {
#         'caption': "Forcings for the ParFlow hydrological model.",
#         'domains': ['global'],
#         'authors': [
#             'defnet_amy',
#         ],
#         'projects': [
#             'ewatercycle',
#         ],
#         'references': [
#             'acknow_project',
#         ],
#         'ancestors': [ancestor_file],
#     }
#     return record

def make_filename(attributes, cfg, varname_xwalk, num_hours, extension='nc'):
    """
    Return a valid path for saving a diagnostic data file.
    
    File names are specific to ParFlow.
    """
    short_name = attributes["short_name"]
    try:
        parflow_varname = varname_xwalk[short_name]
    except:
        raise ValueError(f'Input variable {short_name} not recognized as input variable for ParFlow recipe.')

    # Set up istep in file name, padded to always consist of six characters
    start_timestep = str(1).zfill(6)
    end_timestep = str(num_hours).zfill(6)

    # Define output file name and full path
    base_name = f"{attributes['alias']}/{attributes['start_year']}/{attributes['alias']}.{parflow_varname}.{start_timestep}_to_{end_timestep}"
    filename = get_diagnostic_filename(base_name, cfg, extension=extension)
    return filename


def main(cfg):
    """Process data for use as input to the ParFlow hydrological model."""

    # Crosswalk to ParFlow-specific variable names
    parflow_varname_xwalk = {
        'tas':'Temp',
        'pr':'APCP',
        'ps':'Press'
    }

    input_data = cfg['input_data'].values()
    grouped_input_data = group_metadata(input_data,
                                        'long_name',
                                        sort='dataset')

    print("grouped_input_data: ", grouped_input_data)
    for long_name in grouped_input_data:
        logger.info("Processing variable %s", long_name)

        for attributes in grouped_input_data[long_name]:
            logger.info("Processing dataset %s", attributes['dataset'])

            # TO DO: create 'process_data' function(?)
            # Read in data cube
            input_file = attributes['filename']
            cube = iris.load_cube(input_file)

            # Rename variable name using ParFlow variable naming conventions
            cube.var_name = parflow_varname_xwalk[attributes['short_name']]

            # Get number of hours in cube
            num_hours = cube.coord('time').shape[0]

            # Set up file name for saving data
            output_filename = make_filename(
                    attributes, cfg, parflow_varname_xwalk, num_hours, extension='nc'
                )
            print("Output file: ", output_filename)
            Path(output_filename).parent.mkdir(exist_ok=True)

            # Save output file
            iris.save(cube, output_filename)

            # # Store provenance
            # provenance_record = create_provenance_record(attributes)
            # with ProvenanceLogger(cfg) as provenance_logger:
            #     provenance_logger.log(output_filename, provenance_record)


if __name__ == '__main__':

    with run_diagnostic() as config:
        main(config)

# Notes:
# grouped_input_data:  {'Near-Surface Air Temperature': [{'alias': 'ERA5', 'dataset': 'ERA5', 'diagnostic': 'parflow', 'end_year': 1990, 'filename': '/Users/ad9465/Documents/Scratch/esmvaltool_tutorial/esmvaltool_output/recipe_parflow_20221220_195637/preproc/parflow/tas/native6_ERA5_reanaly_1_E1hr_tas_1990-1990.nc', 'frequency': '1hrPt', 'long_name': 'Near-Surface Air Temperature', 'mip': 'E1hr', 'modeling_realm': ['atmos'], 'preprocessor': 'rough_cutout', 'project': 'native6', 'recipe_dataset_index': 0, 'short_name': 'tas', 'standard_name': 'air_temperature', 'start_year': 1990, 'tier': 3, 'timerange': '1990/1990', 'type': 'reanaly', 'units': 'K', 'variable_group': 'tas', 'version': 1}]}
# Output file:  /Users/ad9465/Documents/Scratch/esmvaltool_tutorial/esmvaltool_output/recipe_parflow_20221220_195637/work/parflow/script/ERA5/Temp.txt
