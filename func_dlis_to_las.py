# python 3.6.8
# DLISIO v0.1.15
# numpy v1.16.2
# pandas v0.24.1
# lasio v0.23

import os
import pandas as pd
import lasio
import dlisio
dlisio.set_encodings(['latin1'])
import numpy as np

def convert_dlis_to_las(filepath, output_folder_location, null=-999.25):
    filename = os.path.basename(filepath)
    filename = os.path.splitext(filename)[0]
    embedded_files = []
    origins = []
    frame_count = 0

    def df_column_uniquify(df):
        df_columns = df.columns
        new_columns = []
        for item in df_columns:
            counter = 0
            newitem = item
            while newitem in new_columns:
                counter += 1
                newitem = "{}_{}".format(item, counter)
            new_columns.append(newitem)
        df.columns = new_columns
        return df

    with dlisio.load(filepath) as file:
        print(file.describe())
        for d in file:
            embedded_files.append(d)
            frame_count = 0
            for origin in d.origins:
                origins.append(origin)
            for fram in d.frames:
                curves_name = []
                longs = []
                unit = []
                curves_L = []
                frame_count = frame_count + 1
                for channel in fram.channels:
                    curves_name.append(channel.name)
                    longs.append(channel.long_name)
                    unit.append(channel.units)
                    curves = channel.curves()
                    curves_L.append(curves)
                name_index = 0
                las = lasio.LASFile()
                curve_df = pd.DataFrame()
                las_units = []
                las_longs = []
                for c in curves_L:
                    name = curves_name[name_index]
                    print("Processing " + name)
                    units = unit[name_index]
                    long = longs[name_index]
                    c = np.vstack(c)
                    try:
                        num_col = c.shape[1]
                        col_name = [name] * num_col
                        df = pd.DataFrame(data=c, columns=col_name)
                        curve_df = pd.concat([curve_df, df], axis=1)
                        name_index = name_index + 1
                        object_warning = str(
                            name) + ' had to be expanded in the final .las file, as it has multiple samples per index'
                    except:
                        num_col = 1
                        df = pd.DataFrame(data=c, columns=[name])
                        name_index = name_index + 1
                        curve_df = pd.concat([curve_df, df], axis=1)
                        continue
                    u = [units] * num_col
                    l = [long] * num_col
                    las_units.append(u)
                    las_longs.append(l)
                    print("Completed " + name)
                las_units = [item for sublist in las_units for item in sublist]
                las_longs = [item for sublist in las_longs for item in sublist]

                # Check that the lists are ready for the curve metadata
                print("If these are different lengths, something is wrong:")
                print(len(las_units))
                print(len(las_longs))
                curve_df = df_column_uniquify(curve_df)
                curves_name = list(curve_df.columns.values)
                reordered_curves_name = move_valid_index_to_first_col(curves_name)
                curve_df = curve_df.reindex(reordered_curves_name, axis=1)

                print(len(curves_name))

                # we will take the first curve in the frame as the index.
                curve_df = curve_df.set_index(reordered_curves_name[0])
                # write the pandas data to the las file
                las.set_data(curve_df)
                # write the curve metadata from our three lists.
                counter = 0
                for x in curves_name:
                    las.curves[x].unit = las_units[counter]
                    las.curves[x].descr = las_longs[counter]
                    counter = counter + 1
                las.well.COMP = origin.company
                las.well.WELL = origin.well_name
                las.well.FLD = origin.field_name
                las.well.SRVC = origin.producer_name
                las.well.DATE = origin.creation_time
                las.well.UWI = origin.well_id
                las.well.API = origin.well_id
                las.well.NULL = null
                las.params['PROD'] = lasio.HeaderItem('PROD', value=origin.product)
                las.params['PROG'] = lasio.HeaderItem('PROG', value=origin.programs)
                las.params['RUN'] = lasio.HeaderItem('RUN', value=origin.run_nr)
                las.params['DESCENT'] = lasio.HeaderItem('DESCENT', value=origin.descent_nr)
                las.params['VERSION'] = lasio.HeaderItem('VERSION', value=origin.version)
                las.params['LINEAGE'] = lasio.HeaderItem('LINEAGE', value="Python-converted from DLIS")
                las.params['ORFILE'] = lasio.HeaderItem('ORFILE', value=filepath)

                # -----------------------------------------------------------------------
                # Write file
                # -----------------------------------------------------------------------
                outfile = filename + "_" + "converted_with_python_" + str(frame_count) + ".las"
                outpath = os.path.join(output_folder_location, outfile)

                if not os.path.exists(output_folder_location):
                    print("Making output directory: [{}]\n".format(output_folder_location))
                    os.makedirs(output_folder_location)

                print("Writing: [{}]\n".format(outpath))
                las.write(outpath, version=2)


            print("number of frames: " + str(frame_count) + ": this is the number of .las files created")
            print("embedded_files: " + str(len(embedded_files)))
            print("This file has " + str(len(origins)) + " metadata headers.  This code has used the first.")
            print(object_warning)


def move_valid_index_to_first_col(curves_name):
    idx_col = 0
    for curve in ['DEPT', 'DEPTH', 'TIME', 'INDEX']:
        if curve in curves_name:
            idx_col = curves_name.index(curve)
            break

    reordered_curves_name = curves_name[idx_col:idx_col+1]
    reordered_curves_name.extend(curves_name[:idx_col])
    reordered_curves_name.extend(curves_name[idx_col+1:])

    return reordered_curves_name

