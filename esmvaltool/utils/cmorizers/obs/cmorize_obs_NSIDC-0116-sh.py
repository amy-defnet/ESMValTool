# pylint: disable=invalid-name
"""ESMValTool CMORizer for NSIDC-0116 data.

Tier
   Tier 2: other freely-available dataset.

Source
   https://nsidc.org/data/NSIDC-0116

Last access
   20190513

Download and processing instructions
    Download daily data from:
    https://nsidc.org/data/NSIDC-0116

    Login required for download, but requires citation only to use


"""
from .utilities import (read_cmor_config)
from .nsidc_common import cmorize


def cmorization(in_dir, out_dir):
    """Cmorization func call."""
    cfg = read_cmor_config('NSIDC-0116_sh.yml')
    cmorize(cfg, 'sh', in_dir, out_dir)
