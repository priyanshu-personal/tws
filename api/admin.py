from django.contrib import admin
from .models import Bill, Category, Item, InventorySold, Biller

# Customize Admin site settings
admin.site.site_header = "The Wadhwa Store"
admin.site.site_title = "The Wadhwa Store"
admin.site.index_title = "The Wadhwa Store"
# Register your models here.


class BillSearchableFields(admin.ModelAdmin):
    search_fields = ['customer_name', 'date']
    list_display = ['date', 'time', 'customer_name', 'total', 'mode_of_payment', 'biller']
    

class ItemAdmin(admin.ModelAdmin):
    search_fields = ['name', 'category__name']
    list_display = ['category', 'name', 'price']
    
class InventorySoldAdmin(admin.ModelAdmin):
    search_fields = ['name', 'date']
    list_display = ['date', 'name', 'quantity', 'total']

class BillerAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_display = ['name']

admin.site.register(Bill, BillSearchableFields)
# admin.site.register(Bill, ItemAdmin)
admin.site.register(Category)
admin.site.register(Item,ItemAdmin)
admin.site.register(InventorySold,InventorySoldAdmin)
admin.site.register(Biller, BillerAdmin)

