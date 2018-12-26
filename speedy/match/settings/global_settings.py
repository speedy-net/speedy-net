# Used also by Speedy Net.

MIN_HEIGHT_ALLOWED = 1 # In cm. # ~~~~ TODO: move to class SpeedyMatchSiteProfileSettings?
MAX_HEIGHT_ALLOWED = 450 # In cm. # ~~~~ TODO: move to class SpeedyMatchSiteProfileSettings?

MIN_AGE_MATCH_ALLOWED = 0 # In years. # ~~~~ TODO: move to class SpeedyMatchSiteProfileSettings?
MAX_AGE_MATCH_ALLOWED = 180 # In years. # ~~~~ TODO: move to class SpeedyMatchSiteProfileSettings?

SPEEDY_MATCH_SITE_PROFILE_FORM_FIELDS = [ # ~~~~ TODO: move to class SpeedyMatchSiteProfileSettings?
    [],  # There's no step 0
    [],  # Step 1 = registration form
    ['photo'],
    ['profile_description', 'city', 'height'],
    ['children', 'more_children'],
    ['diet', 'smoking_status'],
    ['marital_status'],
    ['gender_to_match', 'match_description', 'min_age_match', 'max_age_match'],
    ['diet_match', 'smoking_status_match'],
    ['marital_status_match'],
]


