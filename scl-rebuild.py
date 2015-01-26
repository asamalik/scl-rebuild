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
A simple script that rebuilds Software Collections from CentOS
dist-git in the Copr Build Service.
"""

import getpass
import argparse
from argparse import RawTextHelpFormatter

from collection_downloader import CollectionDownloader
#
# TODO: PACKAGE LIST GETTER
#
# Gets:
# - Scl name:
#       mariadb100
#
#
# TODO: MAIN SCRIPT
#
# Gets:
# - Scl name:
#       mariadb100
#
# - Storage:
#       asamalik@fedorapeople.org:/public_html/
#       https://asamalik.fedorapeople.org/
#
# - Copr project:
#       asamalik/mariadb100
#
#

def main():
    parser = argparse.ArgumentParser(description="""
        A simple script that rebuilds Software Collections from CentOS
        dist-git in the Copr Build Service.
        """, formatter_class=RawTextHelpFormatter)

    parser.add_argument("sclname",
        help="A name of the collection.")
    parser.add_argument("-u", "--username",
        help="Set the username to be used with services."
             "\n(Default: your system username)")
    parser.add_argument("-d", "--destination",
        help="Set the destination you want to store srpms."
             "\n(Default: <username>@fedorapeople.org:/public_html/<sclname>)")
    parser.add_argument("-s", "--source-url",
        help="Set the URL from which the srpms will be accessible."
             "\n(Default: https://<username>.fedorapeople.org/<sclname>)")
    parser.add_argument("-c", "--copr-project",
        help="Set the name of your Copr project.")
    parser.add_argument("-l", "--local-download", action="store_true",
        help="Downloads the srpms locally without building them.")
    parser.add_argument("-n", "--no-build", action="store_true",
        help="Just uploads the srpms without building them.")
    parser.add_argument("-v", "--verbose", action="store_true",
        help="Increases output verbosity.")
    args = parser.parse_args()

    sclname = args.sclname
    username = args.username or getpass.getuser()
    source_url = args.source_url or "https://{0}.fedorapeople.org/{1}".format(
                            username, sclname)
    destination = args.destination or "{0}@fedorapeople.org:public_html/".format(
                            username)
    copr_project = args.copr_project or "{0}/{1}".format(
                            username, sclname)

    with CollectionDownloader(sclname) as downloader:
        downloader.add_meta()
        downloader.add_pkg("mariadb")
        downloader.copy_pkgs(destination, remote=(not args.local_download))


if __name__ == "__main__":
    main()
