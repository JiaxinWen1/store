# ===== shoes/models.py =====
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid
import os

def shoe_image_path(instance, filename):
    """自定义图片上传路径"""
    ext = filename.split('.')[-1]
    filename = f'{uuid.uuid4().hex}.{ext}'
    return os.path.join('shoes', str(instance.shoe.id), filename)

class Brand(models.Model):
    """品牌模型"""
    name = models.CharField('品牌名称', max_length=50, unique=True)
    name_en = models.CharField('英文名称', max_length=50, blank=True)
    logo = models.ImageField('品牌Logo', upload_to='brands/', blank=True, null=True)
    description = models.TextField('品牌描述', blank=True)
    website = models.URLField('官方网站', blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '品牌'
        verbose_name_plural = '品牌'
        ordering = ['name']

    def __str__(self):
        return self.name

class Shoe(models.Model):
    """鞋子主模型"""
    CATEGORY_CHOICES = [
        ('basketball', '篮球鞋'),
        ('running', '跑步鞋'),
        ('lifestyle', '生活鞋款'),
        ('football', '足球鞋'),
        ('skateboard', '滑板鞋'),
        ('other', '其他'),
    ]

    SIZE_SYSTEM_CHOICES = [
        ('US', '美码'),
        ('UK', '英码'),
        ('EU', '欧码'),
        ('CN', '中国码'),
        ('JP', '日本码'),
    ]

    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, verbose_name='品牌')
    model = models.CharField('型号', max_length=100)
    version = models.CharField('版本', max_length=50, blank=True)
    colorway = models.CharField('配色', max_length=100)
    category = models.CharField('分类', max_length=20, choices=CATEGORY_CHOICES, default='lifestyle')
    release_year = models.PositiveIntegerField(
        '发售年份',
        validators=[MinValueValidator(1950), MaxValueValidator(9999)],
        blank=True,
        null=True
    )
    retail_price = models.DecimalField('官方零售价', max_digits=10, decimal_places=2, blank=True, null=True)
    currency = models.CharField('货币', max_length=3, default='CNY')
    
    # 尺码相关
    size_system = models.CharField('尺码体系', max_length=2, choices=SIZE_SYSTEM_CHOICES, default='US')
    available_sizes = models.JSONField('可选尺码', default=list, blank=True)
    
    # 详细信息
    description = models.TextField('产品描述', blank=True)
    features = models.JSONField('产品特性', default=list, blank=True)
    materials = models.TextField('材质信息', blank=True)
    
    # 技术参数
    weight = models.PositiveIntegerField('重量(克)', blank=True, null=True)
    heel_height = models.DecimalField('鞋跟高度(厘米)', max_digits=4, decimal_places=1, blank=True, null=True)
    
    # SKU和库存
    sku = models.CharField('SKU', max_length=50, unique=True, blank=True)
    stock_quantity = models.PositiveIntegerField('库存数量', default=0)
    
    # 状态
    is_active = models.BooleanField('是否激活', default=True)
    is_limited = models.BooleanField('是否限量', default=False)
    
    # 元数据
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='创建者')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '鞋款'
        verbose_name_plural = '鞋款'
        ordering = ['-created_at']
        unique_together = ['brand', 'model', 'colorway']

    def __str__(self):
        return f"{self.brand.name} {self.model} - {self.colorway}"

    def save(self, *args, **kwargs):
        # 自动生成SKU
        if not self.sku:
            self.sku = f"{self.brand.name[:3].upper()}-{self.model[:10].upper()}-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

class ShoeImage(models.Model):
    """鞋子图片模型"""
    shoe = models.ForeignKey(Shoe, on_delete=models.CASCADE, related_name='images', verbose_name='鞋款')
    image = models.ImageField('图片', upload_to=shoe_image_path)
    alt_text = models.CharField('图片描述', max_length=200, blank=True)
    is_primary = models.BooleanField('是否为主图', default=False)
    order = models.PositiveIntegerField('排序', default=0)
    uploaded_at = models.DateTimeField('上传时间', auto_now_add=True)

    class Meta:
        verbose_name = '鞋子图片'
        verbose_name_plural = '鞋子图片'
        ordering = ['order', '-uploaded_at']

    def __str__(self):
        return f"{self.shoe} - 图片 {self.order}"

    def save(self, *args, **kwargs):
        # 如果设置为主图，取消其他图片的主图状态
        if self.is_primary:
            ShoeImage.objects.filter(shoe=self.shoe, is_primary=True).exclude(pk=self.pk).update(is_primary=False)
        super().save(*args, **kwargs)