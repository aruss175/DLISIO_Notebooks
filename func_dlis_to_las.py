# python 3.11.8
# DLISIO v1.0.1
# numpy v1.26.3
# pandas v2.2.0
# lasio v0.31

import os
import pandas as pd
import lasio
import dlisio
import numpy as np

def convert_dlis_to_las(filepath, output_folder_location, null=-999.25):
    filename = os.path.basename(filepath)
    filename = os.path.splitext(filename)[0]
    embedded_files = []
    origins = []

    with dlisio.dlis.load(filepath) as file:
        print(file.describe())
        for d in file:
            embedded_files.append(d)
            frame_count = 0
            for origin in d.origins:
                origins.append(origin)
            for fram in d.frames:
                frame_count = frame_count + 1

                channel_data = {
                    "curves_name": [],
                    "longs": [],
                    "unit": [],
                    "curves_L": [],
                    "curve_df": pd.DataFrame(),
                    "las_units": [],
                    "las_longs": [],
                }

                # -----------------------------------------------------------------------
                # Process channel/curve information
                # -----------------------------------------------------------------------
                for channel in fram.channels:
                    channel_data["curves_name"].append(channel.name)
                    channel_data["longs"].append(channel.long_name)
                    channel_data["unit"].append(channel.units)
                    curves = channel.curves()
                    channel_data["curves_L"].append(curves)

                las_units, las_longs, curve_df, object_warning = process_curve_info(
                    channel_data
                )

                curves_name = list(curve_df.columns.values)
                print(len(curves_name))

                # we will take the first curve in the frame as the index.
                curve_df = curve_df.set_index(curves_name[0])

                # -----------------------------------------------------------------------
                # Create las file
                # -----------------------------------------------------------------------
                las = create_las(
                    curve_df, curves_name, origin, las_units, las_longs, null, filepath
                )

                # -----------------------------------------------------------------------
                # Write las file
                # -----------------------------------------------------------------------
                write_las_file(las, filename, frame_count, output_folder_location)

            print("number of frames: " + str(frame_count) + ": this is the number of .las files created")
            print("embedded_files: " + str(len(embedded_files)))
            print("This file has " + str(len(origins)) + " metadata headers.  This code has used the first.")
            print(object_warning)


def process_curve_info(channel_data):
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

    for name_index, c in enumerate(channel_data["curves_L"]):
        name = channel_data["curves_name"][name_index]
        print("Processing " + name)
        units = channel_data["unit"][name_index]
        long = channel_data["longs"][name_index]
        c = np.vstack(c)
        try:
            num_col = c.shape[1]
            col_name = [name] * num_col
            df = pd.DataFrame(data=c, columns=col_name)
            channel_data["curve_df"] = pd.concat([channel_data["curve_df"], df], axis=1)
            object_warning = str(
                name) + ' had to be expanded in the final .las file, as it has multiple samples per index'
        except:
            num_col = 1
            df = pd.DataFrame(data=c, columns=[name])
            channel_data["curve_df"] = pd.concat([channel_data["curve_df"], df], axis=1)
            continue
        u = [units] * num_col
        l = [long] * num_col
        channel_data["las_units"].append(u)
        channel_data["las_longs"].append(l)
        print("Completed " + name)

    las_units = [item for sublist in channel_data["las_units"] for item in sublist]
    las_longs = [item for sublist in channel_data["las_longs"] for item in sublist]

    # Check that the lists are ready for the curve metadata
    print("If these are different lengths, something is wrong:")
    print(len(las_units))
    print(len(las_longs))

    curve_df = df_column_uniquify(channel_data["curve_df"])
    return las_units, las_longs, curve_df, object_warning


def create_las(curve_df, curves_name, origin, las_units, las_longs, null, filepath):
    las = lasio.LASFile()
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
    return las


def write_las_file(las, filename, frame_count, output_folder_location):
    outfile = filename + "_" + "converted_with_python_" + str(frame_count) + ".las"
    outpath = os.path.join(output_folder_location, outfile)

    if not os.path.exists(output_folder_location):
        print("Making output directory: [{}]\n".format(output_folder_location))
        os.makedirs(output_folder_location)

    print("Writing: [{}]\n".format(outpath))
    las.write(outpath, version=2)
