"""
createsifvinfo.py

Written by: Eric Robinson

Create a versioninfo.xml file in this directory for the SIF of a given product/version.

This script is meant to be an easy way to create a versioninfo.xml for SIF files posted to Codex.
The script will take the product, version, and build number to use, and create an xml
file using predefined values in all other cases (such as subproduct).

Usage:

   python createsifvinfo.py <product> <version> <build>

"""

import os, sys, time
import versioninfo


def CreateSIFVInfo(product, version, build):
   """
      Create the versioninfo.xml
   """

   timestamp = time.strftime("%Y/%m/%d:%H:%M:%S")

   vinfoobj = versioninfo.VersionInfo()
   vinfoobj.addBuild(product, version, "SIF", build, timestamp, "None", "None", "Folder", "independent", "mul")

   vinfofobj = open("versioninfo.xml", "w")
   vinfofobj.write(vinfoobj.toXML())
   vinfofobj.close()


if __name__ == "__main__":

   if len(sys.argv) < 4:
      print __doc__
      sys.exit()

   product = sys.argv[1]
   version = sys.argv[2]
   build = sys.argv[3]

   if os.path.exists("versioninfo.xml"):
      print "Removing old %s file." % ("versioninfo.xml")
      os.remove("versioninfo.xml")

   CreateSIFVInfo(product, version, build)