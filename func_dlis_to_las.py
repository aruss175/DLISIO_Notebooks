#Work released under MIT License (MIT)
#Author: Ashley Russell

import os
import pandas as pd
import lasio
import dlisio

def convert_dlis_to_las(filepath, output_folder_location, null=-999.25):
    filename = os.path.basename(filepath)
    filename = os.path.splitext(filename)[0]
    embedded_files = []
    origins = []
    object_columns = []
    frame_count = 0
    object_warning = ''
    with dlisio.load(filepath) as file:
        for d in file:
            curves_L = []
            embedded_files.append(d)
            for origin in d.origin:
                origins.append(origin)
            for fram in d.frames:
                curves_name = []
                longs = []
                unit = []
                for channel in fram.channels:
                    curves_name.append(channel.name)
                    longs.append(channel.long_name)
                    unit.append(channel.units)
                frame_count = frame_count + 1
                las = lasio.LASFile()
                fingerprint = fram.fingerprint
                curves = d.curves(fingerprint)
                curves_L.append(curves)
                converted_curves = tuple(curves)
                curves_df = pd.DataFrame.from_records(converted_curves, columns=curves.dtype.names)
                position = 0
                places = []
                for column in curves_df:
                    position = position + 1
                    if curves_df[column].dtype.name == 'object':
                        place = position - 1
                        places.append(place)
                        object_columns.append(str(column))
                        object_warning = str(
                            object_columns) + ' had to be expanded in the final .las file, as it has multiple samples per index'
                        curves_df = curves_df.assign(
                            **pd.DataFrame(curves_df[column].values.tolist()).add_prefix(column))
                        new_columns = list(pd.DataFrame(curves_df[column].values.tolist()).add_prefix(column))
                        curves_df = curves_df.drop(columns=[column])
                        curves_name = curves_name + new_columns
                        longs += len(new_columns) * [longs[place]]
                        unit += len(new_columns) * [unit[place]]
                for index in sorted(places, reverse=True):
                    del curves_name[index]
                    del longs[index]
                    del unit[index]
                # Check that the lists are ready for the curve metadata
                print("If these are different lengths, something is wrong:")
                print(len(unit))
                print(len(curves_name))
                print(len(longs))
                # the index is always the first curve in the frame.
                curves_df = curves_df.set_index(curves_name[0])
                # write the pandas data to the las file
                las.set_data(curves_df)
                # write the curve metadata from our three lists.
                counter = 0
                for x in curves_name:
                    las.curves[x].unit = unit[counter]
                    las.curves[x].descr = longs[counter]
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
                las.write(output_folder_location + "\\" + filename + "_" + 'converted_with_python_' + str(frame_count) + '.las', version=2)
            print("number of frames: " + str(frame_count) + ": this is the number of .las files created")
            print("embedded_files: " + str(len(embedded_files)))
            print("This file has " + str(len(origins)) + " metadata headers.  This code has used the first.")
            print(object_warning)
