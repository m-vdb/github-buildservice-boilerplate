"""Template tags utils."""
from django import template


register = template.Library()


@register.simple_tag
def build_icon(build):
    """
    Return the build icon name.
    """
    if build.is_success:
        return 'done'
    elif build.is_pending:
        return 'alarm'

    return 'clear'


@register.simple_tag
def build_icon_color(build):
    """
    Return the build icon color.
    """
    if build.is_success:
        return 'success'
    elif build.is_pending:
        return 'warning'

    return 'danger'
