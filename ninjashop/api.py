from ninja import NinjaAPI, Schema
from pydantic import EmailStr
from .models import Category, Product, Wishlist, Order, OrderItem, Status
from ninja import UploadedFile, File
from django.shortcuts import get_object_or_404
from typing import List
from django.contrib.auth import authenticate
from ninja.security import HttpBasicAuth
from ninja.errors import HttpError, AuthenticationError
from django.contrib.auth.models import User
from ninja import Query
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import permission_required
from django.http import HttpResponse


class BasicAuth(HttpBasicAuth):
    def authenticate(self, request, username, password):
        user = authenticate(username = username, password = password)
        if user:
            return user
        raise AuthenticationError('Ошибка авторизации!')


api = NinjaAPI(csrf = True, auth = BasicAuth())


@api.exception_handler(PermissionDenied)
def permission_error(request, e):
    return HttpResponse('У вас недостаточно прав для совершения данной операции!', status = 403)
    

@api.get('/basic', auth = BasicAuth(), summary = 'Авторизация')
def authentication(request):
    return { 'Сообщение': 'Пользователь авторизован!', 'Логин пользователя': request.auth.username }


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


class UserAuth(Schema):
    username: str
    password: str


class UserRegistration(Schema):
    username: str
    last_name: str
    first_name: str
    email: EmailStr
    password1: str
    password2: str
    

class UserOut(Schema):
    username: str
    last_name: str
    first_name: str
    email: str
    is_active: bool


class WishlistIn(Schema):
    user: int
    product: int
    quantity: int


class WishlistOut(Schema):
    product: ProductOut
    quantity: int


class StatusOut(Schema):
    name: str


class OrderOut(Schema):
    status: StatusOut
    total: float


class OrderIn(Schema):
    user: int
    status: int
    total: float


class OrderItemOut(Schema):
    order: OrderOut
    product: ProductOut
    cost: float
    quantity: int


class OrderItemIn(Schema):
    order: int
    product: int
    cost: float
    quantity: int


@api.get('/categories', response = List[CategoryOut], summary = 'Получить список категорий')
def list_categories(request):
    return Category.objects.all()


@api.get('/products', response = List[ProductOut], summary = 'Получить список товаров')
def list_products(request):
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


@api.post('/categories', response = CategoryOut, summary = 'Добавить категорию')
@permission_required('auth.add_Категория', raise_exception = True)
def create_category(request, payload: CategoryIn):
    category = Category.objects.create(**payload.dict())
    return category


@api.post('/products', response = ProductOut, summary = 'Добавить товар')
@permission_required('auth.add_Товар', raise_exception = True)
def create_product(request, payload: ProductIn, image: UploadedFile = File(...)):
    payload_dict = payload.dict()
    category = get_object_or_404(Category, slug = payload_dict.pop('category'))
    product = Product(**payload_dict, category = category)
    product.image.save(image.name, image) 
    return product


@api.put('/products/{product_id}', response = ProductOut, summary = 'Изменить информацию о товаре')
@permission_required('auth.change_Товар', raise_exception = True)
def update_product(request, product_id: int, payload: ProductIn):
    product = get_object_or_404(Product, id = product_id)
    for attribute, value in payload.dict().items():
        if attribute == 'category':
            category = get_object_or_404(Category, slug = value)
            setattr(product, attribute, category)
        else:
            setattr(product, attribute, value)
    product.save()
    return product


@api.delete('/categories/{category_slug}', summary = 'Удалить категорию')
@permission_required('auth.delete_Категория', raise_exception = True)
def delete_category(request, category_slug: str):
    category = get_object_or_404(Category, slug = category_slug)
    category.delete()
    return { 'Успешно!': 'Категория была удалена!' }


@api.delete('/products/{product_id}', summary = 'Удалить товар')
@permission_required('auth.delete_Товар', raise_exception = True)
def delete_product(request, product_id: int):
    product = get_object_or_404(Product, id = product_id)
    product.delete()
    return { 'Успешно!': 'Товар был удален!' }


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
    return { 'Успешно!': 'Пользователь зарегистрирован!', 'Логин пользователя': user.username }


@api.get('/users', response = List[UserOut], summary = 'Просмотр информации о пользователях')
@permission_required('auth.view_user', raise_exception = True)
def users(request):    
    return User.objects.all()
    

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


@api.get('/wishlist/{user_id}/', response = List[WishlistOut], summary = 'Получить лист желаний пользователя')
def get_wishlist(request, user_id: int):
    user = get_object_or_404(User, id = user_id)
    wishlist = Wishlist.objects.filter(user = user)
    return wishlist


@api.post('/wishlist', response = WishlistOut, summary = 'Добавить лист желаний')
def create_wishlist(request, payload: WishlistIn):
    payload_dict = payload.dict()
    user = get_object_or_404(User, id = payload_dict.pop('user'))
    product = get_object_or_404(Product, id = payload_dict.pop('product'))

    if Wishlist.objects.filter(user = user, product = product).exists():
        wishlist = get_object_or_404(Wishlist, user = user, product = product)
        wishlist.quantity = payload_dict.pop('quantity')
    else:
        wishlist = Wishlist(**payload_dict, user = user, product = product)    

    wishlist.save()
    return wishlist


@api.put('/wishlist_add', response = WishlistOut, summary = 'Добавить единицу товара в лист желаний')
def add_to_wishlist(request, wishlist_id: int):
    wishlist = get_object_or_404(Wishlist, id = wishlist_id)
    wishlist.quantity += 1
    wishlist.save()
    return wishlist


@api.put('/wishlist_remove', response = WishlistOut, summary = 'Удалить единицу товара из листа желаний')
def remove_from_wishlist(request, wishlist_id: int):
    wishlist = get_object_or_404(Wishlist, id = wishlist_id)
    wishlist.quantity -= 1

    if wishlist.quantity == 0:
        wishlist.delete()
    else:
        wishlist.save()

    return wishlist


@api.get('/orders', response = List[OrderItemOut], summary = 'Получить список всех заказов')
@permission_required('auth.view_Позиция_заказа', raise_exception = True)
def list_orders(request):
    return OrderItem.objects.all()


@api.get('/order/{user_id}/', response = List[OrderItemOut], summary = 'Получить список заказов пользователя')
def get_user_orders(request, user_id: int):
    try:
        user = get_object_or_404(User, id = user_id)
        order = get_object_or_404(Order, user = user)
        order_items = OrderItem.objects.filter(order = order)
        return order_items
    except: 
        raise HttpError(404, 'Произошла ошибка!')


@api.post('/order', response = OrderOut, summary = 'Добавить заказ')
def create_order(request, wishlists: List[int]):
    '''Получаю список id листов желаний, которые будут включены в заказ'''
    status = get_object_or_404(Status, id = 1)
    wishlist = get_object_or_404(Wishlist, id = wishlists[0])
    order = Order(user = wishlist.user, status = status, total = 0)   
    order.save()
    '''Прохожусь по всем id и собираю их в элементы заказа'''
    for item in wishlists:
        wishlist = get_object_or_404(Wishlist, id = item)
        OrderItem.objects.create(
            order = order,
            product = wishlist.product,
            quantity = wishlist.quantity,
            cost = wishlist.product.price * wishlist.quantity
        )
    
    order.total += order.get_total_amount()  
    order.save()

    return order


@api.put('/change_status', response = OrderOut, summary = 'Изменить статус заказа')
@permission_required('auth.change_Заказ', raise_exception = True)
def change_status(request, order_id: int, status_id: int):
    order = get_object_or_404(Order, id = order_id)
    status = get_object_or_404(Status, id = status_id)
    order.status = status
    order.save()
    return order