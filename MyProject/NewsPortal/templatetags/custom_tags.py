from django import template
from datetime import datetime
register = template.Library()

@register.simple_tag()
def current_time(format_string):
    return datetime.utcnow().strftime(format_string)

@register.simple_tag(takes_context = True)
def url_replace(context,**kwargs):
   d = context['request'].GET.copy()
   for i , v in kwargs.items():
      d[i] = v
   return d.urlencode()


