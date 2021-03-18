from django.template import Library
from django.template.defaultfilters import stringfilter
from datetime import datetime

register = Library()

@stringfilter
def parse_date(date_string):
    try:
        print(date_string)
        return datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%S%z")
    except ValueError:
        print("ValueError")
        return None


register.filter(parse_date)
