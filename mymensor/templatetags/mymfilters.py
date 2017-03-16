import re
import urllib
from django.utils.safestring import mark_safe
from django.template.defaultfilters import stringfilter
from django.utils.html import conditional_escape
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


@register.filter
@stringfilter
def qrcode(value, alt=None):
    """
    Generate QR Code image from a string with the Google charts API

    http://code.google.com/intl/fr-FR/apis/chart/types.html#qrcodes

    Exemple usage --
    {{ my_string|qrcode:"my alt" }}

    <img src="http://chart.apis.google.com/chart?chs=150x150&amp;cht=qr&amp;chl=my_string&amp;choe=UTF-8" alt="my alt" />
    """

    url = conditional_escape("https://api.qrserver.com/v1/create-qr-code/?%s" % \
                             urllib.urlencode({'size': '150x150', 'data': value, 'charset-source': 'UTF-8'}))
    alt = conditional_escape(alt or value)

    return mark_safe(u"""<img class="qrcode" src="%s" width="150" height="150" alt="%s" />""" % (url, alt))



