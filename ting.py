#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib
import os
import re
import sys
import hashlib
import getpass

#set global parameters
user =  getpass.getuser()
if os.path.isdir("/media/"+user+"/Ting/$ting") == True:
    MountedTingPath = ("/media/" + user + "/Ting/$ting")
    print("Ting mounted at " + MountedTingPath + ".")
elif os.path.isdir("/media/"+user+"/TING/$ting") == True:
    MountedTingPath = "/media/" + user + "/TING/$ting"
    print("Ting mounted at " + MountedTingPath + ".")
elif os.path.isdir("/media/TING/$ting") == True:
    MountedTingPath = "/media/" + user + "/TING/$ting"
    print("Ting mounted at " + MountedTingPath + ".")
elif os.path.isdir("/media/Ting/$ting") == True:
    MountedTingPath = "/media/" + user + "/TING/$ting"
    print("Ting mounted at " + MountedTingPath + ".")
else: 
    print("Ting not mounted or mounted with another user") 
    sys.exit("Bye.")

if os.path.isfile("/media/"+user+"/Ting/$ting/TBD.TXT") == True:
    tbd = ("TBD.TXT")
elif os.path.isfile("/media/"+user+"/Ting/$ting/tbd.txt") == True:
    tbd = ("tbd.txt")
else: 
    sys.exit("Cannot find the tbd.txt!")

TingURL = "system.ting.eu/book-files"
TingFileTypes = ["Thumb", "File", "Script"]

TingFileDestDict = {}
TingFileDestDict["Thumb"] = MountedTingPath + "/{}_en.png"
TingFileDestDict["File"] = MountedTingPath + "/{}_en.ouf"
TingFileDestDict["Script"] = MountedTingPath + "/{}_en.src"

TingFileSourceDict = {}
TingFileSourceDict["Thumb"] = "http://"+TingURL+"/get/id/{}/area/en/type/thumb"
TingFileSourceDict["File"] = "http://"+TingURL+"/get/id/{}/area/en/type/archive"
TingFileSourceDict["Script"] = "http://"+TingURL+"/get/id/{}/area/en/type/script"

def GetBookIDs(TBDFilePath=MountedTingPath+"/"+tbd):
    TBDFile = open(TBDFilePath, "r")
    BookIDs = TBDFile.readlines()
    for i, BookID in enumerate(BookIDs):
        BookIDs[i] = BookID.strip()
    return BookIDs
    
def CheckForBookDesciptionFile(BookIDAsString, TingPath=MountedTingPath):
    BookExists = os.path.exists(TingPath+"/"+BookIDAsString+"_en.txt")
    return BookExists
    
def GetBookMD5Sums(BookID, TingPath=MountedTingPath):
    ResultDict = dict.fromkeys(TingFileTypes)
    
    aFile = open(TingPath+"/"+BookID+"_en.txt")
    Lines = aFile.readlines()
    aFile.close()

    for key in ResultDict.iterkeys():
        for Line in Lines:
            Match = re.findall(key+"MD5: ([0-9,a-f]+)", Line)
            if Match:
                ResultDict[key] = Match[0]
                break
    return ResultDict
    
def CheckForBookFileValid(BookID, FileType, MD5SUM, FileDestDict=TingFileDestDict):
    LocalFilePath = FileDestDict[FileType].format(BookID)
    
    isValid = True
    isValid = isValid and os.path.exists(LocalFilePath)
    
    if isValid:
        md5 = hashlib.md5()
        File = open(LocalFilePath, "r")
        md5.update(File.read())
        isValid = isValid and (MD5SUM == md5.hexdigest())
    print "Book: ", BookID, FileType, MD5SUM, isValid
    return isValid

def GetBookFile(BookID, FileType, FileSourceDict=TingFileSourceDict, FileDestDict=TingFileDestDict):
    LocalFilePath = FileDestDict[FileType].format(BookID)
    FullURL = FileSourceDict[FileType].format(BookID)
    print "Start Download from", FullURL
    urllib.urlretrieve(FullURL, LocalFilePath)
    return
        
    
def GetBookDesciptionFile(BookIDAsString, URL=TingURL, TingPath=MountedTingPath):
    FullURL = "http://"
    FullURL += URL
    FullURL += "/get-description/id/"
    FullURL += BookIDAsString
    FullURL += "/area/en"
    
    LocalFile = TingPath
    LocalFile += "/"
    LocalFile += BookIDAsString
    LocalFile += "_en.txt"

    urllib.urlretrieve(FullURL, LocalFile)
    return

def main(argv):

 BookIDs = GetBookIDs()
 print "Found followings BookIDs for processing:"
 print BookIDs

 for BookID in BookIDs:
    if not(CheckForBookDesciptionFile(BookID)):
        GetBookDesciptionFile(BookID)
    MD5Sums = GetBookMD5Sums(BookID)
    
    for key, value in MD5Sums.iteritems():
        if value != None:
            if not(CheckForBookFileValid(BookID, key, value)):
                GetBookFile(BookID, key)
                if not(CheckForBookFileValid(BookID, key, value)):
                    print "Error: download failed for Book", BookID, key

 print("removing " + MountedTingPath+"/"+tbd + "..") 
 os.remove(MountedTingPath+"/"+tbd)
 print "Job done!"


   

if __name__ == "__main__":
   main(sys.argv[1:])
 
    
