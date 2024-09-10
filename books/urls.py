from django.urls import path
from .import views


urlpatterns = [
    # Book detail and list
    path('books/<int:pk>/', views.BookDetailView.as_view(), name='book_detail'),
    path('books/', views.BookListView.as_view(), name='book_list'),
    # download pdf file
    path('books/<int:pk>/download/', views.BookPdfDownloadView.as_view(), name='book_pdf_download'),
    # Add comment, update, delete
    path('books/<int:pk>/comments/<int:comment_id>/update/', views.CommentUpdateView.as_view(), name='comment_update'),
    path('books/<int:pk>/comments/<int:comment_id>/delete/', views.CommentDeleteView.as_view(), name='comment_delete'),
    path('books/<int:pk>/comments/', views.CommentCreateView.as_view(), name='comment_create'),
    # Rent book
    path('books/<int:pk>/rentals/', views.RentalCreateView.as_view(), name='create-rental'),
    path('books/<int:pk>/rentals/<int:rental_id>/return/', views.RentalReturnView.as_view(), name='return-rental'),
    # Queue Book
    path('books/<int:book_id>/request/', views.RequestBookView.as_view(), name='request_book'),
    path('books/<int:book_id>/queue/', views.QueueListView.as_view(), name='queue_list'),
    path('books/<int:book_id>/process_queue/', views.ProcessQueueView.as_view(), name='process_queue'),
    # Download excel file, book detail docx, book detail pdf
    path('download-excel/', views.DownloadExcelFileView.as_view(), name='download-excel'),
    path('download-book-docx/<int:book_id>/', views.download_book_docx, name='download-book-docx'),
    path('download-book-pdf/<int:book_id>/', views.download_book_pdf, name='download-book-pdf'),
]
