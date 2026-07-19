from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import Exercise
import requests
from django.conf import settings
from django.http import HttpResponse
api_key=settings.WORKOUTX_API_KEY

# Create your views here.
def exercise_list(request):
    exercises = Exercise.objects.filter(
        is_active=True,
    )

    search_query = request.GET.get(
        "q",
        "",
    ).strip()

    selected_body_part = request.GET.get(
        "body_part",
        "",
    ).strip()

    selected_equipment = request.GET.get(
        "equipment",
        "",
    ).strip()

    selected_difficulty = request.GET.get(
        "difficulty",
        "",
    ).strip()

    if search_query:
        exercises = exercises.filter(
            Q(name__icontains=search_query)
            | Q(target__icontains=search_query)
            | Q(body_part__icontains=search_query)
            | Q(equipment__icontains=search_query)
            | Q(description__icontains=search_query)
        )

    if selected_body_part:
        exercises = exercises.filter(
            body_part=selected_body_part,
        )

    if selected_equipment:
        exercises = exercises.filter(
            equipment=selected_equipment,
        )

    if selected_difficulty:
        exercises = exercises.filter(
            difficulty=selected_difficulty,
        )

    body_parts = (
        Exercise.objects.filter(
            is_active=True,
        )
        .exclude(body_part="")
        .values_list(
            "body_part",
            flat=True,
        )
        .distinct()
        .order_by("body_part")
    )

    equipment_options = (
        Exercise.objects.filter(
            is_active=True,
        )
        .exclude(equipment="")
        .values_list(
            "equipment",
            flat=True,
        )
        .distinct()
        .order_by("equipment")
    )

    difficulty_options = (
        Exercise.objects.filter(
            is_active=True,
        )
        .exclude(difficulty="")
        .values_list(
            "difficulty",
            flat=True,
        )
        .distinct()
        .order_by("difficulty")
    )

    return render(
        request,
        "workouts/exercise_list.html",
        {
            "exercises": exercises,
            "body_parts": body_parts,
            "equipment_options": equipment_options,
            "difficulty_options": difficulty_options,
            "search_query": search_query,
            "selected_body_part": selected_body_part,
            "selected_equipment": selected_equipment,
            "selected_difficulty": selected_difficulty,
        },
    )


def exercise_detail(request, exercise_id):
    exercise = get_object_or_404(
        Exercise,
        pk=exercise_id,
        is_active=True,
    )

    return render(
        request,
        "workouts/exercise_detail.html",
        {
            "exercise": exercise,
        },
    )
def exercise_gif(request, exercise_id):
    exercise = get_object_or_404(
        Exercise,
        pk=exercise_id,
        is_active=True,
    )

    api_key = settings.WORKOUTX_API_KEY

    if not api_key:
        return HttpResponse(
            "WORKOUTX_API_KEY was not loaded.",
            status=500,
            content_type="text/plain",
        )

    try:
        response = requests.get(
            exercise.gif_url,
            headers={
                "X-WorkoutX-Key": api_key,
            },
            timeout=30,
        )

    except requests.RequestException as error:
        return HttpResponse(
            f"Could not contact WorkoutX: {error}",
            status=502,
            content_type="text/plain",
        )

    if response.status_code != 200:
        return HttpResponse(
            (
                f"WorkoutX returned status {response.status_code}.\n"
                f"Response: {response.text[:300]}"
            ),
            status=502,
            content_type="text/plain",
        )

    content_type = response.headers.get(
        "Content-Type",
        "image/gif",
    )

    return HttpResponse(
        response.content,
        content_type=content_type,
    )