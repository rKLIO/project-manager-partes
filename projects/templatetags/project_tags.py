from django import template

register = template.Library()

@register.filter
def get_role(memberships_dict, user):
    return memberships_dict.get(user)
