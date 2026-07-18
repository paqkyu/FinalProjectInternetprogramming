import time
from decimal import Decimal, InvalidOperation

import requests

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from workouts.models import Exercise


class Command(BaseCommand):
    help = "Download WorkoutX exercises and store them locally."

    def add_arguments(self, parser):
        parser.add_argument(
            "--limit",
            type=int,
            default=10,
            help="Exercises requested per API call. Free plan maximum is 10.",
        )

        parser.add_argument(
            "--max-exercises",
            type=int,
            default=None,
            help="Optional maximum number of exercises to process.",
        )

        parser.add_argument(
            "--all",
            action="store_true",
            help="Continue until WorkoutX returns no more exercises.",
        )

    def handle(self, *args, **options):
        api_key = settings.WORKOUTX_API_KEY

        if not api_key:
            raise CommandError(
                "WORKOUTX_API_KEY has not been configured."
            )

        request_limit = options["limit"]
        max_exercises = options["max_exercises"]
        download_all = options["all"]

        if request_limit < 1:
            raise CommandError("--limit must be at least 1.")

        if not download_all and max_exercises is None:
            max_exercises = 100

        url = "https://api.workoutxapp.com/v1/exercises"

        headers = {
            "X-WorkoutX-Key": api_key,
        }

        offset = 0
        processed_count = 0
        created_count = 0
        updated_count = 0
        request_count = 0
        plan_name = ""

        while True:
            if max_exercises is not None:
                remaining = max_exercises - processed_count

                if remaining <= 0:
                    break

                current_limit = min(request_limit, remaining)
            else:
                current_limit = request_limit

            try:
                response = requests.get(
                    url,
                    headers=headers,
                    params={
                        "limit": current_limit,
                        "offset": offset,
                    },
                    timeout=30,
                )

                request_count += 1

            except requests.RequestException as error:
                raise CommandError(
                    f"Could not connect to WorkoutX: {error}"
                ) from error

            try:
                response.raise_for_status()
            except requests.HTTPError as error:
                raise CommandError(
                    f"WorkoutX request failed.\n"
                    f"Status: {response.status_code}\n"
                    f"Response: {response.text[:500]}"
                ) from error

            try:
                response_data = response.json()
            except ValueError as error:
                raise CommandError(
                    "WorkoutX did not return valid JSON.\n"
                    f"Response: {response.text[:500]}"
                ) from error

            if isinstance(response_data, list):
                exercises = response_data

            elif (
                isinstance(response_data, dict)
                and isinstance(response_data.get("data"), list)
            ):
                exercises = response_data["data"]

            else:
                raise CommandError(
                    "WorkoutX returned an unexpected response.\n"
                    f"Response: {str(response_data)[:1000]}"
                )

            # An empty page means that there are no more exercises.
            if not exercises:
                self.stdout.write(
                    "WorkoutX returned an empty page. "
                    "All available exercises have been processed."
                )
                break

            if not plan_name:
                plan_name = response.headers.get(
                    "X-WorkoutX-Plan",
                    "unknown",
                )

                quota_remaining = response.headers.get(
                    "X-Quota-Remaining",
                    "unknown",
                )

                self.stdout.write(
                    f"WorkoutX plan: {plan_name}"
                )

                self.stdout.write(
                    f"Monthly requests remaining: {quota_remaining}"
                )

            for item in exercises:
                external_id = item.get("id")

                if external_id is None:
                    self.stdout.write(
                        self.style.WARNING(
                            "Skipped an exercise without an ID."
                        )
                    )
                    continue

                exercise, created = Exercise.objects.update_or_create(
                    external_id=str(external_id),
                    defaults={
                        "name": item.get(
                            "name",
                            "Unnamed exercise",
                        ),
                        "body_part": item.get(
                            "bodyPart",
                            "",
                        ),
                        "target": item.get(
                            "target",
                            "",
                        ),
                        "equipment": item.get(
                            "equipment",
                            "",
                        ),
                        "difficulty": item.get(
                            "difficulty",
                            "",
                        ),
                        "mechanic": item.get(
                            "mechanic",
                            "",
                        ),
                        "force": item.get(
                            "force",
                            "",
                        ),
                        "description": item.get(
                            "description",
                            "",
                        ),
                        "instructions": item.get(
                            "instructions",
                        ) or [],
                        "secondary_muscles": item.get(
                            "secondaryMuscles",
                        ) or [],
                        "gif_url": item.get(
                            "gifUrl",
                            "",
                        ),
                        "recommended_sets": item.get(
                            "recommendedSets",
                            "",
                        ),
                        "recommended_reps": item.get(
                            "recommendedReps",
                            "",
                        ),
                        "calories_per_minute": self.parse_decimal(
                            item.get("caloriesPerMinute")
                        ),
                        "is_active": True,
                    },
                )

                if created:
                    created_count += 1
                else:
                    updated_count += 1

                processed_count += 1

            # Move to the next API page.
            offset += len(exercises)

            quota_remaining = response.headers.get(
                "X-Quota-Remaining",
                "unknown",
            )

            self.stdout.write(
                f"Processed: {processed_count} | "
                f"Created: {created_count} | "
                f"Updated: {updated_count} | "
                f"Requests: {request_count} | "
                f"Quota remaining: {quota_remaining}"
            )

            # The free plan permits 30 requests per minute.
            # Waiting slightly more than two seconds avoids exceeding it.
            if plan_name.lower() == "free":
                time.sleep(2.1)

        database_total = Exercise.objects.count()

        self.stdout.write(
            self.style.SUCCESS(
                "\nSynchronization complete.\n"
                f"Exercises processed: {processed_count}\n"
                f"New exercises created: {created_count}\n"
                f"Existing exercises updated: {updated_count}\n"
                f"API requests used: {request_count}\n"
                f"Total exercises in database: {database_total}"
            )
        )

    @staticmethod
    def parse_decimal(value):
        if value in (None, ""):
            return None

        try:
            return Decimal(str(value))
        except (
            InvalidOperation,
            TypeError,
            ValueError,
        ):
            return None