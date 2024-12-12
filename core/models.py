
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Location(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Sport(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class WorkoutCategory(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Exercise(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Workout(models.Model):
    date = models.DateField(db_index=True)
    sport = models.ForeignKey(Sport, on_delete=models.CASCADE)
    workout_category = models.ForeignKey(WorkoutCategory, on_delete=models.CASCADE)
    duration = models.PositiveIntegerField(null=True)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    def __str__(self):
        return f"{self.date} - {self.sport}"


class WorkoutDetail(models.Model):
    workout = models.ForeignKey(Workout, on_delete=models.CASCADE,  related_name='details')
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    reps = models.PositiveIntegerField(null=True, blank=True)
    weight = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    calories = models.PositiveIntegerField(null=True, blank=True)
    distance = models.PositiveIntegerField(null=True, blank=True)
    duration = models.PositiveIntegerField(null=True, blank=True)
    order = models.PositiveIntegerField(null=True, blank=True)
    def __str__(self):
        return f"Workout Details: {self.exercise.name} - {self.workout.date} - Order {self.order}"
    
    

