'''
Several merging functions needed for combining dataframes.
'''
import pandas as pd
from models.imported_sheet import ImportedSheet

def combine_data(_alignment_columns, _aligned_row, _dfs: list[pd.DataFrame]):
    '''
    Test
    '''

def find_duplicates(alignment_columns: list[str], alignment_row_data, sheets: list[ImportedSheet]) -> dict[str, pd.DataFrame]:
    '''
    Given alignment columns to reference and a set of dataframes which contains one of the alignment columns
    and atleast one dataframe that has the alignment row data provided within its alignment_column, this will check
    to see if any other dataframes containing that alignment row data in their alignment column has duplicate columns with varing data
    and if so, return a dataframe with those conflict rows.

    Returns
    -------
    Maping of duplicate column name -> dataframe containing columns for the filename, and associated value
    '''
    # (filename, cut dataset)
    matches = []

    for sheet in sheets:
        data = sheet.get_df()
        for col in alignment_columns:
            if col in data.columns:
                if data[col].tolist().count(alignment_row_data) == 1:
                    matches.append((sheet.file_name ,data.loc[data[col] == alignment_row_data,:]))
                    #match found for given sheet, no need to check other alignment_columns.
                    break

    # Key = the column name, value = dataframe with file names as columns and value being different value ?
    common_columns = {}

    while len(matches) > 1:
        duplicates = set.intersection(*[set(match[1].columns) for match in matches])
        # Drop df references with no more duplicates
        for match in list(matches):
            local_duplicates = set.intersection(duplicates, set(match[1].columns))
            if len(local_duplicates) == 0:
                matches.remove(match)

        for duplicate in duplicates:
            # filename: value
            values = {}
            for match in matches:
                filename = match[0]
                data = match[1]
                values[filename] = data[duplicate].tolist()[0]

            duplicate_data = pd.DataFrame(values)
            common_columns[duplicate] = duplicate_data

    return common_columns


def combine_columns(columns: list[pd.Series], drop_missing: bool) -> pd.Series:
    '''
    Combine several column series into 1. If drop_missing is flagged then only the values
    present in each column will be kept in output.
    '''
    sets = [set(col) for col in columns]
    if drop_missing:
        common_rows = set.intersection(*sets)
        return pd.Series(list(common_rows))

    all_unique_rows = set.union(*sets)
    return pd.Series(list(all_unique_rows))
