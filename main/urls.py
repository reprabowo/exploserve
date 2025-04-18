from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .views import fetch_sinta_data, ajax_load_programs

urlpatterns = [
    # Home and Dashboard
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),

    # Profile Views
    path('profile/', views.profile_detail, name='profile_detail'),  # For the logged-in user
    path('profile/<int:user_id>/', views.profile_detail, name='profile_detail'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),

    # User Management (System Owner Only)
    path('users/', views.user_list, name='user_list'),
    path('users/create/', views.create_user, name='create_user'),
    path('users/update/<int:user_id>/', views.update_user, name='update_user'),
    path('users/delete/<int:user_id>/', views.delete_user, name='delete_user'),

    # Institution Public Views (Visible to All Users)
    path('institutions/', views.institution_list, name='institution_list'),
    path('institutions/<int:institution_id>/', views.institution_profile, name='institution_profile'),

    # Institution Management Views (Accessible to System Owner, System Admin, and Institutional Admin)
    path('institutions/manage/', views.institution_manage_list, name='institution_manage_list'),
    path('institutions/create/', views.create_institution, name='create_institution'),
    path('institutions/update/<int:institution_id>/', views.update_institution, name='update_institution'),
    path('institutions/delete/<int:institution_id>/', views.delete_institution, name='delete_institution'),

    # Study Program Management
    path('programs/', views.programstudi_list, name='programstudi_list'),
    path('programs/create/', views.create_programstudi, name='create_programstudi'),
    path('programs/update/<int:program_id>/', views.update_programstudi, name='update_programstudi'),
    path('programs/delete/<int:program_id>/', views.delete_programstudi, name='delete_programstudi'),
    path('programs/<int:program_id>/', views.programstudi_detail, name='programstudi_detail'),

    # Password Change URLs
    path('password_change/', auth_views.PasswordChangeView.as_view(template_name='password_change.html'), name='password_change'),
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(template_name='password_change_done.html'), name='password_change_done'),

    # Password Reset URLs (Forgot Password)
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='password_reset.html'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'), name='password_reset_complete'),

    # Research Grant Management
    path('grants/', views.research_grant_list, name='research_grant_list'),
    path('grants/create/', views.create_research_grant, name='create_research_grant'),
    path('grants/update/<int:grant_id>/', views.update_research_grant, name='update_research_grant'),
    path('grants/delete/<int:grant_id>/', views.delete_research_grant, name='delete_research_grant'),
    path('grants/<int:grant_id>/', views.research_grant_detail, name='research_grant_detail'),

    # Footer Column Management
    path('footer/', views.footer_column_list, name='footer_column_list'),
    path('footer/create/', views.create_footer_column, name='create_footer_column'),
    path('footer/update/<int:column_id>/', views.update_footer_column, name='update_footer_column'),
    path('footer/delete/<int:column_id>/', views.delete_footer_column, name='delete_footer_column'),

    # Search Column Management
    path('search/', views.search, name='search'),

    # Announcement Management URLs
    path('announcements/', views.announcement_list, name='announcement_list'),
    path('announcements/create/', views.create_announcement, name='create_announcement'),
    path('announcements/update/<int:announcement_id>/', views.update_announcement, name='update_announcement'),
    path('announcements/delete/<int:announcement_id>/', views.delete_announcement, name='delete_announcement'),
    path('announcements/<int:announcement_id>/', views.announcement_detail, name='announcement_detail'),

    # Dashboard Announcements (for institution-specific announcements)
    path('announcements/dashboard/', views.dashboard_announcements, name='dashboard_announcements'),
    
    # Public Announcement URL
    path('announcements/public/', views.announcement_public_list, name='announcement_public_list'),

    # Attachment deletion URL
    path('announcements/attachment/delete/<int:file_id>/', views.delete_attachment_file, name='delete_attachment_file'),

    path('test-upload/', views.test_upload, name='test_upload'),

    path("fetch_sinta_data/<int:sinta_id>/", fetch_sinta_data, name="fetch_sinta_data"),

    path('users/public/', views.user_list_public, name='user_list_public'),

    path('ajax/load-programs/', views.ajax_load_programs, name='ajax_load_programs'),


]
