"""
   codexlocation.py

   Written by: Eric Robinson

   Defines a class, "CodexLocation", that will handle ftp, smb, or afp
   locations returned from Codex.  There is a base class that defines the
   standard methods, and then sub classes for each type of download.

   Usage:

      obj = CodexLocation(uri [, username, password]) - Create a connection to
         a remote server where uri is a location uri returned from Codex.
         "username" and "password" are the values to use for
         connecting to the server.  These will default to
         "esbuilder" and its password.

      obj.listdir() -  Returns a list of the files in the remote folder.
      obj.curdir() - Returns the path of the current remote folder
      obj.download(remotepath, localpath) - Downloads the "remotepath" file to
         the "localpath" location.  Both values are relative to their respective
         servers, so "remotepath" is relative to the remote server's current directory.
         This command will handle files or directories, but if you specify a file,
         you must specify the filename in the localpath.
      obj.close() - Close the connection to the remote server.
"""

import os, sys, os.path, ftplib, shutil
import smb, ftp, afp


class BadProtocolError(Exception): pass
class BadPathError(Exception): pass
class ReadOnlyError(Exception): pass
class ModeNotSupported(Exception): pass

def CodexLocation(uri, mode="r", username="suitbldr", password="-Qic5ad5"):
   """
      Call this function to return a class object of the correct protocol
   """
   if uri.startswith("ftp"):
      return CodexLocationFTP(uri, mode, username, password)
   elif uri.startswith("smb") and mode == "r":
      return CodexLocationSMB(uri, mode, username, password)
   elif uri.startswith("smb") and mode == "w":
      return CodexLocationSMB(uri, mode, username, password)
   elif uri.startswith("afp"):
      return CodexLocationFTP(uri, mode, username, password)
   else:
      raise BadProtocolError, "Protocol not recognized"


class CodexLocationBase(object):
   """
      Base class.  The protocol specific classes are sub-classed from here.
   """

   def __init__(self, uri, mode, username, password):
      self._parseURI(uri)
      self.username = username
      self.password = password
      self.mode = mode
      self.srvobj = self._connect()

   def listdir(self):
      pass

   def download(self, filename, targetpath):
      pass

   def chdir(self, newpath):
      pass

   def curdir(self):
      pass

   def _parseURI(self, uri):
      """
         Parse the given URI into its component parts and return them
      """

      # The URI starts with the scheme, which is followed by a colon.  We
      # search for the colon and consider the scheme everything ahead of it.
      colonidx = uri.find(":")
      self.scheme = uri[:colonidx]

      # Then cut the scheme and colon off the string so we don't deal with it.
      rest = uri[colonidx+1:].lstrip("/\\")

      # The next part is the server.  First, strip off any slashes at the front,
      # then take everything up to the next slash as the server.
      slashidx = rest.find("/")
      self.server = rest[:slashidx]

      # Once again, strip off the stuff we've dealt with.
      rest = rest[slashidx+1:]

      # URI's coming from sub-installers should not have query values, so the
      # rest of the URI string should just be the path.  Just to be safe, we'll
      # search for possible query stuff, like "?", or "@"

      qidx = rest.find("?")
      atidx = rest.find("@")
      if qidx > -1:
         self.path = rest[:qidx]
         self.query = rest[qidx+1:]
      elif atidx > -1:
         self.path = rest[:atidx]
         self.query = rest[atidx+1:]
      else:
         self.path = rest.rstrip("/\\")
         self.query = ""

   def _connect(self):
      pass

   def close(self):
      try:
         self.srvobj.close()
      except:
         pass



class CodexLocationFTP(CodexLocationBase):
   """
      FTP sub-class for remote downloading
   """
   def __init__(self, uri, mode, username, password):
      super(CodexLocationFTP, self).__init__(uri, mode, username, password)


   def _connect(self):
      """
         Create a connection to the ftp server and cd to the path we want.
      """
      ftpobj = ftplib.FTP(self.server, "ADOBENET\\%s" % (self.username), self.password)
      try:
         if self.mode == "r":
            ftpobj.cwd(self.path)
         else:
            path = self.path
            if not path.startswith("/"):
               path = "/" + path
            ftp.goToDir(ftpobj, path)
         self.rootpath = ftpobj.pwd()
      except:
         raise BadPathError
      return ftpobj

   def listdir(self):
      return self.srvobj.nlst()


   def chdir(self, path=None):
      """
         Change directory on an FTP server
      """
      if path:
         try:
            self.srvobj.cwd(path)
         except:
            raise BadPathError, "Path %s does not exist"
      else:
         self.srvobj.cwd(self.rootpath)


   def curdir(self):
      """
         Return the current path on the remote server
      """
      return self.srvobj.pwd()


   def download(self, remotepath, localpath):
      """
         Download a file or folder from an FTP server
      """
      ftp.download(self.srvobj, localpath, remotepath)


   def upload(self, localpath, remotepath):
      """
         Upload a file or folder to an FTP server
      """
      if "w" not in self.mode:
         raise ReadOnlyError, "Cannot upload when mode is not \"w\""
      if os.path.isdir(localpath):
         # local path is a folder
         origpath = self.srvobj.pwd()
         ftp.postFolder(self.srvobj, localpath, remotepath)
         self.srvobj.cwd(origpath)
      elif os.path.exists(localpath):
         # local path is a file
         ftp.postFile(self.srvobj, remotepath, localpath)
      else:
         # localpath doesn't exist
         raise BadPathError, "Path %s doesn't exist" % (localpath)


class CodexLocationSMB(CodexLocationBase):
   """
      SMB sub-class for remote downloading
   """
   def __init__(self, uri, mode, username, password):
      super(CodexLocationSMB, self).__init__(uri, mode, username, password)


   def _connect(self):
      """
         Create a connection to the smb server
      """
      (volname, path) = self.path.split("/", 1)
      serverpath = "%s%s%s%s%s" % (os.sep, os.sep, self.server, os.sep, volname)
      if sys.platform == "win32":
         serverpath = serverpath.replace("/", "\\")
      else:
         serverpath = serverpath.replace("\\", "/")
      username = "ADOBENET\\%s" % (self.username)
      passwd = self.password

      try:
         smbmount = smb.SMB(serverpath, username, passwd)
      except:
         raise BadPathError
      self.smbpath = os.path.join(smbmount.getLocalPath(), path)

      if "r" in self.mode:
         if not os.path.exists(self.smbpath):
            smbmount.close()
            raise BadPathError, "Folder %s does not exist" % (path)

      if "w" in self.mode:
         if not os.path.exists(self.smbpath):
            try:
               os.makedirs(self.smbpath)
            except:
               raise BadPathError, "Cannot create folder %s on %s/%s" % (path, self.server, volname)

      self.rootpath = self.smbpath
      return smbmount


   def listdir(self):
      return os.listdir(self.smbpath)


   def chdir(self, path=None):
      """
         Change directory to a new location
      """
      if path:
         newpath = os.path.join(self.smbpath, path)
         if os.path.isdir(newpath):
            self.smbpath = newpath
         elif "w" in mode:
            try:
               os.makedirs(os.path.realpath(newpath))
               self.smbpath = newpath
            except:
               raise BadPathError, "Cannot create directory %s on %s" % (newpath, self.server)
         else:
            raise BadPathError, "Path %s does not exist" % (newpath)
      else:
         self.smbpath = self.rootpath


   def curdir(self):
      """
         Return the current directory on the remote server
      """
      return self.smbpath


   def download(self, remotepath, localpath):
      """
         Download a file or folder from an SMB server
      """
      remotepath = os.path.join(self.smbpath, remotepath)
      if os.path.isdir(remotepath):
         # The remote path is a folder.  Act accordingly.
         if os.path.exists(localpath):
            shutil.rmtree(localpath)
         copydir(remotepath, localpath)
      else:
         if os.path.exists(localpath):
            os.remove(localpath)
         shutil.copy(remotepath, localpath)


   def upload(self, localpath, remotepath):
      """
         Upload a file or folder to an SMB server
      """
      if "w" not in self.mode:
         raise ReadOnlyError, "Cannot upload when mode is not \"w\""
      remotepath = os.path.join(self.smbpath, remotepath)
      remoteparent = os.path.dirname(remotepath)
      if not os.path.exists(remoteparent):
         try:
            os.makedirs(remoteparent)
         except:
            raise BadPathError, "Could not create folder %s" % (remoteparent)
      if os.path.isdir(localpath):
         # The local path is a folder.  Act accordingly.
         if os.path.exists(remotepath):
            shutil.rmtree(remotepath)
         copydir(localpath, remotepath)
      else:
         if os.path.exists(remotepath):
            os.remove(remotepath)
         shutil.copy(localpath, remotepath)


class CodexLocationAFP(CodexLocationBase):
   """
      AFP sub-class for remote downloading.
   """
   def __init__(self, uri, mode, username, password):
      super(CodexLocationAFP, self).__init__(uri, mode, username, password)


   def _connect(self):
      """
         Create a connection to the afp server
      """
      (volname, path) = self.path.split("/", 1)
      serverpath = "%s%s%s%s%s" % (os.sep, os.sep, self.server, os.sep, volname)
      if sys.platform == "win32":
         serverpath = serverpath.replace("/", "\\")
      else:
         serverpath = serverpath.replace("\\", "/")
      username = "%s" % (self.username)
      passwd = self.password

      try:
         afpmount = afp.AFP(serverpath, username, passwd)
      except:
         raise BadPathError
      self.afppath = os.path.join(afpmount.getLocalPath(), path)

      if "w" in self.mode:
         if not os.path.exists(self.afppath):
            try:
               os.makedirs(self.afppath)
            except:
               raise BadPathError, "Cannot create folder %s on %s/%s" % (path, self.server, volname)

      self.rootpath = self.afppath
      return afpmount


   def listdir(self):
      return os.listdir(self.afppath)


   def chdir(self, path=None):
      """
         Change directory to a new location
      """
      if path:
         newpath = os.path.join(self.afppath, path)
         if os.path.isdir(newpath):
            self.afppath = newpath
         elif "w" in mode:
            try:
               os.makedirs(os.path.realpath(newpath))
               self.afppath = newpath
            except:
               raise BadPathError, "Cannot create directory %s on %s" % (newpath, self.server)
         else:
            raise BadPathError, "Path %s does not exist" % (newpath)
      else:
         self.afppath = self.rootpath


   def curdir(self):
      """
         Return the current directory on the remote server
      """
      return self.afppath


   def download(self, remotepath, localpath):
      """
         Download a file or folder from an afp server
      """
      remotepath = os.path.join(self.afppath, remotepath)
      if os.path.isdir(remotepath):
         # The remote path is a folder.  Act accordingly.
         if os.path.exists(localpath):
            shutil.rmtree(localpath)
         copydir(remotepath, localpath)
      else:
         if os.path.exists(localpath):
            os.remove(localpath)
         shutil.copy(remotepath, localpath)


   def upload(self, localpath, remotepath):
      """
         Upload a file or folder to an afp server
      """
      if "w" not in self.mode:
         raise ReadOnlyError, "Cannot upload when mode is not \"w\""
      remotepath = os.path.join(self.afppath, remotepath)
      remoteparent = os.path.dirname(remotepath)
      if not os.path.exists(remoteparent):
         try:
            os.makedirs(remoteparent)
         except:
            raise BadPathError, "Could not create folder %s" % (remoteparent)
      if os.path.isdir(localpath):
         # The local path is a folder.  Act accordingly.
         if os.path.exists(remotepath):
            shutil.rmtree(remotepath)
         copydir(localpath, remotepath)
      else:
         if os.path.exists(remotepath):
            os.remove(remotepath)
         shutil.copy(localpath, remotepath)



def copydir(src, dst):
   """
      Used for copying directories.
   """
   if sys.platform == "win32":
      shutil.copytree(src, dst)
   else:
      cmd = "ditto \"%s\" \"%s\""  % (src, dst)
      os.system(cmd)

if __name__ == "__main__":

   uri = "ftp://hermes.corp.adobe.com/builds/SuiteConfiguration/1.0/Win/mul/test"
   obj = CodexLocation(uri, "w")
   try:
      print obj.scheme, obj.server, obj.path, obj.query
      print obj.listdir()
      print obj.curdir()
      obj.upload("SOAPpy", ".")
      print obj.curdir()
   finally:
      obj.close()