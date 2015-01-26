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

    API provided:
        add_meta()
        add_pkg(<name>)
        copy_pkgs(<destination>,[remote=True])
        pkg_list([path=<some_desired_prefix_path>])
        verbosity = True

    Example usage:
    ======================================================================
    with CollectionDownloader("mariadb100") as downloader:
        downloader.add_meta()
        downloader.add_pkg("mariadb")
        downloader.copy_pkgs("/home/adam/")
        downloader.copy_pkgs("asamalik@example.com:public_html/", remote=True)

        print downloader.meta_pkg.srpm_name
        print downloader.pkgs[0].srpm_name
    ======================================================================
    """
    # Config:
    distgit_url = "https://git.centos.org/git/sig-sclo/"
    verbosity = False

    # Content:
    meta_pkg = None
    pkgs = []

    def __init__(self, scl_name):
        self.scl_name = scl_name

    def __enter__(self):
        self.tmp_git_dir = tempfile.mkdtemp(prefix="scl-rebuild-")
        self.tmp_pkg_dir = tempfile.mkdtemp(prefix="scl-rebuild-pkgs-")

        self.scl_dir = "/".join([self.tmp_pkg_dir, self.scl_name])
        self.pkgs_dir = "/".join([self.tmp_pkg_dir, self.scl_name, "pkgs"])

        sh.mkdir("-p", self.pkgs_dir)
        return self

    def __exit__(self, type, value, traceback):
        shutil.rmtree(self.tmp_git_dir)
        shutil.rmtree(self.tmp_pkg_dir)

    def add_meta(self):
        self.meta_pkg = Package(self, self.scl_name)
        self.meta_pkg.download()
        self.meta_pkg.make_srpm()
        self.meta_pkg.get_srpm(self.scl_dir)

    def add_pkg(self, name):
        pkg = Package(self, name)
        pkg.download()
        pkg.make_srpm()
        pkg.get_srpm(self.pkgs_dir)
        self.pkgs.append(pkg)

    def copy_pkgs(self, destination, remote=False):
        if self.verbosity:
            print "\nCopying srpms to: {}".format(destination)
        if remote:
            sh.scp("-r", self.scl_dir, destination)
        else:
            sh.cp("-r", self.scl_dir, destination)
        if self.verbosity:
            print "  Done."

    def pkg_list(self, path=""):
        if path and path[-1] != "/":
            path += "/"
        pkgs = [path + self.meta_pkg.srpm_name]
        for pkg in self.pkgs:
            pkgs.append(path + "pkgs/" +pkg.srpm_name)
        return pkgs


class Package:
    """
    Represents a single package. Needed by CollectionDownloader.

    This class does not implement any stable public API.
    """
    def __init__(self, downloader, name):
        self.downloader = downloader
        self.name = name
        self.git_url = self.downloader.distgit_url + name + ".git"
        self.srpm_name = ""

    def download(self):
        sh.cd(self.downloader.tmp_git_dir)
        if self.downloader.verbosity:
            print "\nCloning: {}".format(self.git_url)
        sh.git("clone", self.git_url)
        sh.cd(self.name)
        sh.git("checkout", "scl-" + self.downloader.scl_name + "-el7")
        sh.fedpkg("sources")

    def make_srpm(self):
        sh.cd("/".join([self.downloader.tmp_git_dir, self.name]))
        if self.downloader.verbosity:
            print "Creating srpm..."
        sh.rpmbuild("-bs", "--define", "scl {}".format(self.downloader.scl_name),
                           "--define", "_topdir .",
                           "--define", "_sourcedir .",
                           "{}.spec".format(self.name))
        self.srpm_name = str(sh.ls("SRPMS")).strip()
        if self.downloader.verbosity:
            print "  Done: {}".format(self.srpm_name)

    def get_srpm(self, destination):
        sh.mv("/".join([self.downloader.tmp_git_dir,
                        self.name, "SRPMS", self.srpm_name]), destination)
