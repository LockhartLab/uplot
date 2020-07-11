"""
merge_dev_with_master.py
written in Python3
author: C. Lockhart <chris@lockhartlab.org>
"""

from _scripts.increment_version import *
from gitpipe import Git

# Connect to git repository
git = Git()

# We must be on dev branch
branch = git.get_branch()
assert branch == 'dev', branch

# Increment version; print out string
version = increment_version()
print('package version: {}\n'.format(version))

# Add, commit, and push any uncommitted changes
git.add('-A')
git.commit(input('Commit message: '))
git.push(remote='origin', branch='dev')

# Checkout master, merge, tag, and push
git.checkout('master')
git.merge(branch='dev', options='--no-edit')
git.tag('v' + version)
git.push(remote='origin', branch='master', options='--tags')

