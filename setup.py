from setuptools import find_packages, setup

APP_EXTRAS = [
    "Flask",
    "scikit-learn",
    "SQLAlchemy",
]

DATA_EXTRAS = [
    "notebook>=6.4.5",
    "spotipy>=2.19.0",
	"scipy>=1.7.0"
]

DB_EXTRAS = [
    "psycopg2",
    "google-cloud-storage",
]

setup(
    name='cs6242_project',
    version="0.0.1",
    packages=find_packages(),
    description='Interactive music recommender',
    author='CS6242 Team 21',
    install_requires=[
        "numpy>=1.21.2",
        "pandas>=1.3.4",
    ],
    extras_require={
        "data_collection": DATA_EXTRAS,
        "db": DB_EXTRAS,
        "app": APP_EXTRAS,
    },
    entry_points={
        'console_scripts': [
            'process_spotify = cs6242_project.data.process_spotify:main',
        ],
    },
)
