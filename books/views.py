from rest_framework import status
from django.shortcuts import get_object_or_404
from django.http import FileResponse, Http404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .models import Book, Queue
from .serializers import QueueSerializer, BookSerializer, CommentBookSerializer
from .models import Comment
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .models import Book, Rental
from .serializers import RentalSerializer
from django.utils import timezone
from django.http import HttpResponse
import os
import openpyxl
from openpyxl.styles import Font
from io import BytesIO
from .utils import create_book_template


class BookDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            book = Book.objects.get(pk=pk)
            comments = Comment.objects.filter(book=book)
            book_serializer = BookSerializer(book)
            comment_serializer = CommentBookSerializer(comments, many=True)

            return Response({
                'book': book_serializer.data,
                'comments': comment_serializer.data
            }, status=status.HTTP_200_OK)
        except Book.DoesNotExist:
            return Response({'error': 'Kitob topilmadi'}, status=status.HTTP_404_NOT_FOUND)


class CommentCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            book = Book.objects.get(pk=pk)
            serializer = CommentBookSerializer(data=request.data)
            if serializer.is_valid():
                serializer.validated_data['book'] = book
                serializer.validated_data['user'] = request.user
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Book.DoesNotExist:
            return Response({'error': 'Kitob topilmadi'}, status=status.HTTP_404_NOT_FOUND)


class CommentUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, pk, comment_id):
        try:
            comment = Comment.objects.get(pk=comment_id, book_id=pk, user=request.user)
            serializer = CommentBookSerializer(comment, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Comment.DoesNotExist:
            return Response({'error': 'izoh topilmadi yoki mumkin emas'}, status=status.HTTP_404_NOT_FOUND)


class CommentDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk, comment_id):
        try:
            comment = Comment.objects.get(pk=comment_id, book_id=pk, user=request.user)
            comment.delete()
            return Response({'message': 'Izoh o\'chirilindi'}, status=status.HTTP_204_NO_CONTENT)
        except Comment.DoesNotExist:
            return Response({'error': 'Izoh topilmadi yoki mumkin emas'}, status=status.HTTP_404_NOT_FOUND)

class BookListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        books = Book.objects.all()
        serializers = BookSerializer(books, many=True)
        return Response(serializers.data, status=status.HTTP_200_OK)


class BookPdfDownloadView(APIView):
    def get(self, request, pk, *args, **kwargs):
        book = get_object_or_404(Book, pk=pk)
        if book.book_pdf:
            response = FileResponse(book.book_pdf, as_attachment=True)
            response['Content-Disposition'] = f'attachment; filename="{book.title}.pdf"'
            return response
        else:
            raise Http404("PDF fayl mavjud emas")


class RequestBookView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, book_id, *args, **kwargs):
        user = request.user
        book = Book.objects.get(id=book_id)
        if Queue.objects.filter(book=book, user=user).exists():
            return Response({'detail': 'Siz bu kitob uchun allaqachon navbatdasiz'}, status=status.HTTP_400_BAD_REQUEST)
        queue_entry = Queue.objects.create(book=book, user=user)
        return Response({'detail': 'Siz bu kitobga navbatga yozildingiz'}, status=status.HTTP_201_CREATED)


class QueueListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, book_id, *args, **kwargs):
        book = Book.objects.get(id=book_id)
        queues = Queue.objects.filter(book=book).order_by('request_date')
        serializer = QueueSerializer(queues, many=True)

        user_queue_count = None
        for position, queue in enumerate(queues, start=1):
            if queue.user == request.user:
                user_queue_count = position
                break
            else:
                user_queue_count = None

        return Response({
            'queue':serializer.data,
            'user_queue_count':user_queue_count
        })



class ProcessQueueView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, book_id, *args, **kwargs):
        book = Book.objects.get(id=book_id)
        queue = Queue.objects.filter(book=book).order_by('request_date').first()

        if queue:
            user = queue.user
            queue.delete()
            return Response({'detail': 'Queue processed and user notified.'}, status=status.HTTP_200_OK)

        return Response({'detail': 'Queue is empty.'}, status=status.HTTP_404_NOT_FOUND)


class RentalCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            book = Book.objects.get(pk=pk)
            if book.quantity <= 0:
                return Response({'error': 'Ijaraga berishga kitoblar qolmagan'}, status=status.HTTP_400_BAD_REQUEST)

            serializer = RentalSerializer(data=request.data)
            if serializer.is_valid():
                serializer.validated_data['book'] = book
                serializer.validated_data['user'] = request.user
                serializer.save()

                book.quantity -= 1
                book.save()

                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Book.DoesNotExist:
            return Response({'error': 'Kitob topilmadi'}, status=status.HTTP_404_NOT_FOUND)


class RentalReturnView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, pk, rental_id):
        try:
            rental = Rental.objects.get(pk=rental_id, user=request.user)
            if rental.return_date:
                return Response({'error': 'Book already returned'}, status=status.HTTP_400_BAD_REQUEST)

            rental.return_date = timezone.now()
            rental.is_returned = True
            rental.save()

            book = rental.book
            book.quantity += 1
            book.save()

            next_queue = Queue.objects.filter(book=book).order_by('request_date').first()

            if next_queue:
                next_queue.user.notify('Siz navbatga turgan kitob endi ijaraga mavjud')

                Rental.objects.create(
                    book=book,
                    user=next_queue.user,
                    return_due_date=timezone.now() + timezone.timedelta(days=14)
                )
                next_queue.delete()

            return Response({'message': 'Kitob muvofaaqiyatli qaytarildi'}, status=status.HTTP_200_OK)
        except Rental.DoesNotExist:
            return Response({'error': 'Ijaralar mavjud emas'}, status=status.HTTP_404_NOT_FOUND)


class DownloadExcelFileView(APIView):
    def get(self, request):
        workbook = openpyxl.Workbook()
        sheet = workbook.active
        headers = [
            "Title", "Yozuvi", "Tili", "Pages", "Nashriyot",
            "Description", "ISBN", "Author", "Realize Date",
            "Category", "Quantity", "Created At", "Updated At"
        ]

        sheet.append(headers)

        for cell in sheet["1:1"]:
            cell.font = Font(bold=True)

        books = Book.objects.all()
        for book in books:
            sheet.append([
                book.title,
                book.yozuvi.name_yozuv if book.yozuvi else "",
                book.tili.til if book.tili else "",
                book.pages,
                book.nashriyot,
                book.description,
                book.isbn,
                f'{book.author.first_name} {book.author.last_name}' if book.author else "",
                book.realize_date.strftime("%Y-%m-%d") if book.realize_date else "",
                book.category.name if book.category else "",
                book.quantity,
                book.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                book.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
            ])

        file_buffer = BytesIO()
        workbook.save(file_buffer)
        file_buffer.seek(0)

        response = HttpResponse(
            file_buffer,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="books_data.xlsx"'
        return response

def download_book_docx(request, book_id):
    book = Book.objects.get(id=book_id)
    file_stream = create_book_template(book)
    response = HttpResponse(
        file_stream,
        content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    )
    response['Content-Disposition'] = f'attachment; filename="{book.title.replace(" ", "_")}_details.docx"'
    return response


def download_book_pdf(request, book_id):
    from spire.doc import Document as SpireDocument, FileFormat

    book = Book.objects.get(id=book_id)

    file_stream = create_book_template(book)

    temp_word_file = f'{book.title.replace(" ", "_")}_details.docx'
    with open(temp_word_file, 'wb') as temp_file:
        temp_file.write(file_stream.getvalue())

    document = SpireDocument()
    document.LoadFromFile(temp_word_file)

    temp_pdf_file = f'{book.title.replace(" ", "_")}_details.pdf'
    document.SaveToFile(temp_pdf_file, FileFormat.PDF)

    with open(temp_pdf_file, 'rb') as pdf_file:
        response = HttpResponse(pdf_file.read(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{temp_pdf_file}"'

    os.remove(temp_word_file)
    os.remove(temp_pdf_file)

    return response