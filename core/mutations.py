import graphene
from graphql import GraphQLError

from graphql_jwt.mutations import Verify 
from graphql_jwt.shortcuts import get_token

from django.db import transaction
from .types import (
    LocationType,
    SportType,
    ExerciseType,
    UpdateWorkoutDetailInputType,
    WorkoutCategoryType,
    CreateWorkoutDetailInputType,
    WorkoutDetailType,
    WorkoutType,
    UserType
)
from .models import Location, Sport, WorkoutCategory, Exercise, Workout, WorkoutDetail, User
from decimal import Decimal


import graphene
from graphql import GraphQLError
from graphql_jwt.mutations import Verify
from graphql_jwt.shortcuts import get_token
from django.contrib.auth import get_user_model
from django.db import transaction
from .types import UserType
from .models import User
from graphql_jwt.exceptions import PermissionDenied
from graphql_jwt.utils import jwt_decode
import logging
import jwt 
from django.conf import settings


# Create User Mutation
class CreateUser(graphene.Mutation):
    user = graphene.Field(lambda: UserType)
    token = graphene.String()

    class Arguments:
        username = graphene.String(required=True)
        password = graphene.String(required=True)
        email = graphene.String(required=True)

    def mutate(self, info, username, password, email):
        # Check for existing user
        if User.objects.filter(username=username).exists():
            raise GraphQLError("Username already exists")
        if User.objects.filter(email=email).exists():
            raise GraphQLError("Email already in use")

        # Create user within a transaction block
        with transaction.atomic():
            user = User.objects.create_user(username=username, email=email, password=password)
            token = get_token(user)

        return CreateUser(user=user, token=token)


# Login Mutation
class Login(graphene.Mutation):
    user = graphene.Field(lambda: UserType)
    token = graphene.String()

    class Arguments:
        username = graphene.String(required=True)
        password = graphene.String(required=True)

    def mutate(self, info, username, password):
        try:
            user = get_user_model().objects.get(username=username)
        except get_user_model().DoesNotExist:
            raise GraphQLError("Invalid credentials")

        if not user.check_password(password):
            raise GraphQLError("Invalid credentials")

        token = get_token(user)
        return Login(user=user, token=token)


class VerifyToken(graphene.Mutation):
    is_valid = graphene.Boolean()
    user = graphene.Field(lambda: UserType)

    class Arguments:
        pass  # No need for token argument

    def mutate(self, info):
        headers = info.context.META
        auth_header = headers.get('HTTP_AUTHORIZATION', None)

        if auth_header:
            # Extract the token from the 'Authorization' header
            token = auth_header.split()[1]
            try:
                # Decode the token to get the payload
                decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
                logging.info(f"Decoded Token: {decoded_token}")

                # Get the username from the token payload
                username = decoded_token.get("username")
                if not username:
                    raise GraphQLError("Invalid token: Username not found.")

                # Retrieve the user based on the username
                try:
                    user = get_user_model().objects.get(username=username)
                    info.context.user = user  # Set the user in context for authorization
                except get_user_model().DoesNotExist:
                    logging.error("User not found for decoded username")
                    return VerifyToken(is_valid=False)

                # If successful, return the user and is_valid = True
                return VerifyToken(is_valid=True, user=user)

            except jwt.ExpiredSignatureError:
                logging.warning("Token has expired.")
                raise GraphQLError("Token has expired.")
            except jwt.InvalidTokenError:
                logging.warning("Invalid token.")
                raise GraphQLError("Invalid token.")
            except Exception as e:
                # Log any other exceptions for debugging
                logging.error(f"Error verifying token: {str(e)}")
                return VerifyToken(is_valid=False)
        else:
            raise GraphQLError("Authorization header is missing.")
        
class CreateLocation(graphene.Mutation):
    location = graphene.Field(LocationType)

    class Arguments:
        name = graphene.String(required=True)

    def mutate(self, info, name):
        location = Location(name=name)
        location.save()
        return CreateLocation(location=location)


class CreateSport(graphene.Mutation):
    sport = graphene.Field(SportType)

    class Arguments:
        name = graphene.String(required=True)

    def mutate(self, info, name):
        sport = Sport(name=name)
        sport.save()
        return CreateSport(sport=sport)


class CreateWorkoutCategory(graphene.Mutation):
    workout_category = graphene.Field(WorkoutCategoryType)

    class Arguments:
        name = graphene.String(required=True)

    def mutate(self, info, name):
        workout_category = WorkoutCategory(name=name)
        workout_category.save()
        return CreateWorkoutCategory(workout_category=workout_category)


class CreateExercise(graphene.Mutation):
    exercise = graphene.Field(ExerciseType)

    class Arguments:
        name = graphene.String(required=True)
        description = graphene.String()

    def mutate(self, info, name, description=""):
        exercise = Exercise(name=name, description=description)
        exercise.save()
        return CreateExercise(exercise=exercise)


class CreateWorkout(graphene.Mutation):
    workout = graphene.Field(WorkoutType)
    workout_details = graphene.List(WorkoutDetailType)

    class Arguments:
        date = graphene.types.datetime.Date(required=True)
        sport_name = graphene.String(required=True)
        workout_category_name = graphene.String(required=True)
        location_name = graphene.String(required=True)
        duration = graphene.Int(required=False)
        workout_details_input = graphene.List(CreateWorkoutDetailInputType, required=False)

    def mutate(
        self,
        info,
        date,
        workout_category_name,
        duration=None,
        sport_name=None,
        location_name=None,
        workout_details_input=None,
    ):
        with transaction.atomic():
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
                raise GraphQLError("You must be logged in to create workouts.") 
            sport, _ = Sport.objects.get_or_create(name=sport_name)
            location, _ = Location.objects.get_or_create(name=location_name)
            workout_category, _ = WorkoutCategory.objects.get_or_create(
                name=workout_category_name
            )
            workout = Workout(
                user=user,
                date=date,
                sport=sport,
                workout_category=workout_category,
                duration=duration,
                location=location,
            )
            workout.save()
            workout_details = []
            if workout_details_input:
                for detail in workout_details_input:
                    exercise, _ = Exercise.objects.get_or_create(
                        name=detail.exercise_name
                    )
                    weight = (
                        Decimal(detail.weight) if detail.weight is not None else None
                    )
                    workout_detail = WorkoutDetail(
                        workout=workout,
                        exercise=exercise,
                        reps=detail.reps,
                        weight=weight,
                        calories=detail.calories,
                        distance=detail.distance,
                        duration=detail.duration,
                        order=detail.order,
                    )
                    workout_detail.save()
                    workout_details.append(workout_detail)
            return CreateWorkout(workout=workout, workout_details=workout_details)


class UpdateWorkout(graphene.Mutation):
   
    workout = graphene.Field(WorkoutType)
    workout_details = graphene.List(WorkoutDetailType)

    class Arguments:
        workout_id = graphene.ID(required=True)
        date = graphene.types.datetime.Date(required=False)
        sport_name = graphene.String(required=False)
        workout_category_name = graphene.String(required=False)
        location_name = graphene.String(required=False)
        duration = graphene.Int(required=False)
        workout_details_input = graphene.List(UpdateWorkoutDetailInputType, required=False)

    def mutate(
        self,
        info,
        workout_id,
        date,
        sport_name,
        workout_category_name,
        location_name,
        duration=None,
        workout_details_input=None,
    ):
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
            raise GraphQLError("You must be logged in to update workouts.") 
        try:
            workout = Workout.objects.get(id=workout_id)
        except Workout.DoesNotExist:
            raise Exception("Workout not found")
        if date:
            workout.date = date
        if duration is not None:
            workout.duration = duration
        if sport_name:
            sport, _ = Sport.objects.get_or_create(name=sport_name)
            workout.sport = sport
        if workout_category_name:
            workout_category, _ = WorkoutCategory.objects.get_or_create(name=workout_category_name)
            workout.workout_category = workout_category
        if location_name:
            location, _ = Location.objects.get_or_create(name=location_name)
            workout.location = location
        workout.save()

        # Handling workout details
        workout_details = []
        existing_detail_ids = {detail.id for detail in workout.details.all()}

        # Track provided IDs for update/delete operations
        input_detail_ids = set()
        
        if workout_details_input:
            for detail in workout_details_input:
                if detail.id:  # Update existing detail
                    try:
                        workout_detail = WorkoutDetail.objects.get(id=detail.id, workout=workout)
                    except WorkoutDetail.DoesNotExist:
                        raise Exception("Workout detail not found")
                    input_detail_ids.add(detail.id)  # Track this ID for update
                else:  # Create new detail
                    workout_detail = WorkoutDetail(workout=workout)

                # Update detail fields
                exercise, _ = Exercise.objects.get_or_create(name=detail.exercise_name)
                workout_detail.exercise = exercise
                workout_detail.reps = detail.reps
                workout_detail.weight = Decimal(detail.weight) if detail.weight is not None else None
                workout_detail.calories = detail.calories
                workout_detail.distance = detail.distance
                workout_detail.duration = detail.duration
                workout_detail.order = detail.order
                workout_detail.save()
                workout_details.append(workout_detail)

        
        details_to_delete = existing_detail_ids - input_detail_ids
        if details_to_delete:
            WorkoutDetail.objects.filter(id__in=details_to_delete).delete()

        return UpdateWorkout(workout=workout, workout_details=workout_details)


class Mutation(graphene.ObjectType):
    create_location = CreateLocation.Field()
    create_sport = CreateSport.Field()
    create_workout_category = CreateWorkoutCategory.Field()
    create_exercise = CreateExercise.Field()
    create_workout = CreateWorkout.Field()
    update_workout = UpdateWorkout.Field()
    create_user = CreateUser.Field()
    login = Login.Field()
    verify_token = VerifyToken.Field()
