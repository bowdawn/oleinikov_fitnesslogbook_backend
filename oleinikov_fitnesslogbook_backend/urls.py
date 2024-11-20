from django.contrib import admin
from django.urls import path
from graphene_django.views import GraphQLView
from django.views.decorators.csrf import csrf_exempt
from core.schema import schema 
from .views import landing

urlpatterns = [
    path('admin/', admin.site.urls),
    path('graphql/', csrf_exempt(GraphQLView.as_view(graphiql=True, schema=schema))),
    path('', landing, name='landing'),
]
