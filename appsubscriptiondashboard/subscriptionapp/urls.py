from django.urls import include, path
from rest_framework.authtoken.views import obtain_auth_token  # <-- Here
from django.views.decorators.csrf import csrf_exempt

from . import views

urlpatterns = [
   
    # User APP CRUD    
   path('create-app/', views.CreateUserApp.as_view(), name='create-app'), 
   path('update-app/', views.UpdateUserApp.as_view(), name='update-app'),   
   path('delete-app/', views.DeleteUserApp.as_view(), name='delete-app'),   
   path('app-details/', views.UpdateUserApp.as_view(), name='app-details'),   
   
   path('subscription-details/', views.SubscriptionDetails.as_view(), name='subscription-details'),   
   
   path('unsubscribe/',views.SubscriptionDelete.as_view(),name="unsubscribe"),
   # ====================================== Versioning APIs ======================================================================
   # User App CRUD
   path('<str:version>/create-app/', views.CreateUserApp.as_view(), name='create-app'),   
   path('<str:version>/update-app/', views.UpdateUserApp.as_view(), name='update-app'),   
   path('<str:version>/delete-app/', views.DeleteUserApp.as_view(), name='delete-app'),   
   path('<str:version>/app-details/', views.UserAppDetails.as_view(), name='app-details'),   
 
   path('<str:version>/subscription-details/', views.SubscriptionDetails.as_view(), name='subscription-details'),   
   
   path('<str:version>/unsubscribe/',views.SubscriptionDelete.as_view(),name="unsubscribe"),

   # ====================================== End of Versioning APIs ===============================================================
]