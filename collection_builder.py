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


import time
from copr.client import CoprClient


class CollectionBuilder:
    def __init__(self, username, sclname, coprname, pkgs):
        self.client = CoprClient.create_from_file_config()
        self.pkgs = pkgs
        self.username = username
        self.sclname = sclname
        self.coprname = coprname

    def build_meta(self):
        print "\nBuilding meta-package: (please do not interrupt)"
        result = self.client.create_new_build(self.coprname,
                                              pkgs=self.pkgs[:1],
                                              username=self.username)
        print "  Build id: {}".format(result.builds_list[0].build_id)

        prev_status = ""
        while True:
            status = result.builds_list[0].handle.get_build_details().status
            if prev_status != status:
                prev_status = status
                print "  {0}: {1}".format(time.strftime("%H:%M:%S"),status)
            if status in ["skipped", "succeeded"]:
                return True
            if status in ["failed"]:
                print "  Build failed! See logs for more details:"
                print "  https://copr.fedoraproject.org/coprs/{0}/{1}/build/{2}".format(
                                    self.username, self.coprname,
                                    result.builds_list[0].build_id)
                return False
            if status in ["cancelled"]:
                print "  Build cancelled!"
                return False
            time.sleep(10)


    def build_pkgs(self):
        print "\nBuilding other packages. Total: {}".format(len(self.pkgs[1:]))
        for pkg in self.pkgs[1:]:
            result = self.client.create_new_build(self.coprname,
                                              pkgs=self.pkgs[1:],
                                              username=self.username)

        print "(This script can be safely interrupted now)"
        try:
            watched = set(result.builds_list)
            done = set()
            result_counter = {
                "skipped": 0,
                "failed": 0,
                "succeeded": 0}
            while watched != done:
                for bw in watched:
                    if bw in done:
                        continue
                    status = bw.handle.get_build_details().status
                    if status in ["skipped", "failed", "succeeded"]:
                        result_counter[status] += 1
                        done.add(bw)
                        print "\n  {0}".format(time.strftime("%H:%M:%S"))
                        print "    skipped:   {}".format(result_counter["skipped"])
                        print "    succeeded: {}".format(result_counter["succeeded"])
                        print "    failed:    {}".format(result_counter["failed"])
                        print "    remaining: {}".format(len(watched) - len(done))
                time.sleep(10)
            print "  Done!"
        except KeyboardInterrupt:
            pass
