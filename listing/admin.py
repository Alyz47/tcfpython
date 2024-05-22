from django.contrib import admin

from .models import (Listing,
                     ListingImage,
                     Category,
                     SubCategory,
                     Feedback,
                     Size,
                     Preference,
                     PreferredSize,
                     PreferredSubCategory,
                     SubCategoryClassification)


class ListingAdmin(admin.ModelAdmin):
    list_display = ('uuid', 'title', 'gender', 'category', 'seller', 'is_sold', 'created', 'modified')
    list_filter = ('title', 'category', 'seller', 'is_sold', 'created', 'modified')


class ListingImageAdmin(admin.ModelAdmin):
    list_display = ('listing', 'image', 'is_cover')


class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    list_display = ('id', 'name', 'slug', 'image')


class SubCategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    list_display = ('name', 'slug', 'image', 'main_category', 'gender')


class SizeAdmin(admin.ModelAdmin):
    list_display = ('category', 'size')
    list_filter = ('category',)

    # def get_cat_slug(self, obj):
    #     return obj.category.slug if obj.category else None
    # get_cat_slug.short_description = 'Category Slug'


class PreferenceAdmin(admin.ModelAdmin):
    list_display = ('user_profile',)


class PreferredSubCategoryAdmin(admin.ModelAdmin):
    list_display = ('preference', 'sub_category')


class PreferredSizeAdmin(admin.ModelAdmin):
    list_display = ('preference', 'size')

class SubCategoryClassificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'uploaded_image', 'sub_category', 'score')


admin.site.register(Listing, ListingAdmin)
admin.site.register(ListingImage, ListingImageAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(SubCategory, SubCategoryAdmin)
admin.site.register(Feedback)
admin.site.register(Size, SizeAdmin)
admin.site.register(Preference, PreferenceAdmin)
admin.site.register(PreferredSize, PreferredSizeAdmin)
admin.site.register(PreferredSubCategory, PreferredSubCategoryAdmin)
admin.site.register(SubCategoryClassification, SubCategoryClassificationAdmin)
