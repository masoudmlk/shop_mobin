from django.core.validators import MinValueValidator, MaxValueValidator


def score_validator():
    return [MinValueValidator(1), MaxValueValidator(5)]
