"""
increment_version.py
written in Python3
author: C. Lockhart <chris@lockhartlab.org>
"""


import yaml


# Helper function to increment the package version
# noinspection PyShadowingNames
def increment_version():
    # Read in version
    with open('version.yml', 'r') as f:
        version = yaml.safe_load(f.read())

    # Update patch
    version['patch'] += 1

    # Output version
    with open('version.yml', 'w') as f:
        yaml.safe_dump(version, f)

    # Transform version dict to string
    version = '.'.join([str(version[key]) for key in ['major', 'minor', 'patch']])

    # Write version string to uplot/_version.py
    with open('uplot/_version.py', 'w') as f:
        f.write("__version__ = '{}'\n".format(version))

    # Return
    return version
