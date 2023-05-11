import itertools
import os

import numpy as np
import pytest
from conftest import codc, odc_modules


def exception_map(module, exception):
    if not codc:
        return exception
    return codc.ODCException if module == codc else exception


data_file1 = os.path.join(os.path.dirname(__file__), "data/data1.odb")

data_file1_bitfields = {
    "report_status@hdr": [
        {"name": "active", "offset": 0, "size": 1},
        {"name": "passive", "offset": 1, "size": 1},
        {"name": "rejected", "offset": 2, "size": 1},
        {"name": "blacklisted", "offset": 3, "size": 1},
        {"name": "use_emiskf_only", "offset": 4, "size": 1},
    ],
    "report_event1@hdr": [
        {"name": "no_data", "offset": 0, "size": 1},
        {"name": "all_rejected", "offset": 1, "size": 1},
        {"name": "bad_practice", "offset": 2, "size": 1},
        {"name": "rdb_rejected", "offset": 3, "size": 1},
        {"name": "redundant", "offset": 4, "size": 1},
        {"name": "stalt_missing", "offset": 5, "size": 1},
        {"name": "qc_failed", "offset": 6, "size": 1},
        {"name": "overcast_ir", "offset": 7, "size": 1},
        {"name": "thinned", "offset": 8, "size": 1},
        {"name": "latlon_corrected", "offset": 9, "size": 1},
        {"name": "stalt_corrected", "offset": 10, "size": 1},
    ],
    "report_rdbflag@hdr": [
        {"name": "lat_humon", "offset": 0, "size": 1},
        {"name": "lat_qcsub", "offset": 1, "size": 1},
        {"name": "lat_override", "offset": 2, "size": 1},
        {"name": "lat_flag", "offset": 3, "size": 2},
        {"name": "lat_hqc_flag", "offset": 5, "size": 1},
        {"name": "lon_humon", "offset": 6, "size": 1},
        {"name": "lon_qcsub", "offset": 7, "size": 1},
        {"name": "lon_override", "offset": 8, "size": 1},
        {"name": "lon_flag", "offset": 9, "size": 2},
        {"name": "lon_hqc_flag", "offset": 11, "size": 1},
        {"name": "date_humon", "offset": 12, "size": 1},
        {"name": "date_qcsub", "offset": 13, "size": 1},
        {"name": "date_override", "offset": 14, "size": 1},
        {"name": "date_flag", "offset": 15, "size": 2},
        {"name": "date_hqc_flag", "offset": 17, "size": 1},
        {"name": "time_humon", "offset": 18, "size": 1},
        {"name": "time_qcsub", "offset": 19, "size": 1},
        {"name": "time_override", "offset": 20, "size": 1},
        {"name": "time_flag", "offset": 21, "size": 2},
        {"name": "time_hqc_flag", "offset": 23, "size": 1},
        {"name": "stalt_humon", "offset": 24, "size": 1},
        {"name": "stalt_qcsub", "offset": 25, "size": 1},
        {"name": "stalt_override", "offset": 26, "size": 1},
        {"name": "stalt_flag", "offset": 27, "size": 2},
        {"name": "stalt_hqc_flag", "offset": 29, "size": 1},
    ],
    "level@conv_body": [
        {"name": "maxwind", "offset": 0, "size": 1},
        {"name": "tropopause", "offset": 1, "size": 1},
        {"name": "d_part", "offset": 2, "size": 1},
        {"name": "c_part", "offset": 3, "size": 1},
        {"name": "b_part", "offset": 4, "size": 1},
        {"name": "a_part", "offset": 5, "size": 1},
        {"name": "surface", "offset": 6, "size": 1},
        {"name": "signwind", "offset": 7, "size": 1},
        {"name": "signtemp", "offset": 8, "size": 1},
    ],
    "datum_anflag@body": [
        {"name": "final", "offset": 0, "size": 4},
        {"name": "fg", "offset": 4, "size": 4},
        {"name": "depar", "offset": 8, "size": 4},
        {"name": "varqc", "offset": 12, "size": 4},
        {"name": "blacklist", "offset": 16, "size": 4},
        {"name": "ups", "offset": 20, "size": 1},
        {"name": "uvt", "offset": 21, "size": 1},
        {"name": "uhu", "offset": 22, "size": 1},
        {"name": "ut2", "offset": 23, "size": 1},
        {"name": "uh2", "offset": 24, "size": 1},
        {"name": "uv1", "offset": 25, "size": 1},
        {"name": "urr", "offset": 26, "size": 1},
        {"name": "usn", "offset": 27, "size": 1},
        {"name": "usst", "offset": 28, "size": 1},
    ],
    "datum_status@body": [
        {"name": "active", "offset": 0, "size": 1},
        {"name": "passive", "offset": 1, "size": 1},
        {"name": "rejected", "offset": 2, "size": 1},
        {"name": "blacklisted", "offset": 3, "size": 1},
        {"name": "use_emiskf_only", "offset": 4, "size": 1},
    ],
    "datum_event1@body": [
        {"name": "vertco_missing", "offset": 0, "size": 1},
        {"name": "obsvalue_missing", "offset": 1, "size": 1},
        {"name": "fg_missing", "offset": 2, "size": 1},
        {"name": "rdb_rejected", "offset": 3, "size": 1},
        {"name": "assim_cld_flag", "offset": 4, "size": 1},
        {"name": "bad_practice", "offset": 5, "size": 1},
        {"name": "vertpos_outrange", "offset": 6, "size": 1},
        {"name": "fg2big", "offset": 7, "size": 1},
        {"name": "depar2big", "offset": 8, "size": 1},
        {"name": "obs_error2big", "offset": 9, "size": 1},
        {"name": "datum_redundant", "offset": 10, "size": 1},
        {"name": "level_redundant", "offset": 11, "size": 1},
        {"name": "not_analysis_varno", "offset": 12, "size": 1},
        {"name": "duplicate", "offset": 13, "size": 1},
        {"name": "levels2many", "offset": 14, "size": 1},
        {"name": "level_selection", "offset": 15, "size": 1},
        {"name": "vertco_consistency", "offset": 16, "size": 1},
        {"name": "vertco_type_changed", "offset": 17, "size": 1},
        {"name": "combined_flagging", "offset": 18, "size": 1},
        {"name": "report_rejected", "offset": 19, "size": 1},
        {"name": "varqc_performed", "offset": 20, "size": 1},
        {"name": "obserror_increased", "offset": 21, "size": 1},
        {"name": "contam_cld_flag", "offset": 22, "size": 1},
        {"name": "contam_rain_flag", "offset": 23, "size": 1},
        {"name": "contam_aerosol_flag", "offset": 24, "size": 1},
        {"name": "bad_emissivity", "offset": 25, "size": 1},
        {"name": "model_cld_flag", "offset": 26, "size": 1},
    ],
    "datum_rdbflag@body": [
        {"name": "press_humon", "offset": 0, "size": 1},
        {"name": "press_qcsub", "offset": 1, "size": 1},
        {"name": "press_override", "offset": 2, "size": 1},
        {"name": "press_flag", "offset": 3, "size": 2},
        {"name": "press_hqc_flag", "offset": 5, "size": 1},
        {"name": "press_judged_prev_an", "offset": 6, "size": 2},
        {"name": "press_used_prev_an", "offset": 8, "size": 1},
        {"name": "_press_unused_6", "offset": 9, "size": 6},
        {"name": "varno_humon", "offset": 15, "size": 1},
        {"name": "varno_qcsub", "offset": 16, "size": 1},
        {"name": "varno_override", "offset": 17, "size": 1},
        {"name": "varno_flag", "offset": 18, "size": 2},
        {"name": "varno_hqc_flag", "offset": 20, "size": 1},
        {"name": "varno_judged_prev_an", "offset": 21, "size": 2},
        {"name": "varno_used_prev_an", "offset": 23, "size": 1},
    ],
}


@pytest.mark.parametrize("odyssey", odc_modules)
def test_error_handling(odyssey):
    """Ensure that exceptions in the C++ layer are caught and forwarded as python exceptions"""
    with pytest.raises(exception_map(odyssey, FileNotFoundError)):
        odyssey.Reader("No such ODB file")


@pytest.mark.parametrize("odyssey", odc_modules)
def test_frame_column_bitfields(odyssey):
    """
    Check if bitfield columns are properly described

    Please see ODB-523 for more information.
    """

    r = odyssey.Reader(data_file1)

    for frame in r.frames:
        for column_name in data_file1_bitfields:
            column = frame.column_dict[column_name]

            assert column.dtype == odyssey.DataType.BITFIELD
            assert len(column.bitfields) == len(data_file1_bitfields[column.name])

            for bf, bf_expected in zip(column.bitfields, data_file1_bitfields[column.name]):
                assert bf.name == bf_expected["name"]
                assert bf.size == bf_expected["size"]
                assert bf.offset == bf_expected["offset"]


@pytest.mark.parametrize("odyssey", odc_modules)
def test_frame_extract_bits(odyssey):
    """
    Check that we can extract specific bitfields explicitly
    """
    r = odyssey.Reader(data_file1, aggregated=True)
    assert len(r.frames) == 1
    df = r.frames[0].dataframe()

    for frame_col in r.frames[0].columns:

        if frame_col.dtype != odyssey.BITFIELD:
            continue

        col = df[frame_col.name]

        for bitfield in frame_col.bitfields:

            # Calculate this explicitly
            mask = (1 << bitfield.size) - 1
            bitvals = np.right_shift(col, bitfield.offset) & mask
            if bitfield.size == 1:
                bitvals = bitvals.astype(bool)

            # Now ask for this value in the columns
            full_bitfield_name = f"{frame_col.name.split('@')[0]}.{bitfield.name}@{frame_col.name.split('@')[1]}"
            df_direct = odyssey.read_odb(data_file1, columns=[full_bitfield_name], single=True)

            assert df_direct.shape[1] == 1
            assert all(df_direct[full_bitfield_name] == bitvals)
