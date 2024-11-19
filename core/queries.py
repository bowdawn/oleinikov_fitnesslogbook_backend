import graphene
from .types import LocationType, SportType, WorkoutCategoryType, ExerciseType, WorkoutDetailType, WorkoutPaginationType, WorkoutType, UserType
from .models import Location, Sport, WorkoutCategory, Exercise, Workout, WorkoutDetail, User
from graphql import GraphQLError 
import datetime
import jwt 
from django.conf import settings
from collections import defaultdict



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

    def resolve_users(self, info):
        return User.objects.all()
    
    def resolve_crossfit_attendance_count(self, info):
        # Get today's date
        today = datetime.date.today()
        
        # Calculate the most recent Monday
        monday = today - datetime.timedelta(days=today.weekday())
        
        # Filter for workouts categorized as CrossFit and attended this week
        crossfit = Sport.objects.filter(name="CrossFit").first()
        
        if not crossfit:
            return 0  # No CrossFit sport found
        
        # Filter workouts for the current week and category, counting unique dates only
        unique_days_this_week = Workout.objects.filter(
            sport=crossfit,
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
        
        # Filter for workouts categorized as CrossFit and attended last week
        crossfit = Sport.objects.filter(name="CrossFit").first()
        
        if not crossfit:
            return 0  # No CrossFit sport found
        
        # Filter workouts for last week, counting unique dates only
        unique_days_last_week = Workout.objects.filter(
            sport=crossfit,
            date__gte=last_monday,
            date__lte=last_sunday
        ).values('date').distinct().count()
        
        
        
        return unique_days_last_week
    
    
    def resolve_crossfit_attendance_total_count(self, info):
        # Retrieve the CrossFit sport category
        crossfit = Sport.objects.filter(name="CrossFit").first()
        
        if not crossfit:
            return 0  # No CrossFit category found
        
        # Get all distinct workout days for CrossFit attendance
        total_crossfit_days = (
            Workout.objects.filter(sport=crossfit)
            .values('date')
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
    
        # Group workouts by date
        grouped_workouts = defaultdict(list)
        for workout in workouts:
            grouped_workouts[workout.date].append(workout)
    
        # Apply pagination based on grouped dates
        unique_dates = sorted(grouped_workouts.keys(), reverse=True)
        total_count = len(unique_dates)
    
        if offset is not None:
            unique_dates = unique_dates[offset:]
        if limit is not None:
            unique_dates = unique_dates[:limit]
    
        grouped_items = [
            {"date": date, "workouts": grouped_workouts[date]}
            for date in unique_dates
        ]
    
        has_next_page = (offset + limit) < total_count if limit and offset is not None else False
        has_previous_page = offset > 0 if offset is not None else False
    
        return WorkoutPaginationType(
            grouped_items=grouped_items,
            total_count=total_count,
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

    def resolve_workout_detail(self, info, id, exercise_name=None):
       """
       Resolves a single WorkoutDetail by its ID and optionally filters by exercise name.
    
       Args:
           info: GraphQL context information.
           id: The primary key of the WorkoutDetail to retrieve.
           exercise_name: Optional name of the exercise to filter by.
    
       Returns:
           WorkoutDetail object if found and matches the optional exercise_name.
    
       Raises:
           GraphQLError: If the WorkoutDetail does not exist or does not match the exercise_name.
       """
       try:
           # Base query
           query = WorkoutDetail.objects.filter(pk=id)
           
           # Optionally filter by exercise_name
           if exercise_name:
               query = query.filter(exercise__name=exercise_name)
           
           # Get the result or raise an error
           workout_detail = query.first()
           if not workout_detail:
               raise GraphQLError(
                   f"Workout detail with ID {id} and exercise name '{exercise_name}' does not exist."
                   if exercise_name
                   else f"Workout detail with ID {id} does not exist."
               )
           
           return workout_detail
       except Exception as e:
           raise GraphQLError(f"An unexpected error occurred: {str(e)}")