from django.contrib import admin
from .dubicars_models import (
    AdError,
    DubicarsAd,
    DubicarsAdCharacteristic,
    DubicarsAdExteriorFeature,
    DubicarsAdFinance,
    DubicarsAdInteriorDesign,
    DubicarsAdSecurity,
    DubicarsAdService,
    DubicarsAdWarranty,
    DubicarsCategory,
    DubicarsPage,
    DubicarsTag,
    DubiscrapeImage,
    Update,
    Website,
    )

# Register your models here.

class DubicarsCategoryAdmin(admin.ModelAdmin):
    search_fields = ('name',  )

class DubicarsPageAdmin(admin.ModelAdmin):
    search_fields = ('url',  )

class DubicarsAdAdmin(admin.ModelAdmin):
    search_fields = ('url',  )

class ImageAdmin(admin.ModelAdmin):
    list_display = ('id','image', 'dubicar_ad')


admin.site.register(DubicarsAd, DubicarsAdAdmin)
admin.site.register(DubicarsAdCharacteristic)
admin.site.register(AdError)
admin.site.register(DubicarsAdExteriorFeature)
admin.site.register(DubicarsAdInteriorDesign)
admin.site.register(DubicarsAdSecurity)
admin.site.register(DubicarsCategory, DubicarsCategoryAdmin)
admin.site.register(Website)
admin.site.register(DubiscrapeImage, ImageAdmin)
admin.site.register(Update)
admin.site.register(DubicarsTag)
admin.site.register(DubicarsPage, DubicarsPageAdmin)