from django import template
from django.http import Http404

from ..models import Item

register = template.Library()


def get_children(items_values, item_id, selected_items_id):
    child_items = list(items_values.filter(parent_id=item_id))
    for item in child_items:
        if item['id'] in selected_items_id:
            item['children'] = get_children(items_values, item['id'], selected_items_id)
    return child_items


def get_selected_items_id(selected_item, main_items):
    selected_items = []
    if selected_item in main_items:
        selected_items.append(selected_item.pk)
        return selected_items
    parent = selected_item
    while parent:
        selected_items.append(parent.pk)
        parent = parent.parent
    return selected_items


def get_querystring(context, menu):
    querystring_args = []
    for key in context['request'].GET:
        if key != menu:
            querystring_args.append(f'{key}={context["request"].GET[key]}')
    querystring = '&'.join(querystring_args)
    return querystring


@register.inclusion_tag("menu/tree_menu.html", takes_context=True)
def draw_menu(context, menu_slug):
    items = Item.objects.filter(menu__slug=menu_slug).select_related('menu', 'parent')
    items_values = items.values()
    main_items = list(items_values.filter(parent=None))
    querystring = get_querystring(context, menu_slug)
    extended_ctx = {'items': main_items, 'menu': menu_slug, 'other_querystring': querystring}
    if menu_slug not in context['request'].GET:
        return extended_ctx
    try:
        select_item_id = int(context['request'].GET[menu_slug])
        selected_item = items.get(pk=select_item_id)
    except Item.DoesNotExist:
        raise Http404
    selected_items_id = get_selected_items_id(selected_item, main_items)
    for item in main_items:
        if item['id'] in selected_items_id:
            item['children'] = get_children(items_values, item['id'], selected_items_id)
    extended_ctx['items'] = main_items
    return extended_ctx

