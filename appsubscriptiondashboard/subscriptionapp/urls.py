from django.urls import include, path
from rest_framework.authtoken.views import obtain_auth_token  # <-- Here
from django.views.decorators.csrf import csrf_exempt

from . import views

urlpatterns = [
   path('create-app/', views.CreateUserApp.as_view(), name='create-app'), 
   path('update-app/', views.UpdateUserApp.as_view(), name='update-app'),   
   path('delete-app/', views.DeleteUserApp.as_view(), name='delete-app'),   
   path('app-details/', views.UpdateUserApp.as_view(), name='app-details'),   

   # ====================================== Versioning APIs ======================================================================
   path('<str:version>/create-app/', views.CreateUserApp.as_view(), name='create-app'),   
   path('<str:version>/update-app/', views.UpdateUserApp.as_view(), name='update-app'),   
   path('<str:version>/delete-app/', views.DeleteUserApp.as_view(), name='delete-app'),   
   path('<str:version>/app-details/', views.UpdateUserApp.as_view(), name='app-details'),   

   # ====================================== End of Versioning APIs ======================================================================
]