from django.template.defaulttags import register
from datetime import datetime


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


@register.filter
def parse_date(date_string):
    try:
        return datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%S%z")
    except ValueError:
        return None
