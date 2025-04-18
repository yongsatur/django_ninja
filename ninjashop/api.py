from ninja import NinjaAPI, Schema
from pydantic import EmailStr
from .models import Category, Product
from ninja import UploadedFile, File
from django.shortcuts import get_object_or_404
from typing import List
from django.contrib.auth import authenticate, login, logout
from ninja.errors import HttpError, AuthenticationError
from django.contrib.auth.models import User
from ninja import Query


api = NinjaAPI(csrf = True)


class CategoryIn(Schema):
    name: str
    slug: str


class CategoryOut(Schema):
    id: int
    name: str
    slug: str


class ProductIn(Schema):
    name: str
    slug: str
    category: str
    description: str
    price: float 


class ProductOut(Schema):
    id: int
    name: str
    slug: str
    category: CategoryOut
    description: str
    price: float 


class UserAuthentication(Schema):
    username: str
    password: str


class UserRegistration(Schema):
    username: str
    last_name: str
    first_name: str
    email: EmailStr
    password1: str
    password2: str
    

class UserList(Schema):
    username: str
    last_name: str
    first_name: str
    email: str
    is_active: bool


@api.get('/categories', response = List[CategoryOut], summary = 'Получить список категорий')
def list_categories(request):
    return Category.objects.all()


@api.get('/products', response = List[ProductOut], summary = 'Получить список товаров')
def list_product(request):
    return Product.objects.all()


@api.get('/categories/{category_slug}', response = CategoryOut, summary = 'Получить категорию по slug')
def get_category(request, category_slug: str):
    return get_object_or_404(Category, slug = category_slug)


@api.get('/products/{product_id}', response = ProductOut, summary = 'Получить товар по id')
def get_product(request, product_id: int):
    return get_object_or_404(Product, id = product_id)


@api.get('/products/{category_slug}/', response = List[ProductOut], summary = 'Получить список товаров по категории')
def get_products_of_category(request, category_slug: str):
    category = get_object_or_404(Category, slug = category_slug)
    products = Product.objects.filter(category = category)
    return products


@api.post('/categories', summary = 'Добавить категорию')
def create_category(request, payload: CategoryIn):
    category = Category.objects.create(**payload.dict())
    return {'name': category.name, 'slug': category.slug}


@api.post('/products', summary = 'Добавить товар')
def create_product(request, payload: ProductIn, image: UploadedFile = File(...)):
    payload_dict = payload.dict()
    category = get_object_or_404(Category, slug = payload_dict.pop('category'))
    product = Product(**payload_dict, category = category)
    product.image.save(image.name, image) 
    return {
        'id': product.id,
        'category': product.category.name, 
        'name': product.name, 
        'slug': product.slug, 
        'price': product.price, 
        'description': product.description
    }


@api.put('/products/{product_id}', summary = 'Изменить информацию о товаре')
def update_product(request, product_id: int, payload: ProductIn):
    product = get_object_or_404(Product, id = product_id)
    for attribute, value in payload.dict().items():
        if attribute == 'category':
            category = get_object_or_404(Category, slug = value)
            setattr(product, attribute, category)
        else:
            setattr(product, attribute, value)
    product.save()
    return {
        'success': True, 
        'id': product.id,
        'category': product.category.name, 
        'name': product.name, 
        'slug': product.slug, 
        'price': product.price, 
        'description': product.description
    }


@api.delete('/categories/{category_slug}', summary = 'Удалить категорию')
def delete_category(request, category_slug: str):
    category = get_object_or_404(Category, slug = category_slug)
    category.delete()
    return {'success': True}


@api.delete('/products/{product_id}', summary = 'Удалить товар')
def delete_product(request, product_id: str):
    product = get_object_or_404(Product, id = product_id)
    product.delete()
    return {'success': True}


@api.get('/account', summary = 'Проверка авторизации пользователя')
def account(request):
    if not request.user.is_authenticated:
        raise HttpError(401, 'Пользователь не авторизован!')
    return { 'Авторизованный пользователь': request.user.username }


@api.post('/login', summary = 'Авторизация пользователя')
def login_user(request, payload: UserAuthentication):
    user = authenticate(username = payload.username, password = payload.password)
    if user is not None:
        login(request, user)
        return {'Статус': 'Авторизация успешна!', 'Пользователь': user.username}
    raise AuthenticationError('Ошибка авторизации!')


@api.post('/registration', summary = 'Регистрация пользователя')
def registration_user(request, payload: UserRegistration):
    if User.objects.filter(username = payload.username).exists():
        raise HttpError(400, 'Пользователь с таким именем уже существует!')
    
    user = User.objects.create_user(
        username = payload.username,
        last_name = payload.last_name,
        first_name = payload.first_name,
        email = payload.email,
        password = payload.password1
    )
    login(request, user)
    
    return { 'Сообщение': 'Пользователь успешно зарегистрирован!' }


@api.post('/logout', auth = None, summary = 'Выйти из аккаунта')
def logout_user(request):
    logout(request)
    return {'Сообщение': 'Вы вышли из аккаунта!'}


@api.get('/users', response = List[UserList], summary = 'Просмотр информации о пользователях')
def users(request):
    account(request)
    
    if request.user.has_perm('auth.view_user'):
        return User.objects.all()
    else:
        raise HttpError(403, 'У вас недостаточно прав для просмотра информации!')
    

@api.get('/products_sort', response = List[ProductOut], summary = 'Сортировка товаров по цене')
def products_sort(request, sort: str = Query(None, description = 'Введите asc или desc')):
    queryset = Product.objects.all()
    if sort == 'asc':
        queryset = queryset.order_by('price')
    elif sort == 'desc':
        queryset = queryset.order_by('-price')
    return queryset


@api.get('/products_name_search', response = List[ProductOut], summary = 'Поиск товара по названию')
def search_product_name(request, search: str = Query(None, description = 'Строка поиска')):
    return Product.objects.filter(name__icontains = search)


@api.get('/products_desc_search', response = List[ProductOut], summary = 'Поиск товара по описанию')
def search_product_desc(request, search: str = Query(None, description = 'Строка поиска')):
    return Product.objects.filter(description__icontains = search)