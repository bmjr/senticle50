from django import template

register = template.Library()


@register.filter(name='row_size')
def row_size(row_items):
    return 12 // len(row_items)


@register.filter
def concatenate(string, string_to_add):
    return str(string) + str(string_to_add)


@register.filter
def dictionary_lookup(dictionary, key):
    if key in dictionary:
        return dictionary[key]

    return None
