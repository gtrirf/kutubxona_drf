from django.db import models
from django.utils import timezone
from users.models import CustomUser
import openpyxl
from openpyxl.styles import Font


class Category(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name="Category Name")

    class Meta:
        db_table = 'category'
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class Author(models.Model):
    first_name = models.CharField(max_length=255, verbose_name="First Name")
    last_name = models.CharField(max_length=255, verbose_name="Last Name")
    nickname = models.CharField(max_length=255, verbose_name='Nick Name', null=True, blank=True)

    class Meta:
        db_table = 'author'
        verbose_name = "Author"
        verbose_name_plural = "Authors"

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class Yozuvi(models.Model):
    name_yozuv = models.CharField(max_length=30)

    class Meta:
        db_table = 'yozuvi'
        verbose_name = 'Yozuvi'
        verbose_name_plural = 'Yozuvlar'

    def __str__(self):
        return self.name_yozuv


class Tili(models.Model):
    til = models.CharField(max_length=30)

    class Meta:
        db_table = 'til'
        verbose_name = 'Til'
        verbose_name_plural = 'Tillar'

    def __str__(self):
        return self.til


class Book(models.Model):
    title = models.CharField(max_length=255, verbose_name="Book Title")
    yozuvi = models.ForeignKey(Yozuvi, on_delete=models.SET_NULL, related_name='books', verbose_name='Yozuvi', null=True, blank=True)
    tili = models.ForeignKey(Tili, on_delete=models.SET_NULL, related_name='books', verbose_name='Tili', null=True, blank=True)
    pages = models.IntegerField()
    nashriyot = models.CharField(null=True, blank=True, max_length=255)
    description = models.TextField(verbose_name="Description")
    isbn = models.CharField(max_length=13, unique=True, verbose_name="ISBN")
    author = models.ForeignKey(Author, on_delete=models.SET_NULL, related_name='books', verbose_name="Author", null=True, blank=True)
    realize_date = models.DateField(null=True, blank=True, verbose_name="Realize Date")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, related_name='books', verbose_name="Category", null=True, blank=True)
    image = models.ImageField(
        upload_to='books_img/',
        blank=True,
        null=True,
        default='default_img/default_img_book.jpg',
        verbose_name="Book Image"
    )
    book_pdf = models.FileField(upload_to='pdf_files/', null=True, blank=True)
    quantity = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")

    class Meta:
        db_table = 'book'
        verbose_name = "Book"
        verbose_name_plural = "Books"
        indexes = [
            models.Index(fields=['isbn']),
            models.Index(fields=['title']),
        ]

    def __str__(self):
        return f'{self.title} - {self.isbn}'



class Comment(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    comment = models.TextField()
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'commentBook'

    def __str__(self):
        return f'{self.book} - {self.user}'


class Rental(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='rentals')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    rental_date = models.DateTimeField(auto_now_add=True)
    return_due_date = models.DateTimeField()
    return_date = models.DateTimeField(null=True, blank=True)
    is_returned = models.BooleanField(default=False)

    class Meta:
        db_table = 'rental'
        verbose_name = "Rental"
        verbose_name_plural = "Rentals"

    def __str__(self):
        return f'{self.book.title} rented by {self.user}'


class Queue(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='queues')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    request_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'queue'
        verbose_name = "Queue"
        verbose_name_plural = "Queues"

    def __str__(self):
        return f'{self.book.title} queue for {self.user}'

