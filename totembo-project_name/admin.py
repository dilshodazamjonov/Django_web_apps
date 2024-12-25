from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import *
from .forms import *

# Register your models here.

admin.site.register(Brand)
admin.site.register(FavoriteProduct)

# Models for Ordering

admin.site.register(Order)
admin.site.register(OrderProduct)
admin.site.register(Customer)
admin.site.register(Region)
admin.site.register(City)
admin.site.register(ShippingAddress)

# Models for Contacting and Reviews

admin.site.register(SupportMessage)
admin.site.register(Reviews)
admin.site.register(Subscriber)
admin.site.register(Profile)

@admin.register(RatingStar)
class RatingStarAdmin(admin.ModelAdmin):
    list_display = ['value']
    ordering = ['value']

@admin.register(ProductRating)
class ProductRatingAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'star']
    list_filter = ['product', 'star']
    ordering = ['-id']

# admin.site.register(Category)
# admin.site.register(Product)
# admin.site.register(ImageProduct)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['pk', 'title', 'get_icon_category', 'parent', 'image']
    list_display_links = ['pk', 'title']
    prepopulated_fields = {'slug': ('title',)}
    form = CategoryForm
    def get_icon_category(self, obj):
        if obj.icon:
            try:
                return mark_safe(f'<img src="{obj.icon.url}" width="30">')
            except:
                return '-'
        else:
            return '-'

class ImageProductAdminInline(admin.TabularInline):
    fk_name = 'product'
    model = ImageProduct
    extra = 1

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['pk', 'title', 'get_photo', 'price', 'quantity', 'slug', 'category', 'model']
    list_editable = ['quantity', 'price', 'category', 'model']
    list_display_links = ['pk', 'title']
    prepopulated_fields = {'slug': ('title',)}
    list_filter = ['category', 'color', 'price']
    inlines = [ImageProductAdminInline]

    def get_photo(self, obj):
        if obj.images:
            try:
                return mark_safe(f'<img src="{obj.images.first().image.url}" width="40" >')
            except:
                return '-'
        else:
            return '-'