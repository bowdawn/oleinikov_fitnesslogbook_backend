import graphene
from .types import LocationType, SportType, WorkoutCategoryType, ExerciseType, WorkoutDetailType, WorkoutPaginationType, WorkoutType, UserType
from .models import Location, Sport, WorkoutCategory, Exercise, Workout, WorkoutDetail, User
from graphql import GraphQLError 
import datetime
import jwt 
from django.conf import settings
from collections import defaultdict
from django.db.models import Max
from django.core.paginator import Paginator


class MaxWeightPerReps(graphene.ObjectType):
        reps = graphene.Int()
        max_weight = graphene.Float()


class Query(graphene.ObjectType):
    all_locations = graphene.List(LocationType)
    all_sports = graphene.List(SportType)
    all_workout_categories = graphene.List(WorkoutCategoryType)
    all_exercises = graphene.List(ExerciseType)
    all_workouts = graphene.Field(WorkoutPaginationType, limit=graphene.Int(), offset=graphene.Int())
    all_workout_details = graphene.List(WorkoutDetailType)

    location = graphene.Field(LocationType, id=graphene.Int(required=True))
    sport = graphene.Field(SportType, id=graphene.Int(required=True))
    workout_type = graphene.Field(WorkoutCategoryType, id=graphene.Int(required=True))
    exercise = graphene.Field(ExerciseType, id=graphene.Int(required=True))
    workout = graphene.Field(WorkoutType, id=graphene.Int(required=True))
    workout_detail = graphene.Field(WorkoutDetailType, id=graphene.Int(required=True))
    crossfit_attendance_count = graphene.Int()
    crossfit_attendance_last_week_count = graphene.Int()
    crossfit_attendance_total_count = graphene.Int()
    swimming_attendance_count = graphene.Int()
    swimming_attendance_last_week_count = graphene.Int()
    swimming_attendance_total_count = graphene.Int()
    users = graphene.List(UserType)
    max_weight_per_reps = graphene.List(
        MaxWeightPerReps, 
        exercise_name=graphene.String(required=True)
    )

    def resolve_users(self, info):
        return User.objects.all()
    
    def resolve_crossfit_attendance_count(self, info):
        # Get today's date
        today = datetime.date.today()
        
        # Calculate the most recent Monday
        monday = today - datetime.timedelta(days=today.weekday())
        
     
        
        # Filter workouts for the current week and category, counting unique dates only
        unique_days_this_week = Workout.objects.filter(
            sport__name__iexact="CrossFit",
            date__gte=monday,
            date__lte=today
        ).values('date').distinct().count()  # Use 'date' to count unique workout days
        
        return unique_days_this_week
    
    def resolve_crossfit_attendance_last_week_count(self, info):
        # Get today's date
        today = datetime.date.today()
        
        # Calculate the start and end dates for last week (previous Monday to Sunday)
        last_monday = today - datetime.timedelta(days=today.weekday() + 7)
        last_sunday = last_monday + datetime.timedelta(days=6)
        
       
        
        # Filter workouts for last week, counting unique dates only
        unique_days_last_week = Workout.objects.filter(
            sport__name__iexact="CrossFit",
            date__gte=last_monday,
            date__lte=last_sunday
        ).values('date').distinct().count()
        
        
        
        return unique_days_last_week
    
    
    def resolve_crossfit_attendance_total_count(self, info):        
        # Get all distinct workout days for CrossFit attendance
        total_crossfit_days = (
        Workout.objects.filter(sport__name__iexact="CrossFit")  # Case-insensitive match for "CrossFit"
        .values_list('date', flat=True)  # Get the distinct workout dates
        .distinct()
        .count()
    )
        
        return total_crossfit_days
    
    def resolve_swimming_attendance_count(self, info):
        # Get today's date
        today = datetime.date.today()
        
        # Calculate the most recent Monday
        monday = today - datetime.timedelta(days=today.weekday())
        
        # Filter for workouts categorized as swimming and attended this week
        swimming = Sport.objects.filter(name="Swimming").first()
        
        if not swimming:
            return 0  # No swimming sport found
        
        # Filter workouts for the current week and category, counting unique dates only
        unique_days_this_week = Workout.objects.filter(
            sport=swimming,
            date__gte=monday,
            date__lte=today
        ).values('date').distinct().count()  # Use 'date' to count unique workout days
        
        return unique_days_this_week
    
    def resolve_swimming_attendance_last_week_count(self, info):
        # Get today's date
        today = datetime.date.today()
        
        # Calculate the start and end dates for last week (previous Monday to Sunday)
        last_monday = today - datetime.timedelta(days=today.weekday() + 7)
        last_sunday = last_monday + datetime.timedelta(days=6)
        
        # Filter for workouts categorized as swimming and attended last week
        swimming = Sport.objects.filter(name="Swimming").first()
        
        if not swimming:
            return 0  # No swimming sport found
        
        # Filter workouts for last week, counting unique dates only
        unique_days_last_week = Workout.objects.filter(
            sport=swimming,
            date__gte=last_monday,
            date__lte=last_sunday
        ).values('date').distinct().count()
        
        
        
        return unique_days_last_week
    
    
    def resolve_swimming_attendance_total_count(self, info):
        # Retrieve the swimming sport category
        swimming = Sport.objects.filter(name="Swimming").first()
        
        if not swimming:
            return 0  # No swimming category found
        
        # Get all distinct workout days for swimming attendance
        total_swimming_days = (
            Workout.objects.filter(sport=swimming)
            .values('date')
            .distinct()
            .count()
        )
        
        return total_swimming_days
    
    
    
    
    

    def resolve_all_locations(self, info):
        return Location.objects.all()

    def resolve_all_sports(self, info):
        return Sport.objects.all()

    def resolve_all_workout_categories(self, info):
        return WorkoutCategory.objects.all()

    def resolve_all_exercises(self, info):
        return Exercise.objects.all()

    def resolve_all_workouts(self, info, limit=None, offset=None):
        headers = info.context.META
        auth_header = headers.get('HTTP_AUTHORIZATION', None)
        
        if auth_header:
            token = auth_header.split()[1]
            
            try:
                payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
                username = payload.get('username')
                
                if not username:
                    raise GraphQLError("Invalid token.")
                
                try:
                    user = User.objects.get(username=username)
                    info.context.user = user
                except User.DoesNotExist:
                    raise GraphQLError("User does not exist.")
            except jwt.ExpiredSignatureError:
                raise GraphQLError("Token has expired.")
            except jwt.InvalidTokenError:
                raise GraphQLError("Invalid token.")
        else:
            raise GraphQLError("Authorization header is missing.")
        
        user = info.context.user
        
        if not user.is_authenticated:
            raise GraphQLError("You must be logged in to view workouts.")
        
        # Filter and order workouts
        workouts = Workout.objects.filter(user=user).order_by('-date')
        
        # Paginate workouts
        paginator = Paginator(workouts, limit or 10)  # Default to 10 items per page if limit is None
        page = paginator.get_page(offset // (limit or 10) + 1)
    
        # Group workouts by date
        grouped_workouts = defaultdict(list)
        for workout in page.object_list:
            grouped_workouts[workout.date].append(workout)
        
        grouped_items = [
            {"date": date, "workouts": grouped_workouts[date]}
            for date in sorted(grouped_workouts.keys(), reverse=True)
        ]
        
        has_next_page = page.has_next()
        has_previous_page = page.has_previous()
        
        return WorkoutPaginationType(
            grouped_items=grouped_items,
            total_count=paginator.count,
            has_next_page=has_next_page,
            has_previous_page=has_previous_page,
        )

                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      
    def resolve_all_workout_details(self, info):
        return WorkoutDetail.objects.all()

    def resolve_location(self, info, id):
        try:
            return Location.objects.get(pk=id)
        except Location.DoesNotExist:
            raise GraphQLError(f"Location with ID {id} does not exist.")

    def resolve_sport(self, info, id):
        try:
            return Sport.objects.get(pk=id)
        except Sport.DoesNotExist:
            raise GraphQLError(f"Sport with ID {id} does not exist.")

    def resolve_workout_type(self, info, id):
        try:
            return WorkoutCategory.objects.get(pk=id)
        except WorkoutCategory.DoesNotExist:
            raise GraphQLError(f"Workout category with ID {id} does not exist.")

    def resolve_exercise(self, info, id):
        try:
            return Exercise.objects.get(pk=id)
        except Exercise.DoesNotExist:
            raise GraphQLError(f"Exercise with ID {id} does not exist.")

    def resolve_workout(self, info, id):
        try:
            return Workout.objects.get(pk=id)
        except Workout.DoesNotExist:
            raise GraphQLError(f"Workout with ID {id} does not exist.")

    def resolve_workout_detail(self, info, id):
        try:
            return WorkoutDetail.objects.get(pk=id)
        except WorkoutDetail.DoesNotExist:
            raise GraphQLError(f"Workout detail with ID {id} does not exist.")

   
    
    

    def resolve_max_weight_per_reps(self, info, exercise_name):
        # Fetch the exercise by name
        try:
            exercise = Exercise.objects.get(name=exercise_name)
        except Exercise.DoesNotExist:
            raise GraphQLError(f"Exercise with name '{exercise_name}' does not exist.")

        # Aggregate maximum weight for each rep count
        max_weights = (
            WorkoutDetail.objects.filter(exercise=exercise)
            .values('reps')  # Group by reps
            .annotate(max_weight=Max('weight'))  # Annotate with the maximum weight
            .order_by('reps')  # Sort by reps (optional)
        )

        # Convert query results into objects compatible with the GraphQL type
        return [MaxWeightPerReps(reps=entry['reps'], max_weight=entry['max_weight']) for entry in max_weights]