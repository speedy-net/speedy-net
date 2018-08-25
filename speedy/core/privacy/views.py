from speedy.core.base.views import StaticPrivacyPolicyBaseView


class PrivacyPolicyView(StaticPrivacyPolicyBaseView):
    template_name = 'privacy/privacy_policy.html'


