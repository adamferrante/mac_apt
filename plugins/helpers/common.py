'''
   Copyright (c) 2017 Yogesh Khatri 

   This file is part of mac_apt (macOS Artifact Parsing Tool).
   Usage or distribution of this software/code is subject to the 
   terms of the MIT License.
   
'''

from __future__ import unicode_literals

import os
import datetime
import pytz
import logging
from enum import IntEnum
from tzlocal import get_localzone

log = logging.getLogger('MAIN.HELPERS.COMMON')

class EntryType(IntEnum):
    FILES = 1
    FOLDERS = 2
    FILES_AND_FOLDERS = 3
    SYMLINKS = 4

class TimeZoneType(IntEnum):
    LOCAL = 1
    UTC = 2

class CommonFunctions:

    @staticmethod
    def GetLocalTimeFromUtcDate(d_utc):
        '''Returns a datetime object converted to local time'''
        local_timezone = get_localzone()
        #local_tz = get_localzone()
        return d_utc.replace(tzinfo=pytz.utc).astimezone(local_timezone)

    @staticmethod
    def ReadMacAbsoluteTime(mac_abs_time): # Mac Absolute time is time epoch beginning 2001/1/1
        '''Returns datetime object, or empty string upon error'''
        if mac_abs_time not in ( 0, None, ''):
            try:
                if type(mac_abs_time) in (str, unicode):
                    mac_abs_time = float(mac_abs_time)
                if mac_abs_time > 0xFFFFFFFF: # more than 32 bits, this should be nano-second resolution timestamp in HighSierra
                    return datetime.datetime.utcfromtimestamp(mac_abs_time / 1000000000 + 978307200)
                return datetime.datetime.utcfromtimestamp(mac_abs_time + 978307200)
            except Exception as ex:
                log.error("ReadMacAbsoluteTime() Failed to convert timestamp from value " + str(mac_abs_time) + " Error was: " + str(ex))
        return ''

    @staticmethod
    def ReadMacHFSTime(mac_hfs_time): # Mac HFS+ timestamp is time epoch beginning 1904/1/1
        '''Returns datetime object, or empty string upon error'''
        if mac_hfs_time not in ( 0, None, ''):
            try:
                if type(mac_hfs_time) in (str, unicode):
                    mac_hfs_time = float(mac_hfs_time)
                return datetime.datetime.utcfromtimestamp(mac_hfs_time - 2082844800)
            except Exception as ex:
                log.error("ReadMacHFSTime() Failed to convert timestamp from value " + str(mac_hfs_time) + " Error was: " + str(ex))
        return ''

    @staticmethod
    def ReadAPFSTime(mac_apfs_time): # Mac APFS timestamp is nano second time epoch beginning 1970/1/1
        '''Returns datetime object, or empty string upon error'''
        if mac_apfs_time not in ( 0, None, ''):
            try:
                if type(mac_apfs_time) in (str, unicode):
                    mac_apfs_time = float(mac_apfs_time)
                return datetime.datetime.utcfromtimestamp(mac_apfs_time / 1000000000.)
            except Exception as ex:
                log.error("ReadAPFSTime() Failed to convert timestamp from value " + str(mac_apfs_time) + " Error was: " + str(ex))
        return ''

    @staticmethod
    def ReadUnixTime(unix_time): # Unix timestamp is time epoch beginning 1970/1/1
        '''Returns datetime object, or empty string upon error'''
        if unix_time not in ( 0, None, ''):
            try:
                if type(unix_time) in (str, unicode):
                    unix_time = float(unix_time)
                return datetime.datetime.utcfromtimestamp(unix_time)
            except Exception as ex:
                log.error("ReadUnixTime() Failed to convert timestamp from value " + str(unix_time) + " Error was: " + str(ex))
        return ''

    @staticmethod
    def IntFromStr(string, base=10, error_val=0):
        integer = error_val
        try:
            integer = int(string, base)
        except: # Will go here if string is '' or contains non-digit characters
            if string == '' or string == None: pass
            else: log.exception('Could not convert string "{}" to int'.format(string))
        return integer

    @staticmethod
    def GetNextAvailableFileName(filepath):
        '''
        Checks for existing file and returns next available file name 
        by appending file name with a number. Ex: file01.jpg
        '''
        if os.path.exists(filepath):
            split = os.path.splitext(filepath)
            filepath_without_ext = split[0]
            ext = split[1]
            index = 1
            fullpath = filepath_without_ext + '{0:02d}'.format(index) + ext
            while (os.path.exists(fullpath)):
                index += 1
                fullpath = filepath_without_ext + '{0:02d}'.format(index) + ext
            filepath = fullpath
        return filepath

    @staticmethod
    def GetFileSize(file):
        '''Return size from an open file handle'''
        current_pos = file.tell()
        file.seek(0, 2) # Seek to end
        size = file.tell()
        file.seek(current_pos) # back to original position
        return size

    @staticmethod
    def TableExists(db_conn, table_name):
        '''Checks if a table with specified name exists in an sqlite db'''
        try:
            cursor = db_conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='%s'" % table_name)
            for row in cursor:
                return True
        except Exception as ex:
            log.error ("In TableExists({}). Failed to list tables of db. Error Details:{}".format(table_name, str(ex)) )
        return False
    
    @staticmethod
    def GetTableNames(self, db_conn):
        '''Retrieve all table names in an sqlite database'''
        try:
            cursor = db_conn.execute("SELECT group_concat(name) from sqlite_master WHERE type='table'")
            for row in cursor:
                return row[0]
        except Exception as ex:
            log.error ("Failed to list tables on db. Error Details: {}".format(str(ex)))
        return ''