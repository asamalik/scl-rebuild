#!/usr/bin/python
#
# Licensed under the GNU General Public License Version 2
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
#
# Copyright (C) 2015
#   Adam Samalik <adam@samalik.com>


""" 
Part of scl-rebuild: a simple script that rebuilds Software Collections from CentOS 
dist-git in the Copr Build Service.
"""


import shutil
import sh
import tempfile

class CollectionDownloader:
    """
    Downloads and stores the srpm files locally.

    Example usage:
    ======================================================================
    with CollectionDownloader("mariadb100") as downloader:
        downloader.add_meta()
        print downloader.meta_pkg.srpm_name
        downloader.meta_pkg.copy_srpm("/home/adam/")
        downloader.meta_pkg.copy_srpm("adam@example.com:", remote=True)

        downloader.add_package("mariadb")
        print downloader.pkgs[0].srpm_name
        downloader.pkgs[0].copy_srpm("/home/adam/")
        downloader.pkgs[0].copy_srpm("adam@example.com:", remote=True)
    ======================================================================
    """
    # Config:
    distgit_url = "https://git.centos.org/git/sig-sclo/"

    # Content:
    meta_pkg = None
    pkgs = []

    def __init__(self, scl_name):
        self.scl_name = scl_name

    def __enter__(self):
        self.tmp_dir = tempfile.mkdtemp(prefix="scl-rebuild-")
        return self

    def __exit__(self, type, value, traceback):
        shutil.rmtree(self.tmp_dir)

    def add_meta(self):
        self.meta_pkg = Package(self, self.scl_name)
        self.meta_pkg.download()
        self.meta_pkg.make_srpm()

    def add_package(self, name):
        pkg = Package(self, name)
        pkg.download()
        pkg.make_srpm()
        self.pkgs.append(pkg)

class Package:
    """
    Represents a single package. Needed by CollectionDownloader.
    """
    def __init__(self, downloader, name):
        self.downloader = downloader
        self.name = name
        self.git_url = self.downloader.distgit_url + name + ".git"
        self.srpm_name = ""

    def download(self):
        sh.cd(downloader.tmp_dir)
        sh.git("clone", self.git_url)
        sh.cd(self.name)
        sh.git("checkout", "scl-" + downloader.scl_name + "-el7")
        sh.fedpkg("sources")

    def make_srpm(self):
        sh.cd(downloader.tmp_dir)
        sh.cd(self.name)
        sh.rpmbuild("-bs", "--define", "scl {}".format(downloader.scl_name),
                           "--define", "_topdir .",
                           "--define", "_sourcedir .",
                           "{}.spec".format(self.name))
        self.srpm_name = str(sh.ls("SRPMS")).strip()

    def copy_srpm(self, destination, remote=False):
        sh.cd(downloader.tmp_dir)
        sh.cd(self.name)
        sh.cd("SRPMS")
        if remote:
            sh.scp(self.srpm_name, destination)
        else:
            sh.cp(self.srpm_name, destination)
