import re
import urllib
from django.utils.safestring import mark_safe
from django.template.defaultfilters import stringfilter
from django.utils.html import conditional_escape
from django.contrib.auth.models import Group
from django import template

register = template.Library()


@register.filter(name="lookupvpnumber")
def lookupvpnumber(value, key):
    try:
        return value.key
    except:
        return key


@register.filter(name='has_group')
def has_group(user, group_name):
    group =  Group.objects.get(name=group_name)
    return group in user.groups.all()

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


@register.filter
@stringfilter
def qrcode(value, alt=None):

    url = conditional_escape("https://api.qrserver.com/v1/create-qr-code/?%s" % \
                             urllib.urlencode({'data': value, 'size': '60x60', 'format':'svg', 'charset-source': 'UTF-8'}))
    alt = conditional_escape(alt or value)

    return mark_safe(u"""<img class="qrcode" src="%s" width="60" height="60" alt="%s" />""" % (url, alt))



