from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('properties/', views.properties_list, name='properties'),
    path('property/<int:pk>/', views.property_detail, name='property_detail'),
    path('property/<int:property_id>/toggle-wishlist/', views.toggle_wishlist, name='toggle_wishlist'),
    path('wishlist/', views.wishlist_view, name='wishlist'),
    path('property/<int:property_id>/review/', views.add_review, name='add_review'),
    path('property/<int:property_id>/contact/', views.contact_seller, name='contact_seller'),
    path('about/', views.about, name='about'),
    path('login/', views.login_user, name='login'),
    path('register/', views.register_user, name='register'),
    path('logout/', views.logout_user, name='logout'),
    
    # Chat URLs
    path('chats/', views.chat_list, name='chat_list'),
    path('chat/<int:user_id>/', views.chat_detail, name='chat_detail'),
    path('chat/send/', views.send_message, name='send_message'),
    path('chat/fetch/<int:user_id>/', views.fetch_messages, name='fetch_messages'),
    
    # Video Call URL
    path('video-call/<str:room_name>/', views.video_call_room, name='video_call_room'),
    
    # Chatbot API
    path('api/chatbot/', views.chatbot_api, name='chatbot_api'),
    
    # Phase 5: Price Estimator
    path('price-estimator/', views.price_estimator, name='price_estimator'),
    path('api/estimate-price/', views.api_estimate_price, name='api_estimate_price'),
]
