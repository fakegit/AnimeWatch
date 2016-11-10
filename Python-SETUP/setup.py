"""
Copyright (C) 2016 kanishka-linux kanishka.linux@gmail.com

This file is part of AnimeWatch.

AnimeWatch is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

AnimeWatch is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with AnimeWatch.  If not, see <http://www.gnu.org/licenses/>.



"""


from setuptools import setup

setup(
    name='animewatch',
    version='3.0.0',
    license='GPLv3',
    author='kanishka-linux',
    author_email='kanishka.linux@gmail.com',
    url='https://github.com/kanishka-linux/AnimeWatch',
    long_description="README.md",
    packages=['AnimeWatch_PyQt5','AnimeWatch_PyQt5.Plugins'],
    include_package_data=True,
    entry_points={'gui_scripts':['animewatch = AnimeWatch_PyQt5.animeWatch:main'],},
    package_data={'AnimeWatch_PyQt5':['tray.png','default.jpg','AnimeWatch.desktop','input.conf','animewatch-start','1.png','Instructions']},
    install_requires=['pycurl','bs4','Pillow','pytaglib','python-libtorrent','lxml','youtube_dl','urllib3','dbus-python','psutil'],
    description="A Audio/Video manager and Front End for mpv/mplayer with special emphasis on Anime Collection",
)