"""
deploy_to_dev.py
written in Python3
author: C. Lockhart <chris@lockhartlab.org>
"""


from gitpipe import Git


# Connect to repository
git = Git()

# Connect to git repository, tag, add files, commit, push
git = Git()
git.add('-A')
git.commit(input('Commit message: '))
git.push(remote='origin', branch='dev')
