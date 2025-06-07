# store
"""
常用管理命令:

# 1. 初始化项目
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser

# 2. 创建测试数据
python manage.py shell

from shoes.models import Brand, Shoe
from django.contrib.auth.models import User

# 创建品牌
nike = Brand.objects.create(
    name="Nike",
    name_en="Nike",
    description="Just Do It"
)

adidas = Brand.objects.create(
    name="Adidas",
    name_en="Adidas",
    description="Impossible is Nothing"
)

# 创建鞋款
user = User.objects.first()
shoe1 = Shoe.objects.create(
    brand=nike,
    model="Air Jordan 1",
    colorway="Bred",
    category="basketball",
    release_year=1985,
    retail_price=1299.00,
    available_sizes=[7, 7.5, 8, 8.5, 9, 9.5, 10, 10.5, 11],
    description="经典篮球鞋，乔丹签名鞋款第一代",
    created_by=user
)

# 3. 运行开发服务器
python manage.py runserver
"""