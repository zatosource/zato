# -*- coding: utf-8 -*-

"""
Copyright (C) 2010 Dariusz Suchojad <dsuch at gefira.pl>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import argparse, os, shutil, tarfile, time

description = "Configures the prerequisites for building DEBs for a given distribution, release and Zato version."
epilog = """All arguments are required. For instance, to configure everything for building DEBs for Ubuntu Karmic and Zato 1.0, you need to invoke:

$ python build.py ubuntu karmic 1.0

Any left-over artifacts from previous runs will be safely backed up in ./_backup and no data will ever be lost.
"""

_opts_distro_name = "Distribution name"
_opts_distro_release = "Distribution release"
_opts_zato_version = "Zato version"

supported_distro = ("ubuntu", "debian")

class DebConfig(object):
    def __init__(self, distro, distro_release, zato_version):
        self.distro = distro
        self.distro_release = distro_release
        self.zato_version = zato_version

    def _backup(self, base_dir, source_dir):
        now = time.strftime("%Y-%m-%d_%H-%M-%S", time.gmtime())
        arch_name = os.path.join(base_dir, "_backup", self.distro + "-" + self.distro_release + "-" + now + ".tar.gz")
        tar = tarfile.open(arch_name, "w:gz")

        os.chdir(source_dir)

        tar.add("./")
        tar.close()

        print("Backup saved in {arch_name}".format(arch_name=arch_name))

    def run(self):
        base_dir = os.getcwd()
        distro_release_dir = os.path.join(base_dir, self.distro, self.distro_release)
        zato_dir_name = "zato-" + self.zato_version

        # Make a backup of things left over from previous invocations, if any,
        # and then delete all stuff.
        if os.path.exists(distro_release_dir):
            self._backup(base_dir, distro_release_dir)
            shutil.rmtree(distro_release_dir)

        # Copy the template to a target directory

        src_dir = os.path.join(base_dir, "_template")
        dst_dir = os.path.join(distro_release_dir, zato_dir_name)
        shutil.copytree(src_dir, dst_dir)

        # Create a new .tar.gz archive which will be a base for creating DEBs.

        os.chdir(distro_release_dir)
        targz_name = os.path.join(distro_release_dir, zato_dir_name + ".tar.gz")
        tar = tarfile.open(targz_name, "w:gz")
        tar.add("./" + zato_dir_name)
        tar.close()

        shutil.copy2(targz_name, "zato_" + self.zato_version + ".orig.tar.gz")

        # Fill in the concrete distribution release.

        f = open(os.path.join(dst_dir, "debian", "changelog"), "r")
        changelog = f.read()
        f.close()

        f = open(os.path.join(dst_dir, "debian", "changelog"), "w")
        f.write(changelog.format(distro_release=self.distro_release))
        f.close()

        # Get ready for the action..
        print("You can now go to {dst_dir} and start building DEBs.".format(dst_dir=dst_dir))


def main():
    parser = argparse.ArgumentParser(description=description,
            formatter_class=argparse.RawDescriptionHelpFormatter, epilog=epilog)
    parser.add_argument("distro", help=_opts_distro_name, choices=supported_distro)
    parser.add_argument("distro_release", help=_opts_distro_release)
    parser.add_argument("zato_version", help=_opts_zato_version)

    args = parser.parse_args()

    dc = DebConfig(args.distro, args.distro_release, args.zato_version)
    dc.run()

if __name__ == "__main__":
    main()