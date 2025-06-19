from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """
    Возвращает значение словаря по ключу.
    Использование: {{ dictionary|get_item:key }}
    """
    return dictionary.get(key, 0)