from django.db import models
from django.urls import reverse


class Category(models.Model):
    name = models.CharField(verbose_name = 'Наименование', max_length = 250)
    slug = models.SlugField(verbose_name = 'Slug', max_length = 250, unique = True)

    class Meta:
        ordering = ('name',)
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
        ordering = ('name',)
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'

    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('product_detail', kwargs = {'id': self.id, 'slug': self.slug})