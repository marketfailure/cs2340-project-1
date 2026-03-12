from django.urls import path
from . import views

urlpatterns = [
    path('<str:username>/', views.profile_view, name='profile_view'),
    path('edit/me/', views.profile_edit_me, name='profile_edit'),
    path('edit/skills/', views.skills_edit, name='skills_edit'),
    path('edit/skills/delete/<int:skill_id>/', views.skill_delete, name='skill_delete'),
    path('edit/education/', views.education_edit, name='education_edit'),
    path('edit/education/delete/<int:edu_id>/', views.education_delete, name='education_delete'),
    path('edit/work/', views.work_edit, name='work_edit'),
    path('edit/work/delete/<int:work_id>/', views.work_delete, name='work_delete'),
    path('edit/links/', views.links_edit, name='links_edit'),
    path('edit/links/delete/<int:link_id>/', views.link_delete, name='link_delete'),
    path('view/me/', views.me, name='me')
]
