from django import template

register = template.Library()

@register.filter
def is_ajax(request):
    return request.headers.get('X-Requested-With') == 'XMLHttpRequest'