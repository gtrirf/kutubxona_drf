from django.contrib import admin
from . import models


@admin.register(models.Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'isbn', 'author', 'category', 'realize_date')
    search_fields = ('title', 'isbn', 'author__first_name', 'author__last_name')


@admin.register(models.Rental)
class RentalAdmin(admin.ModelAdmin):
    list_display = ('book', 'user', 'rental_date', 'return_due_date', 'is_returned')
    list_filter = ('is_returned',)


@admin.register(models.Queue)
class QueueAdmin(admin.ModelAdmin):
    list_display = ('book', 'user', 'request_date')

@admin.register(models.Comment)
class CommentBookAdmin(admin.ModelAdmin):
    list_display = ('book', 'user', 'created_at', 'updated_at')

admin.site.register(models.Tili)
admin.site.register(models.Yozuvi)
admin.site.register(models.Category)
admin.site.register(models.Author)
