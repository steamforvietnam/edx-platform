"""
Tests for waffle utils views.
"""
from django.conf import settings
from django.test import TestCase
from django.test.utils import override_settings
from edx_toggles.toggles import SettingDictToggle, SettingToggle
from edx_toggles.toggles.testutils import override_waffle_flag
from rest_framework.test import APIRequestFactory
from waffle.testutils import override_switch

from common.djangoapps.student.tests.factories import UserFactory

from .. import WaffleFlag, WaffleFlagNamespace
from .. import models
from .. import views as toggle_state_views

TEST_WAFFLE_FLAG_NAMESPACE = WaffleFlagNamespace("test")
TEST_WAFFLE_FLAG = WaffleFlag(TEST_WAFFLE_FLAG_NAMESPACE, "flag", __name__)


# TODO: Missing coverage for:
# - computed_status
class ToggleStateViewTests(TestCase):  # lint-amnesty, pylint: disable=missing-class-docstring

    def test_success_for_staff(self):
        response = self._get_toggle_state_response()
        assert response.status_code == 200
        assert response.data

    def test_failure_for_non_staff(self):
        response = self._get_toggle_state_response(is_staff=False)
        assert response.status_code == 403

    @override_waffle_flag(TEST_WAFFLE_FLAG, True)
    def test_response_with_waffle_flag(self):
        response = self._get_toggle_state_response()
        assert 'waffle_flags' in response.data
        assert response.data['waffle_flags']
        waffle_names = [waffle["name"] for waffle in response.data['waffle_flags']]
        assert 'test.flag' in waffle_names

    @override_switch('test.switch', True)
    def test_response_with_waffle_switch(self):
        response = self._get_toggle_state_response()
        assert 'waffle_switches' in response.data
        assert response.data['waffle_switches']
        waffle_names = [waffle["name"] for waffle in response.data['waffle_switches']]
        assert 'test.switch' in waffle_names

    def test_response_with_setting_toggle(self):
        _toggle = SettingToggle("MYSETTING", default=False, module_name="module1")
        with override_settings(MYSETTING=True):
            response = self._get_toggle_state_response()

        assert {'name': 'MYSETTING', 'is_active': True, 'module': 'module1', 'class': 'SettingToggle'}\
               in response.data['django_settings']

    def test_response_with_existing_setting_dict_toggle(self):
        response = self._get_toggle_state_response()
        assert {'name': "FEATURES['MILESTONES_APP']", 'is_active': True,
                'module': 'common.djangoapps.util.milestones_helpers',
                'class': 'SettingDictToggle'} in response.data['django_settings']

    def test_response_with_new_setting_dict_toggle(self):
        _toggle = SettingDictToggle(
            "CUSTOM_FEATURES", "MYSETTING", default=False, module_name="module1"
        )
        with override_settings(CUSTOM_FEATURES={"MYSETTING": True}):
            response = self._get_toggle_state_response()

        setting_dict = {toggle["name"]: toggle for toggle in response.data["django_settings"]}

        assert {'name': "CUSTOM_FEATURES['MYSETTING']", 'is_active': True, 'module': 'module1',
                'class': 'SettingDictToggle'} == setting_dict["CUSTOM_FEATURES['MYSETTING']"]

    def test_setting_overridden_by_setting_toggle(self):
        _toggle2 = SettingToggle(
            "MYSETTING2", module_name="module1"
        )
        _toggle3 = SettingDictToggle(
            "MYDICT", "MYSETTING3", module_name="module1"
        )
        with override_settings(MYSETTING1=True, MYSETTING2=False, MYDICT={"MYSETTING3": False}):
            # Need to pre-load settings, otherwise they are not picked up by the view
            assert settings.MYSETTING1
            response = self._get_toggle_state_response()

        setting_dict = {toggle["name"]: toggle for toggle in response.data["django_settings"]}

        # Check that Django settings for which a SettingToggle exists have both the correct is_active and class values
        assert setting_dict['MYSETTING1']['is_active']
        assert 'class' not in setting_dict['MYSETTING1']
        assert not setting_dict['MYSETTING2']['is_active']
        assert 'SettingToggle' == setting_dict['MYSETTING2']['class']
        assert not setting_dict["MYDICT['MYSETTING3']"]['is_active']
        assert 'SettingDictToggle' == setting_dict["MYDICT['MYSETTING3']"]['class']

    def test_no_duplicate_setting_toggle(self):
        _toggle1 = SettingToggle(
            "MYSETTING1", module_name="module1"
        )
        _toggle2 = SettingDictToggle(
            "MYDICT", "MYSETTING2", module_name="module1"
        )
        with override_settings(MYSETTING1=True, MYDICT={"MYSETTING2": False}):
            response = self._get_toggle_state_response()

        # Check there are no duplicate setting/toggle
        response_toggles_1 = [toggle for toggle in response.data["django_settings"] if toggle["name"] == "MYSETTING1"]
        response_toggles_2 = [
            toggle for toggle in response.data["django_settings"] if toggle["name"] == "MYDICT['MYSETTING2']"
        ]
        assert 1 == len(response_toggles_1)
        assert 1 == len(response_toggles_2)

    def test_code_owners_without_module_information(self):
        # Create a waffle flag without any associated module_name
        waffle_flag = WaffleFlag(TEST_WAFFLE_FLAG_NAMESPACE, "flag2", module_name=None)
        response = self._get_toggle_state_response(is_staff=True)

        result = [
            flag for flag in response.data["waffle_flags"] if flag["name"] == waffle_flag.name
        ][0]
        assert 'code_owner' not in result

    def test_course_overrides(self):
        models.WaffleFlagCourseOverrideModel.objects.create(waffle_flag="my.flag", enabled=True)
        course_overrides = {}

        # pylint: disable=protected-access
        toggle_state_views._add_waffle_flag_course_override_state(course_overrides)
        toggle_state_views._add_waffle_flag_computed_status(course_overrides)

        assert 'my.flag' in course_overrides
        assert 'course_overrides' in course_overrides['my.flag']
        assert 1 == len(course_overrides['my.flag']['course_overrides'])
        assert 'None' == course_overrides['my.flag']['course_overrides'][0]['course_id']
        assert 'on' == course_overrides['my.flag']['course_overrides'][0]['force']
        assert 'both' == course_overrides['my.flag']['computed_status']

    def _get_toggle_state_response(self, is_staff=True):  # lint-amnesty, pylint: disable=missing-function-docstring
        request = APIRequestFactory().get('/api/toggles/state/')
        user = UserFactory()
        user.is_staff = is_staff
        request.user = user
        view = toggle_state_views.ToggleStateView.as_view()
        response = view(request)
        return response
