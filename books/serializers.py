from rest_framework import serializers
from .models import Book, Comment, Rental, Queue
from rest_framework import serializers
from .models import Rental


class QueueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Queue
        fields = ['id', 'book', 'user', 'request_date']


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ['id', 'title', 'yozuvi', 'tili', 'pages', 'nashriyot',
                  'description', 'isbn', 'author', 'realize_date', 'category',
                  'image', 'book_pdf', 'quantity', 'created_at', 'updated_at'
                  ]


class CommentBookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'book', 'comment', 'user', 'created_at', 'updated_at']
        read_only_fields = ['id','user', 'book', 'created_at', 'updated_at']


    def validate(self, data):
        if not data.get('comment'):
            raise serializers.ValidationError("Comment cannot be empty.")
        return data


class RentalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rental
        fields = '__all__'
        read_only_fields = ('user', 'rental_date', 'is_returned')
