from django import template

register = template.Library()

@register.filter
def multiply(value, arg):
    """Multiplies the value by the argument"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0


@register.filter
def filter(queryset, arg):
    """Filters a queryset based on field=value argument"""
    try:
        field, value = arg.split('=')
        kwargs = {field: value}
        return [item for item in queryset if getattr(item, field) == value]
    except (ValueError, AttributeError):
        return queryset
    
    
    

@register.filter
def sub(value, arg):
    """Subtracts the argument from the value"""
    try:
        return float(value) - float(arg)
    except (ValueError, TypeError):
        return 0    
    


@register.filter
def subtract(value, arg):
    return float(value) - float(arg)    


@register.filter
def multiply(value, arg):
    return float(value) * float(arg)



@register.filter
def divide(value, arg):
    """Divide the value by the arg."""
    try:
        return value / arg
    except (ValueError, TypeError, ZeroDivisionError):
        return 0
