"""Utilities for views."""
from collections import defaultdict


def group_repositories(repos):
    """
    Group repositories given the owner of
    the repo, as follow:
    - if there are more than 2 repos for the same
      owner, then all the repos are under the same
      display section.
    - else, the repo is nested under an 'Other' section.

    :param repos:           an iterable of github Repositories
    """
    sections = defaultdict(list)
    for repo in repos:
        sections[repo.owner.login].append(repo)

    for key in sections.keys():
        if len(sections[key]) <= 1:
            sections['Other'].extend(sections.pop(key))

    # put 'Other' section at the end
    # and compare lowercase
    order = lambda t: 'z' * 100 if t[0] == 'Other' else t[0].lower()
    return sorted(sections.items(), key=order)
