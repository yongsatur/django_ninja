from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


class Category(models.Model):
    name = models.CharField(verbose_name = 'Наименование', max_length = 250)
    slug = models.SlugField(verbose_name = 'Slug', max_length = 250, unique = True)

    class Meta:
        ordering = ('name', )
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(Category, verbose_name = 'Категория', related_name = 'products', on_delete = models.CASCADE)
    name = models.CharField(verbose_name = 'Наименование', max_length = 250)
    slug = models.SlugField(verbose_name = 'Slug', max_length = 250)
    price = models.DecimalField(verbose_name = 'Цена', max_digits = 10, decimal_places = 2)
    description = models.TextField(verbose_name = 'Описание', blank = True, null = True)
    image = models.ImageField(verbose_name = 'Изображение', upload_to = 'images/', blank = True, null = True)

    class Meta:
        ordering = ('name', )
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'

    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('product_detail', kwargs = {'id': self.id, 'slug': self.slug})


class Wishlist(models.Model):
    user = models.ForeignKey(User, verbose_name = 'Пользователь', related_name = 'lists', on_delete = models.CASCADE, null=True)
    product = models.ForeignKey(Product, verbose_name = 'Товар', on_delete = models.CASCADE, null=True)
    quantity = models.PositiveBigIntegerField(verbose_name = 'Количество', default = 1)

    class Meta:
        verbose_name = 'Лист желаний'
        verbose_name_plural = 'Листы желаний'
        constraints = [
            models.UniqueConstraint(fields = ['user', 'product'], name = 'user_product')
        ] 

    def __str__(self):
        return self.user.username + ' - ' + self.product.name + ' - ' + str(self.quantity)


class Status(models.Model):
    name = models.CharField(verbose_name = 'Наименование', max_length = 250)

    class Meta:
        verbose_name = 'Статус'
        verbose_name_plural = 'Статусы'

    def __str__(self):
        return self.name


class Order(models.Model):
    user = models.ForeignKey(User, verbose_name = 'Пользователь', related_name = 'orders', on_delete = models.CASCADE)
    status = models.ForeignKey(Status, verbose_name = 'Статус', on_delete = models.CASCADE)
    total = models.DecimalField(verbose_name = 'Итоговая стоимость', max_digits = 10, decimal_places = 2)
    created_at = models.DateTimeField(verbose_name = 'Дата создания', auto_now_add = True)

    class Meta:
        ordering = ('created_at', )
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    def get_total_amount(self):
        return sum(item.get_amount() for item in self.order_items.all())


class OrderItem(models.Model):
    order = models.ForeignKey(Order, verbose_name = 'Заказ', related_name = 'order_items', on_delete = models.CASCADE)
    product = models.ForeignKey(Product, verbose_name = 'Продукт', on_delete = models.CASCADE)
    cost = models.DecimalField(verbose_name = 'Стоимость', max_digits = 10, decimal_places = 2)
    quantity = models.PositiveBigIntegerField(verbose_name = 'Количество', default = 1)

    class Meta:
        verbose_name = 'Позиция заказа'
        verbose_name_plural = 'Позиции заказа'

    def get_amount(self):
        self.cost = self.product.price * self.quantity
        return self.cost