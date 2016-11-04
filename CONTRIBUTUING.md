When contributing to this repo, keep the following in mind:

## Development Branch

The ``master`` branch is focused solely on what is currently in production.
We are using the [gitflow](https://www.atlassian.com/git/tutorials/comparing-workflows/gitflow-workflow)
workflow. So keep in mind the following rules:

- New feature development is based on the ``develop`` branch.
- Only hotfixes to existing bugs in production are to be branched off of ``master``.
- ``master`` and ``develop`` are protected branches.
 - Do not directly push to either of these branches. 
 - Create a feature branch and make a pull request.
 - Your changes will be merged in on passing CI tests and proper review.

## Code Style

This repository is largely python and follows the [PEP8 code style standard](https://www.python.org/dev/peps/pep-0008/).
This is automatically checked by the [pep8](https://pypi.python.org/pypi/pep8)
package. Commits and pull requests failing these tests will not be accepted.

To make it easier on the developer, we suggest using the [autopep8](https://pypi.python.org/pypi/autopep8) tool.
It should be able to fix the majority of minor style errors.

It is recommended to set autopep8 to be extra aggressive in fixes. An example use: 
```
autopep8 --in-place --aggressive --aggressive --recursive src/ test/
```

## Testing

Please write approriate tests when contributing code. Untested code is broken code.
Tests are stored under the ``test/`` top-level directory and are written using
the default ``unittest`` package.
