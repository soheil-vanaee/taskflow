from django.urls import path
from . import views

urlpatterns = [
    path('', views.ProjectListView.as_view(), name='project-list'),
    path('<int:pk>/', views.ProjectDetailView.as_view(), name='project-detail'),
    path('<int:project_id>/add-member/', views.add_member_to_project, name='add-member'),
    path('<int:project_id>/remove-member/', views.remove_member_from_project, name='remove-member'),
]