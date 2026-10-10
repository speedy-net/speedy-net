# Used also by Speedy Net.

class SPEEDY_MATCH_SITE_PROFILE_SETTINGS(object):
    """
    Namespace class holding Speedy Match site profile configuration constants - height/age limits, the step-by-step activation form field groups, and other related settings. Also used by Speedy Net.
    """
    MIN_HEIGHT_ALLOWED = 1  # In cm.
    MAX_HEIGHT_ALLOWED = 450  # In cm.

    MIN_AGE_TO_MATCH_ALLOWED = 0  # In years.
    MAX_AGE_TO_MATCH_ALLOWED = 180  # In years.

    MIN_HEIGHT_TO_MATCH = 85  # In cm.
    MAX_HEIGHT_TO_MATCH = 320  # In cm.

    SPEEDY_MATCH_SITE_PROFILE_FORM_FIELDS = [
        [],  # There's no step 0
        [],  # Step 1 = registration form
        ['profile_picture'],
        ['profile_description', 'city', 'height'],
        ['children', 'more_children'],
        ['diet', 'smoking_status'],
        ['relationship_status'],
        ['gender_to_match', 'match_description', 'min_age_to_match', 'max_age_to_match'],
        ['diet_match', 'smoking_status_match'],
        ['relationship_status_match'],
    ]


