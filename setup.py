from setuptools import setup
import os, sys

here = os.path.abspath( os.path.dirname( __file__ ))

__version__			= None
__version_info__		= None
exec( open( 'version.py', 'r' ).read() )

setup(
    name			= "threading_sched",
    version			= __version__,
    tests_require		= [ "pytest" ],
    install_requires		= [],
    packages			= [ 
        "threading_sched",
    ],
    package_dir			= {
        "threading_sched":		".",
    },
    include_package_data	= True,
    author			= "Perry Kundert",
    author_email		= "perry@hardconsulting.com",
    description			= "Threading_sched implements a Thread-safe version of Python sched",
    long_description		= """\
In a multi-Threaded Python program, simple and priority scheduling may be
required.  The basic Python 'sched' implementation does not support Threads.
Use 'import threading_sched as sched' to get the basic sched.scheduler API w/
Thread safety.  The sched.scaled_scheduler provides a priority scheduler.
""",
    license			= "GPLv3",
    keywords			= "sched Thread",
    url				= "https://github.com/pjkundert/threading_sched",
    classifiers			= [
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Environment :: Console",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
