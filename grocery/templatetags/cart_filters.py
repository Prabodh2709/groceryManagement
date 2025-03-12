from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key, 0)

@register.filter
def multiplication(a, b):
    return a * b

@register.filter
def is_dictionary_empty(dictionary):
    return len(dictionary.keys())