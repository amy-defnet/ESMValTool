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

def create_provenance_record():
    """Create a provenance record."""
    record = {
        'caption': "Forcings for the ParFlow hydrological model.",
        'domains': ['global'],
        'authors': [
            'defnet_amy',
        ],
        'projects': [
            'ewatercycle',
        ],
        'references': [
            'acknow_project',
        ],
        'ancestors': [],
    }
    return record

def make_filename(metadata, cfg, extension='nc'):
    """
    Return a valid path for saving a diagnostic data file.
    """
    # Use first variable set for defining dataset, start year, end year
    attributes = metadata[0]

    # Define output file name and full path
    base_name = f"{attributes['alias']}/{attributes['alias']}.forcing.hourly.{attributes['start_year']}.{attributes['end_year']}"
    filename = get_diagnostic_filename(base_name, cfg, extension=extension)
    return filename

def get_input_cubes(metadata):
    """Create a dict with all (preprocessed) input files."""

    # Crosswalk to ParFlow-specific variable names
    parflow_varname_xwalk = {
        'tas':'Temp',
        'pr':'APCP',
        'ps':'Press', 
        'uas':'UGRD',
        'vas':'VGRD'
    }

    provenance = create_provenance_record()

    # Create dictionary, all_vars, to store {ParFlow varname}: {data cube} pairs
    all_vars = {}
    for attributes in metadata:
        short_name = attributes['short_name']
        if short_name in all_vars:
            raise ValueError(
                f"Multiple input files found for variable '{short_name}'.")
        filename = attributes['filename']

        logger.info("Loading variable %s", short_name)
        cube = iris.load_cube(filename)

        # Rename variable name using ParFlow variable naming conventions
        cube.var_name = parflow_varname_xwalk[short_name]

        all_vars[parflow_varname_xwalk[short_name]] = cube

        provenance['ancestors'].append(filename)

    return all_vars, provenance

def main(cfg):
    input_metadata = cfg['input_data'].values()

    for dataset, metadata in group_metadata(input_metadata, 'dataset').items():
        all_vars, provenance = get_input_cubes(metadata)
        cubes = iris.cube.CubeList(all_vars.values())

        output_filename = make_filename(metadata, cfg, extension='nc')
        print("Output file: ", output_filename)
        Path(output_filename).parent.mkdir(exist_ok=True)

        # Save output file
        iris.save(cubes, output_filename)

        # Store provenance
        with ProvenanceLogger(cfg) as provenance_logger:
            provenance_logger.log(output_filename, provenance)

#       # # Store provenance
#       # provenance_record = create_provenance_record(attributes)
#       # with ProvenanceLogger(cfg) as provenance_logger:
#       #     provenance_logger.log(output_filename, provenance_record)


if __name__ == '__main__':

    with run_diagnostic() as config:
        main(config)
