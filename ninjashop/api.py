from ninja import NinjaAPI, Schema
from .models import Category, Product
from ninja import UploadedFile, File
from django.shortcuts import get_object_or_404
from typing import List


api = NinjaAPI()


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