from django.urls import path
from .views import *

urlpatterns = [

    #Project Management URLs
    path('create/', create_project, name='create_project'),
    path('<slug:slug>/edit/', edit_project, name='edit_project'),
    path('<slug:slug>/delete/', delete_project, name='delete_project'),

    #Part Management URLs
    path('<slug:slug>/add-part/', add_part, name='add_part'),
    path('part/<int:part_id>/edit/', edit_part, name='edit_part'),
    path('part/<int:part_id>/delete/', delete_part, name='delete_part'),
    
    #Task Management URLs
    path('part/<int:part_id>/add-task/', add_task, name='add_task'),
    path('task/<int:task_id>/edit/', edit_task, name='edit_task'),
    path('task/<int:task_id>/delete/', delete_task, name='delete_task'),

    #Invitation Management URLs
    path('project/<slug:slug>/invite/', invite_to_project, name='invite_to_project'),
    path('invitations/', received_invitations, name='received_invitations'),
    path('invitations/<int:invitation_id>/accept/', accept_invitation, name='accept_invitation'),

    path('<slug:slug>/manage_members/', manage_members, name='manage_members'),
    path('<slug:slug>/remove_member/<int:user_id>/', remove_member, name='remove_member'),
    path('<slug:slug>/add_member/', add_member, name='add_member'),

    path('<slug:slug>/project_detail/', project_detail, name='project_detail')

]
