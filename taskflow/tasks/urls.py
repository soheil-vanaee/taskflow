from django.urls import path
from . import views

urlpatterns = [
    path('', views.TaskListView.as_view(), name='task-list'),
    path('<int:pk>/', views.TaskDetailView.as_view(), name='task-detail'),
    path('<int:task_id>/status/', views.update_task_status, name='update-task-status'),
    path('<int:task_id>/assign/', views.assign_task, name='assign-task'),
    path('<int:task_id>/add-dependency/', views.add_dependency, name='add-dependency'),
]