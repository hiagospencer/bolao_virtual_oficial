from django import template

register = template.Library()

@register.filter
def subtract(value, arg):
    return value - arg

@register.filter(name='absolute')  # Renomeado para evitar conflito
def absolute(value):
    return abs(value)
