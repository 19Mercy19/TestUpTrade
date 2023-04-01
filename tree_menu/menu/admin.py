from django.contrib import admin

from .models import Menu, Item


class MenuAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}


admin.site.register(Menu, MenuAdmin)
admin.site.register(Item)
