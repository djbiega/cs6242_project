from setuptools import find_packages, setup

setup(
    name='cs6242_project',
    version="0.0.1",
    packages=find_packages(),
    description='Interactive music recommender',
    author='CS6242 Team 21',
    install_requires=[
        "numpy>=1.21.2",
        "pandas>=1.3.4",
        "notebook>=6.4.5",
        "spotipy>=2.19.0",
    ],
)
