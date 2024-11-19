import graphene
from graphene_django.types import DjangoObjectType
from .models import Location, Sport, WorkoutCategory, Exercise, Workout, WorkoutDetail, User


class LocationType(DjangoObjectType):
    class Meta:
        model = Location

class SportType(DjangoObjectType):
    class Meta:
        model = Sport

class WorkoutCategoryType(DjangoObjectType):
    class Meta:
        model = WorkoutCategory
        
class UserType(DjangoObjectType):
    class Meta:
        model = User
        fields = ("id", "username", "email", "password") 

class WorkoutType(DjangoObjectType):
    class Meta:
        model = Workout
        fields = ("id", "date", "sport", "workout_category", "duration", "location", "user", "details")

class ExerciseType(DjangoObjectType):
    class Meta:
        model = Exercise

class WorkoutDetailType(DjangoObjectType):
    class Meta:
        model = WorkoutDetail
        
class CreateWorkoutDetailInputType(graphene.InputObjectType):
    exercise_name = graphene.String()
    reps = graphene.Int()
    weight = graphene.Int()
    calories = graphene.Int()
    distance = graphene.Int()
    duration = graphene.Int()
    order = graphene.Int()
    
class UpdateWorkoutDetailInputType(graphene.InputObjectType):
    id = graphene.ID()
    exercise_name = graphene.String()
    reps = graphene.Int()
    weight = graphene.Int()
    calories = graphene.Int()
    distance = graphene.Int()
    duration = graphene.Int()
    order = graphene.Int()
    
class WorkoutGroupType(graphene.ObjectType):
    date = graphene.Date()
    workouts = graphene.List(WorkoutType)

class WorkoutPaginationType(graphene.ObjectType):
    grouped_items = graphene.List(WorkoutGroupType)
    total_count = graphene.Int()
    has_next_page = graphene.Boolean()
    has_previous_page = graphene.Boolean()