from setuptools import setup, find_packages

setup(
    name='SilexExplorerPy',
    version='0.1.0',
    description='A Python package designed to help researchers extract, visualize, and analyze complex phenotypic and environmental data for in-depth scientific insights.',
    author='Sarra ABIDRI',
    author_email='opensilex@inrae.fr ',
    url='https://forge.inrae.fr/OpenSILEX/opensilex-graphql/silexexplorerpy.git',
    packages=find_packages(),
    install_requires=[
        'requests',
        'pandas',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
)