from django.http import JsonResponse

def landing(request):
    return JsonResponse({"message": "Oleinikov Fitness Logbook Backend"})