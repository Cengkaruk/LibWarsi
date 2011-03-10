#!/usr/bin/env python
#-*- coding:utf-8 -*-
"""Warung Aplikasi module.

Exported class :

OnPackage -- Class for manipulating and install .on package (BlankOn Package) with Text and GTK+3 interfaces
BuildOnPackage -- Class for creating BlankOn Package

"""

import os
import tarfile
import string
import apt
from hashlib import md5
import gettext
import tempfile
import apt_pkg
import shutil
import warsiexceptions
import apt.progress.gtk2

version = "0.1"
gettext.textdomain('libwarsi')
_ = gettext.gettext
ex = warsiexceptions

class OnPackage(object):
    """
    Class for manipulating and install .on package (BlankOn Package) with Text and GTK+3 interfaces
    """    

    def __init__(self):
        self.cache = apt.Cache(apt.progress.text.OpProgress())
        apt_pkg.init()

    def extract(self, pkg):
        """Extract BlankOn Package

        Extract archive package and return extracted folder
        
        Arguments:
        pkg - A string, name of package

        Returns:
        extractdata - A string, extracted package on temp directory
 
        """
        dir = os.path.splitext(pkg)[0]
        tmp = tempfile.gettempdir()
        extractdata = os.path.join(tmp, dir)

        #TODO : Default akan menggunakan LZMA, pilihan lain bz2 dan gz

        try:
            tar = tarfile.open(pkg, "r:bz2")
            info = tar.extractall(tmp)
        except IOError:
            raise ex.WarsiIOError("IO Error")
        except tarfile.ExtractError:
            raise ex.WarsiExtractError("Extracting %s failed" %pkg)

        tar.close()
        return extractdata

    def is_valid(self, pkg):
        """Validating BlankOn Package

        Return True or False

        Arguments:
        pkg - A String, name on package

        Returns:
        TRUE or FALSE

        """
        ext = os.path.splitext(pkg)[1]
        return ext == '.on'
        #TODO : any ideas?

    def show_info(self, pkg):
        """Show Information about Package

        Return package information dict.     

        Arguments:
        pkg - A String, name of package

        Returns:
        info - A Dict.

        """
        dir = os.path.splitext(pkg)[0]
        blankinfo = os.path.join(dir, "blank.info")

        try:
            tar = tarfile.open(pkg, "r:bz2")
            info = tar.extractfile(blankinfo)
        except tarfile.ReadError:
            raise ex.WarsiInfoError("Reading package information failed")

        content = info.read()
        tags = apt_pkg.TagSection(content)

        tar.close()
        return tags

    def check_sums(self, pkg, extractdata):
        """Check MD5 checksums of Package

        Return TRUE or FALSE checksums of extracted data with dict

        Arguments:
        pkg - A string, name of package
        extractdata - A string, extracted package on temp directory

        Returns:
        check_sums - A dict, with key is name of package and value TRUE or FALSE

        """
        dir = os.path.splitext(pkg)[0]
        blankmanifest = os.path.join(dir, "blank.manifest")

        try:
            tar = tarfile.open(pkg, "r:bz2")
            info = tar.extractfile(blankmanifest)
        except tarfile.ReadError:
            raise ex.WarsiManifestError("Reading package manifest failed")

        content = info.read()

        data = os.path.join(extractdata, 'data')
        check_sums = {}
        lines = content.split("\n")
        for line in lines:
            for deb in os.listdir(data):
                debdata = line.split(" : ")
                deb_abspath = os.path.join(data, deb)

                if deb == debdata[0]:
                    i = md5(open(deb_abspath, "rb").read()).hexdigest()
                    j = debdata[1]
					
                    if i == j:
                        check_sums[debdata[0]] = "TRUE"
                    else:
                        check_sums[debdata[0]] = "FALSE" 

        tar.close()
        return check_sums
			
    def check_version(self, pkg):
        """Check version of Package

        Return 'Newer', 'Older', or 'Same' version of package with dict

        Arguments:
        pkg - A string, name of package

        Returns:
        check_version - A dict, with key is name of package and value 'Newer', 'Older' or 'Same'

        """
        dir = os.path.splitext(pkg)[0]
        split = dir.split("_")
        name = split[0]
        version = split[1]

        main_pkg = self.cache[name]
        sysversion = main_pkg.versions[0].version

        version_compare = apt_pkg.version_compare(sysversion, version)
        check_version = {}

        if version_compare < 0:
            check_version[dir] = "Newer"
        elif version_compare > 0:
            check_version[dir] = "Older"
        else:
            check_version[dir] = "Same"

        return check_version		

    def check_version_all(self, pkg, extractdata):
        """Check version of All Package

        Return 'Newer', 'Older', or 'Same' version of all package on extracted folder with dict

        Arguments:
        pkg - A string, name of package
        extractdata - A string, extracted package on temp directory

        Returns:
        check_version_all - A list, dict with key is name of package and value 'Newer', 'Older' or 'Same'

        """
        dir = os.path.splitext(pkg)[0]
        split = dir.split("_")
        name = split[0]

        main_pkg = self.cache[name]
        check_version_all = []

        for dep in main_pkg.candidateDependencies:
            for deps in dep.or_dependencies:
                debs = os.path.join(extractdata, "data")

                for deb in os.listdir(debs):
                    split = deb.split("_")
                    name = split[0]

                    if deps.name == name:
                        check = self.check_version(deb) 
                        check_version_all.append(check)

        return check_version_all

    def mark_install(self, pkg, extractdata):
        """Mark install required package

        Return list of marked_install package and copy deb packages to cache directory

        Arguments:
        pkg - A string, name of package
        extractdata - A string, extracted package on temp directory

        Returns:
        install_pkg - A list, list of package will be install

        """
        dir = os.path.splitext(pkg)[0]
        split = dir.split("_")
        name = split[0]

        install_pkg = []
        main_pkg = self.cache[name]
        if not main_pkg.is_installed:
            main_pkg.mark_install
            install_pkg.append(main_pkg)
      
        for deps_cache in main_pkg.candidateDependencies:
            for dep_cache in deps_cache.or_dependencies:
                debs = os.path.join(extractdata, "data")

                for deb in os.listdir(debs):
                    split = deb.split("_")
                    name = split[0]
                    debfile = os.path.join(debs, deb)

                    if dep_cache.name == name:
                        dep_pkg = self.cache[name]

                        if not dep_pkg.is_installed:
                            dep_pkg.mark_install()
                            self.copy_debs(debfile)
                            install_pkg.append(dep_pkg)

        return install_pkg

    def copy_debs(self, debfile):
        """Copy deb package file to CacheDir

        Copy deb packages to cache directory

        Arguments:
        debfile - A string, name of deb package

        """
        cachedir = apt_pkg.config.find_dir("Dir::Cache::Archives")
        try:		
            shutil.copy(debfile, cachedir)
        except shutil.Error:
            raise ex.WarsiCopyDebPackage("%s exist on cache directory" %debfile)        

    def commit_install(self):
        """Install Package

        Do install with apt.commit

        """
        debs = self.cache.get_changes()
        for deb in debs:        
            if self.cache.has_key(deb.name):
                deb.commit(apt.progress.TextFetchProgress(), apt.progress.InstallProgress())

    def commit_install_gui(self):
        """Install Package

        Do install with apt.commit and GTK Progressbar

        """
        debs = self.cache.get_changes()        
        progress = apt.progress.gtk2.GtkAptProgress()
        for deb in debs:        
            if self.cache.has_key(deb.name):
                deb.commit(progress.fetch, progress.install)
