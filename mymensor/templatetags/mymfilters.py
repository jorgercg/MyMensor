import re
from django.utils.safestring import mark_safe
from django import template

register = template.Library()

@register.filter(name="lookupvpnumber")
def lookupvpnumber(value, key):
    try:
        return value.key
    except:
        return key


@register.filter(name="frommillistoseconds")
def frommillistoseconds(value):
    return int(value/1000)


class_re = re.compile(r'(?<=class=["\'])(.*)(?=["\'])')

@register.filter
def add_class(value, css_class):
    string = unicode(value)
    match = class_re.search(string)
    if match:
        m = re.search(r'^%s$|^%s\s|\s%s\s|\s%s$' % (css_class, css_class,
                                                    css_class, css_class), match.group(1))
        print match.group(1)
        if not m:
            return mark_safe(class_re.sub(match.group(1) + " " + css_class,
                                          string))
    else:
        return mark_safe(string.replace('>', ' class="%s">' % css_class))
    return value



