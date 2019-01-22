"""
afp.py

Written by Eric Robinson

Simple API for accessing afp servers

"""

import os, sys, re, shutil

class AFP:
   """
   Creates a remote connection to an AFP server
   """

   __drivelist = ["Z:", "Y:", "X:", "W:", "V:", "U:", "T:", "S:", "R:"]

   __addedflag = 0

   __localpath = None
   __serverpath = None

   def __init__(self, serverpath, username=None, password=None):
      self.__localpath = self.__checkMounts(serverpath)
      if self.__localpath == None:
         self.__localpath = self.__connect(serverpath, username, password)
         if self.__localpath:
            self.__addedflag = 1
         else: 
            raise IOError, "Could not connect to smb server %s" % (serverpath)

   def __checkMounts(self, serverpath, username=None):
      """
      checkMounts(serverpath)
      This function does two things:
      1) Checks to see the if the given serverpath is mounted on our local system.
         If so, it returns the local path (on Windows, this is typically a drive letter)
         If not, returns None
      2) On Windows, this function will pare down our list of possible drive letters
         (drivelist) to exclude drives that are already in use.  This is a side effect.
      """

      if sys.platform == "win32":
         # On Windows, we use "net use" to get a list of network mounts
         cmd = "net use"
         netusecmd = os.popen(cmd, "r")
         matchpattern = re.compile("^OK\s*\t*([A-Z]:)\s*\t*([^\s\t]+)")
         for line in netusecmd:
            # Look for lines that start with "OK", and get the drive and server info
            if line[0:2] == "OK":
               matchresult = matchpattern.match(line)
               if matchresult:
                  driveletter = matchresult.group(1)
                  netpath = matchresult.group(2)
                  if netpath == serverpath:
                     netusecmd.close()
                     return driveletter
                  else:
                     if driveletter in self.__drivelist:
                        self.__drivelist.remove(driveletter)

         netusecmd.close()

      elif sys.platform == "darwin":
         # On Mac, we use "df" for now to figure out whether something is mounted
         # The server path on the mac will show up without the password, so we have
         # to strip it out and convert to all-caps
         if ":" in serverpath:
            (prefix, rest) = serverpath.split(":", 1)
            (passwd, rest) = rest.split("@", 1)
            serverpathnopasswd = "@".join((prefix, rest)).upper()
            cmd = "/bin/df"
            dfcmd = os.popen(cmd, "r")
            matchpattern = re.compile("^\/\/[^\s\t]+\s*\t*\d*\s*\t*\d*\s*\t*\d*\s*\t*\d*\%\s*\t*([^\s\t]+)")
            for line in dfcmd:
               # Look for lines that start with the serverpath
               if serverpathnopasswd in line:
                  matchresult = matchpattern.match(line)
                  if matchresult:
                     localpath = matchresult.group(1)
                     dfcmd.close()
                     return localpath
            dfcmd.close()

      return None


   def __connect(self, serverpath, username=None, password=None, localpath=None):
      """
      connect(serverpath, username=None, password=None, localpath=None)
      Adds a mount point for the server path on the local machine.
      If localpath is given, it is used as the local mount point.  Otherwise,
      a default localpath is used.  (On Windows, a new drive letter.  On Mac,
      a path under /Volumes).
      Returns the localpath of the mount.
      """

      if sys.platform == "win32":
         if localpath == None:
            localpath = self.__drivelist[0]
         cmd = "net use %s %s" % (localpath, serverpath)
         if password:
            cmd += " %s" % (password)
         if username:
            cmd += " /USER:%s" % (username)
         netusecmd = os.popen(cmd, "r")
         resultflag = 0
         for line in netusecmd:
            if "completed successfully" in line:
               resultflag = 1
               break
         netusecmd.close()
      elif sys.platform == "darwin":
         if localpath == None:
            # For Mac, we always need a local mount point, so we must
            # construct one if we don't have it.
            localpath = "/Volumes"
            localext = serverpath.lstrip("/")
            if "@" in localext:
               localext = localext.split("@", 1)[1]
            localpath = os.path.join(localpath, localext)
         # Once we have the localpath, we need to make sure it exists
         # as a directory we can place a mount point on.
         if not os.path.isdir(localpath):
            os.makedirs(localpath)
         if username:
            serverpath = serverpath.lstrip("/")
            if "\\" in username:
               username = username.split("\\")[1]
            if password:
               username += ":%s" % (password)
            serverpath = "afp://%s@%s"  % (username, serverpath)
         cmd = r"/sbin/mount_afp %s %s" % (serverpath, localpath)
         (input, mountcmd) = os.popen4(cmd, "r")
         input.close()
         resultflag = 1
         for line in mountcmd:
            if "fail" in line:
               resultflag = 0
         mountcmd.close()
      else:
         return None

      if resultflag:
         return localpath
      else:
         return None


   def __disconnect(self, localpath):
      """
      disconnect()
      Deletes a mount
      """

      if sys.platform == "win32":
         cmd = "net use %s /delete" % (localpath)
         netusecmd = os.popen(cmd, "r")
         resultflag = 0
         for line in netusecmd:
            if "deleted successfully" in line:
               resultflag = 1
               break
         netusecmd.close()
         if resultflag:
            return 1
         else:
            return 0

      elif sys.platform == "darwin":
         cmd = "umount %s" % (localpath)
         umountcmd = os.popen(cmd, "r")
         umountcmd.close()
         return 1

      return None

   def getLocalPath(self):
      if sys.platform == "win32":
         return self.__localpath + os.sep
      else:
         return self.__localpath

   def isAdded(self):
      return self.__addedflag

   def close(self, force=0):
      if self.__addedflag or force:
         self.__disconnect(self.__localpath)
         self.__addedflag = 0
         self.__localpath = None


if __name__ == "__main__":
   afpmount = AFP("//hermes.corp.adobe.com/builds", "ADOBENET\\esbuilder", "es45\\!44")
   print afpmount.getLocalPath()
   afpmount.close()
