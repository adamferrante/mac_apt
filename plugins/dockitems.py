'''
   Copyright (c) 2017 Yogesh Khatri

   This file is part of mac_apt (macOS Artifact Parsing Tool).
   Usage or distribution of this software/code is subject to the
   terms of the MIT License.

   dockitems.py
   ---------------
   xxx

'''
from __future__ import print_function
from __future__ import unicode_literals # Must disable for sqlite.row_factory

import os
from helpers.macinfo import *
from helpers.writer import *
import logging
from biplist import *
import binascii
import zlib
import struct
from helpers.macinfo import *
from helpers.writer import *


__Plugin_Name = "DOCKITEMS"
__Plugin_Friendly_Name = "Dock Items"
__Plugin_Version = "1.0"
__Plugin_Description = "Parses Users Dock PList"
__Plugin_Author = "Adam Ferrante"
__Plugin_Author_Email = "adam@ferrante.io"

__Plugin_Standalone = False
__Plugin_Standalone_Usage = ''

log = logging.getLogger('MAIN.' + __Plugin_Name) # Do not rename or remove this ! This is the logger object

#---- Do not change the variable names in above section ----#

class DockItem:
    def __init__(self, file_label, parent_mod_date, file_mod_date, file_type, guid, user, source_path): # item, user, source_path):
        self.file_label = file_label
        if parent_mod_date > 0xFFFFFFFF: # On High Sierra, sometimes seen..
            parent_mod_date = parent_mod_date & 0xFFFFFFFF # Killing upper 32 bits, not 100% sure about this!

        self.parent_mod_date = CommonFunctions.ReadMacHFSTime(parent_mod_date)
        self.file_mod_date = CommonFunctions.ReadMacHFSTime(file_mod_date)
        self.file_type = file_type
        self.guid = guid
        self.user = user
        self.path = source_path

def PrintAll(docks, output_params):
    dock_info = [   ('File Label',DataType.TEXT),('Parent Modified',DataType.TEXT),
                    ('File Modified',DataType.DATE),('File Type', DataType.TEXT),('GUID',DataType.TEXT),
                    ('User',DataType.TEXT),('Source',DataType.TEXT)
                ]

    log.info (str(len(docks)) + " user docks found(s) found")

    dock_list_final = []
    for dock_items in docks:
        for item in dock_items:
            single_dock_item = [item.file_label, item.parent_mod_date,
                                item.file_mod_date, item.file_type, item.guid,
                                item.user, item.path
                                ]
            dock_list_final.append(single_dock_item)

    WriteList("Dock Information", "Dock Items", dock_list_final, dock_info, output_params, '')

def ReadDockItemsPlist(mac_info, user, plist_path):
    success, plist, error = mac_info.ReadPlist(plist_path)

    if success:
        processed_list = []
        for key in ['persistent-others', 'persistent-apps']:
            if plist.get(key, None) != None:
                try:
                    for item in plist[key]:
                        tile_data = item.get('tile-data', None)
                        if tile_data:
                            instance = DockItem(tile_data.get('file-label', ''),
                                                tile_data.get('parent-mod-date', None),
                                                tile_data.get('file-mod-date', None),
                                                tile_data.get('file-type', ''),
                                                item.get('GUID', ''),
                                                user.user_name, plist_path)
                            processed_list.append(instance)
                        else:
                            log.warning('No tile-data found!! Perhaps a newer format?')
                except:
                    log.exception("Exception while processing {}".format(key))
            else:
                log.debug('Key {} not found!'.format(key))
    else:
        log.error(error)

    return processed_list


def Plugin_Start(mac_info):
    '''Main Entry point function for plugin'''
    dock_items_path = '{}/Library/Preferences/com.apple.dock.plist' # PList within each users directory.

    docks = []
    for user in mac_info.users:
        if user.home_dir == '/private/var/empty': continue # Optimization, nothing should be here!
        source_path = dock_items_path.format(user.home_dir) # Set a variable to the path of all user dock plist files.

        if mac_info.IsValidFilePath(source_path): # Determine if the above path is valid.
            mac_info.ExportFile(source_path, __Plugin_Name)
            docks.append(ReadDockItemsPlist(mac_info, user, source_path)) #Add each user's dock items to a list.

    PrintAll(docks, mac_info.output_params)


def Plugin_Start_Standalone(input_files_list, output_params):
    pass # I'll be taking care of this though.
    '''log.info("Module Started as standalone")
    for input_path in input_files_list:
        log.debug("Input file passed was: " + input_path)
        notes = []
        db = OpenDb(input_path)
        if db != None:
            filename = os.path.basename(input_path)
            if filename.find('V2') > 0:
                ReadNotesV2_V4_V6(db, notes, 'V2', input_path, '')
            elif filename.find('V4') > 0:
                ReadNotesV2_V4_V6(db, notes, 'V4', input_path, '')
            elif filename.find('V6') > 0:
                ReadNotesV2_V4_V6(db, notes, 'V6', input_path, '')
            elif filename.find('NoteStore') >= 0:
                ReadNotes(db, notes, input_path, '')
            else:
                log.info('Unknown database type, not a recognized file name')
            db.close()
        if len(notes) > 0:
            PrintAll(notes, output_params)
        else:
            log.info('No notes found in {}'.format(input_path))'''

if __name__ == '__main__':
    print ("This plugin is a part of a framework and does not run independently on its own!")