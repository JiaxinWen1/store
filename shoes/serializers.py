# ===== shoes/serializers.py =====
from rest_framework import serializers
from .models import Brand, Shoe, ShoeImage

class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = '__all__'

class ShoeImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShoeImage
        fields = ['id', 'image', 'alt_text', 'is_primary', 'order', 'uploaded_at']

class ShoeListSerializer(serializers.ModelSerializer):
    """鞋款列表序列化器（简化版）"""
    brand_name = serializers.CharField(source='brand.name', read_only=True)
    primary_image = serializers.SerializerMethodField()

    class Meta:
        model = Shoe
        fields = [
            'id', 'brand_name', 'model', 'colorway', 'category',
            'release_year', 'retail_price', 'currency', 'primary_image',
            'is_active', 'is_limited', 'created_at'
        ]

    def get_primary_image(self, obj):
        primary_img = obj.images.filter(is_primary=True).first()
        if primary_img:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(primary_img.image.url)
        return None

class ShoeDetailSerializer(serializers.ModelSerializer):
    """鞋款详情序列化器（完整版）"""
    brand_info = BrandSerializer(source='brand', read_only=True)
    images = ShoeImageSerializer(many=True, read_only=True)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)

    class Meta:
        model = Shoe
        fields = '__all__'

class ShoeCreateUpdateSerializer(serializers.ModelSerializer):
    """鞋款创建/更新序列化器"""
    
    class Meta:
        model = Shoe
        exclude = ['created_by', 'created_at', 'updated_at']

    def validate_available_sizes(self, value):
        """验证尺码格式"""
        if not isinstance(value, list):
            raise serializers.ValidationError("尺码必须是列表格式")
        return value

    def validate_features(self, value):
        """验证特性格式"""
        if not isinstance(value, list):
            raise serializers.ValidationError("特性必须是列表格式")
        return value
