from github3 import login


def get_user_repos(token):
    """
    Get all user repositories using a OAuth Token.
    """
    gh = login(token)
    return gh.all_repositories()
