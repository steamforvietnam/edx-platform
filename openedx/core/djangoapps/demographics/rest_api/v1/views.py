
from edx_rest_framework_extensions.auth.jwt.authentication import JwtAuthentication
from rest_framework import permissions, status
from rest_framework.authentication import SessionAuthentication
from rest_framework.response import Response
from rest_framework.views import APIView

from openedx.core.djangoapps.demographics.api.status import (
    show_user_demographics, get_user_demographics_call_to_action_status,
)
from openedx.core.djangoapps.demographics.models import UserDemographics


class DemographicsStatusView(APIView):
    """
    Demographics display status for the User.

    The API will return whether or not to display t`he Demographics UI based on
    the User's status in the Platform
    """
    authentication_classes = (JwtAuthentication, SessionAuthentication)
    permission_classes = (permissions.IsAuthenticated, )

    def _response_context(self, user, user_demographics=None):
        if user_demographics:
            call_to_action_dismissed = user_demographics.call_to_action_dismissed
        else:
            call_to_action_dismissed = get_user_demographics_call_to_action_status(user)
        return {
            'display': show_user_demographics(user),
            'call_to_action_dismissed': call_to_action_dismissed
        }

    def get(self, request):
        """
        GET /api/user/v1/accounts/demographics/status

        This is a Web API to determine the status of demographics related features
        """
        user = request.user
        return Response(self._response_context(user))

    def patch(self, request):
        """
        PATCH /api/user/v1/accounts/demographics/status

        This is a Web API to update fields that are dependant on user interaction.
        """
        call_to_action_dismissed = request.data.get('call_to_action_dismissed')
        user = request.user
        if not isinstance(call_to_action_dismissed, bool):
            return Response(status.HTTP_400_BAD_REQUEST)
        (user_demographics, _) = UserDemographics.objects.get_or_create(user=user)
        user_demographics.call_to_action_dismissed = call_to_action_dismissed
        user_demographics.save()
        return Response(self._response_context(user, user_demographics))
