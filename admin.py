# ===== shoes/admin.py =====
from django.contrib import admin
from django.utils.html import format_html
from .models import Brand, Shoe, ShoeImage

class ShoeImageInline(admin.TabularInline):
    model = ShoeImage
    extra = 1
    readonly_fields = ['image_preview']
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="100" height="100" />', obj.image.url)
        return "无图片"
    image_preview.short_description = "图片预览"

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ['name', 'name_en', 'website', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'name_en']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(Shoe)
class ShoeAdmin(admin.ModelAdmin):
    list_display = [
        'get_full_name', 'brand', 'category', 'retail_price', 'currency',
        'release_year', 'is_active', 'is_limited', 'stock_quantity'
    ]
    list_filter = [
        'brand', 'category', 'release_year', 'is_active', 'is_limited',
        'created_at', 'size_system'
    ]
    search_fields = ['model', 'colorway', 'brand__name', 'sku']
    readonly_fields = ['sku', 'created_at', 'updated_at', 'created_by']
    inlines = [ShoeImageInline]
    
    fieldsets = (
        ('基本信息', {
            'fields': ('brand', 'model', 'version', 'colorway', 'category')
        }),
        ('产品详情', {
            'fields': ('description', 'features', 'materials', 'weight', 'heel_height')
        }),
        ('价格与发售', {
            'fields': ('retail_price', 'currency', 'release_year')
        }),
        ('尺码信息', {
            'fields': ('size_system', 'available_sizes')
        }),
        ('库存与状态', {
            'fields': ('sku', 'stock_quantity', 'is_active', 'is_limited')
        }),
        ('元数据', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_full_name(self, obj):
        return f"{obj.brand.name} {obj.model} - {obj.colorway}"
    get_full_name.short_description = "完整名称"
    
    def save_model(self, request, obj, form, change):
        if not change:  # 新建时
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(ShoeImage)
class ShoeImageAdmin(admin.ModelAdmin):
    list_display = ['shoe', 'alt_text', 'is_primary', 'order', 'image_preview']
    list_filter = ['is_primary', 'uploaded_at']
    search_fields = ['shoe__model', 'shoe__colorway', 'alt_text']
    readonly_fields = ['image_preview', 'uploaded_at']
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="150" height="150" />', obj.image.url)
        return "无图片"
    image_preview.short_description = "图片预览"
