import datetime

from django.template import Library
from django.template.defaultfilters import stringfilter

register = Library()

@stringfilter
def parse_date(date_string):
    try:
        print(date_string)
        return datetime.datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%SZ")
    except ValueError:
        print("ValueError")
        return None


register.filter(parse_date)
