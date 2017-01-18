from django import template

register = template.Library()

@register.filter(name="lookupvpnumber")
def lookupvpnumber(value, key):
    return value[key]