import ez_setup
ez_setup.use_setuptools()
from setuptools import setup
setup(
    name = "othellotk",
    version = "0.1.0",
    packages = ["othellotk"],

    entry_points={
        'gui_scripts': [
            'othellotk = othellotk.othellotk:main',
        ]
    },

    # metadata for upload to PyPI
    author = "John Cheetham",
    author_email = "kaama12@yahoo.co.uk",
    description = "Edax gui to play Othello against the Edax engine",
    license = "GPLv3+",
    keywords = "othello edax tkinter",
    url = "http://www.johncheetham.com/projects/othellotk/",
)
