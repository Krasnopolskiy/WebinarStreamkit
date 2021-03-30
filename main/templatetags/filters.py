from datetime import datetime
from typing import Any, Dict, Optional

from django.template.defaulttags import register


@register.filter
def get_item(dictionary: Dict[Any, Any], key: Any) -> Any:
    return dictionary.get(key)


@register.filter
def parse_date(date_string: str) -> Optional[datetime]:
    try:
        return datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%S%z")
    except ValueError:
        return None
