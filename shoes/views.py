# ===== shoes/views.py =====
from rest_framework import viewsets, status, filters, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from .models import Brand, Shoe, ShoeImage
from .serializers import (
    BrandSerializer, ShoeListSerializer, ShoeDetailSerializer,
    ShoeCreateUpdateSerializer, ShoeImageSerializer
)

from .serializers import BrandSerializer, ShoeSerializer


class BrandViewSet(viewsets.ModelViewSet):
    """品牌视图集"""
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'name_en']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']

class ShoeViewSet(viewsets.ModelViewSet):
    """鞋款视图集"""
    queryset = Shoe.objects.select_related('brand', 'created_by').prefetch_related('images')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['brand', 'category', 'release_year', 'is_active', 'is_limited']
    search_fields = ['model', 'colorway', 'brand__name', 'description']
    ordering_fields = ['created_at', 'updated_at', 'retail_price', 'release_year']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return ShoeListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return ShoeCreateUpdateSerializer
        return ShoeDetailSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'], parser_classes=[MultiPartParser, FormParser])
    def upload_images(self, request, pk=None):
        """上传鞋款图片"""
        shoe = self.get_object()
        images = request.FILES.getlist('images')
        
        if not images:
            return Response({'error': '请选择要上传的图片'}, status=status.HTTP_400_BAD_REQUEST)
        
        uploaded_images = []
        for idx, image in enumerate(images):
            shoe_image = ShoeImage.objects.create(
                shoe=shoe,
                image=image,
                alt_text=request.data.get('alt_text', f'{shoe} 图片 {idx+1}'),
                order=idx
            )
            uploaded_images.append(ShoeImageSerializer(shoe_image, context={'request': request}).data)
        
        return Response({
            'message': f'成功上传 {len(uploaded_images)} 张图片',
            'images': uploaded_images
        })

    @action(detail=True, methods=['delete'])
    def delete_image(self, request, pk=None):
        """删除指定图片"""
        shoe = self.get_object()
        image_id = request.data.get('image_id')
        
        try:
            image = ShoeImage.objects.get(id=image_id, shoe=shoe)
            image.delete()
            return Response({'message': '图片删除成功'})
        except ShoeImage.DoesNotExist:
            return Response({'error': '图片不存在'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['get'])
    def search(self, request):
        """高级搜索"""
        queryset = self.get_queryset()
        
        # 关键词搜索
        q = request.query_params.get('q')
        if q:
            queryset = queryset.filter(
                Q(model__icontains=q) |
                Q(colorway__icontains=q) |
                Q(brand__name__icontains=q) |
                Q(description__icontains=q)
            )
        
        # 价格范围
        min_price = request.query_params.get('min_price')
        max_price = request.query_params.get('max_price')
        if min_price:
            queryset = queryset.filter(retail_price__gte=min_price)
        if max_price:
            queryset = queryset.filter(retail_price__lte=max_price)
        
        # 年份范围
        start_year = request.query_params.get('start_year')
        end_year = request.query_params.get('end_year')
        if start_year:
            queryset = queryset.filter(release_year__gte=start_year)
        if end_year:
            queryset = queryset.filter(release_year__lte=end_year)
        
        # 分页
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)