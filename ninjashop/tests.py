from .api import *
from .models import *
from django.test import TestCase
from django.contrib.auth.models import User


class CategoryTest(TestCase):
    fixtures = ['data.json']

    def test_str(self):
        category = Category(
            name = 'Category name',
            slug = 'category-name',
        )
        self.assertEqual(str(category), 'Category name')

    def test_get_categories(self):
        response = self.client.get('/api/categories')
        self.assertEqual(response.status_code, 200)

    def test_categories(self):
        payload = {
            'name': 'test 1',
            'slug': 'test-1',
        }
        response = self.client.post('/api/categories', content_type = 'application/json', data = payload)
        self.assertEqual(response.status_code, 200)

    def test_delete_category(self):
        category_slug = 'televizory'
        response = self.client.delete(f'/api/categories/{ category_slug }')
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(response.json(), { 'Успешно!': 'Категория была удалена!' })

    def test_get_category(self):
        category_slug = 'televizory'
        response = self.client.get(f'/api/categories/{ category_slug }')
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(response.json(), { 'id': 1, 'name': 'Телевизоры', 'slug': 'televizory' })

    def test_not_get_category(self):
        category_slug = 'noexist'
        response = self.client.get(f'/api/categories/{ category_slug }')
        self.assertEqual(response.status_code, 404)


class ProductTest(TestCase):
    fixtures = ['data.json']

    def test_str(self):
        category = Category(name = 'Category name', slug = 'category-name')
        product = Product(
            category = category,
            name = 'Product name 1',
            slug = 'product-name-1',
            description = 'Description of product name 1',
            price = 15000,
        )
        self.assertEqual(str(product), 'Product name 1')

    def test_delete_product(self):
        product_id = 1
        response = self.client.delete(f'/api/products/{ product_id }')
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(response.json(), { 'Успешно!': 'Товар был удален!' })

    def test_get_products(self):
        response = self.client.get('/api/products')
        self.assertEqual(response.status_code, 200)

    def test_get_product_by_id(self):
        product_id = 1
        response = self.client.get(f'/api/products/{ product_id }')
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(response.json(), { 
            'id': 1,
            'name': 'Samsung A51',
            'slug': 'samsung-a51',
            'category': { 'id': 2, 'name': 'Телефоны', 'slug': 'telefony' },
            'description': '',
            'price': 30000.00
        })

    def test_not_get_product_by_id(self):
        product_id = 7
        response = self.client.get(f'/api/products/{ product_id }')
        self.assertEqual(response.status_code, 404)

    def test_get_products_of_category(self):
        category_slug = 'televizory'
        response = self.client.get(f'/api/products/{ category_slug }/')
        self.assertEqual(response.status_code, 200)

    def test_not_get_products_of_category(self):
        category_slug = 'noexist'
        response = self.client.get(f'/api/products/{ category_slug }/')
        self.assertEqual(response.status_code, 404)

    def test_products_sort(self):
        min_price = 10000
        max_price = 50000
        response = self.client.get(f'/api/products?min_price={ min_price }&max_price={ max_price }')
        self.assertEqual(response.status_code, 200)

    def test_products_name_search(self):
        search = 'sam'
        response = self.client.get(f'/api/products_name_search?search={ search }')
        self.assertEqual(response.status_code, 200)


class WishlistTest(TestCase):
    fixtures = ['data.json']
    
    def test_str(self):
        user = User.objects.get(username = 'user2')
        product = Product.objects.get(name = 'Samsung TV10')
        wishlist = Wishlist(
            user = user,
            product = product,
            quantity = 1,
        )
        self.assertEqual(str(wishlist), 'user2 - Samsung TV10 - 1')

    def test_get_wishlist(self):
        user_id = 3
        response = self.client.get(f'/api/wishlist/{ user_id }/')
        self.assertEqual(response.status_code, 200)

    def test_not_get_wishlist(self):
        user_id = 7
        response = self.client.get(f'/api/wishlist/{ user_id }/')
        self.assertEqual(response.status_code, 404)

    def test_wishlist(self):
        payload = {
            'user': '2',
            'product': '2',
            'quantity': '1'
        }
        response = self.client.post('/api/wishlist', content_type = 'application/json', data = payload)
        self.assertEqual(response.status_code, 200)

    def test_wishlist_add(self):
        wishlist_id = 1
        response = self.client.put(f'/api/wishlist_add?wishlist_id={ wishlist_id }')
        self.assertEqual(response.status_code, 200)

    def test_wishlist_remove(self):
        wishlist_id = 1
        response = self.client.put(f'/api/wishlist_remove?wishlist_id={ wishlist_id }')
        self.assertEqual(response.status_code, 200)


class OrderTest(TestCase):
    fixtures = ['data.json']

    def test_get_orders(self):
        response = self.client.get('/api/orders')
        self.assertEqual(response.status_code, 200)

    def test_get_order(self):
        user_id = 3
        response = self.client.get(f'/api/order/{ user_id }', follow = True)
        self.assertEqual(response.status_code, 200)

    def test_not_get_order(self):
        user_id = 7
        response = self.client.get(f'/api/order/{ user_id }', follow = True)
        self.assertEqual(response.status_code, 404)

    def test_change_status(self):
        order_id = 1
        status_id = 2
        response = self.client.put(f'/api/change_status?order_id={ order_id }&status_id={ status_id }')
        self.assertEqual(response.status_code, 200)


class RegisterTest(TestCase):
    fixtures = ['data.json']
    payload = {
        'username': 'test',
        'last_name': 'something',
        'first_name': 'something',
        'email': 'test@test.ru',
        'password1': 'dfvgbh16',
        'password2': 'dfvgbh16'
    }

    def test_registration(self):
        response = self.client.post('/api/registration', content_type = 'application/json',  data = self.payload)
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(response.json(), { 'Успешно!': 'Пользователь зарегистрирован!', 'Логин пользователя': 'test' })


class LoginTest(TestCase):
    fixtures = ['data.json']
    payload = {
        'username': 'admin',
        'password': 'admin',
    }

    def test_login(self):
        response = self.client.post('/api/login', content_type = 'application/json', data = self.payload, follow = True)
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(response.json(), { 'Успешно!': 'Пользователь авторизован!', 'Логин пользователя': 'admin' })

    def test_logout(self):
        response = self.client.post('/api/login', content_type = 'application/json', data = self.payload)
        response = self.client.post('/api/logout')
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(response.json(), {'Успешно!': 'Вы вышли из аккаунта!'})

    def test_get_users(self):
        self.client.post('/api/login', content_type = 'application/json', data = self.payload)
        response = self.client.get('/api/users')
        self.assertEqual(response.status_code, 200)

    def test_get_users_no_permissions(self):
        payload = {
            'username': 'user1',
            'password': 'dfvgbh16',
        }
        self.client.post('/api/login', content_type = 'application/json', data = payload)
        response = self.client.get('/api/users')
        self.assertEqual(response.status_code, 403)