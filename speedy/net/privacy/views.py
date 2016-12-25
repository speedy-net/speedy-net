from speedy.core.views import StaticPrivacyPolicyBaseView


class PrivacyPolicyView(StaticPrivacyPolicyBaseView):
    template_name = 'privacy/privacy_policy.html'

