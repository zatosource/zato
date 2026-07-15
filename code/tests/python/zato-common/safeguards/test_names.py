# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# piigex
from piigex.detectors import get_registry

# Zato
from zato.common.util.safeguards.names import Detector_Labels, get_detector_choices, get_land_choices, Land_International, \
    Land_Names

# ################################################################################################################################
# ################################################################################################################################

class TestRegistryCoverage:

    def test_every_registry_detector_has_a_label(self) -> 'None':

        # A library upgrade that adds detectors must fail here instead of showing raw codes in the UI.
        registry = get_registry()

        for name in registry:
            assert name in Detector_Labels, f'Detector `{name}` has no label in Detector_Labels'

    def test_every_registry_land_has_a_full_name(self) -> 'None':

        # A library upgrade that adds lands must fail here instead of showing raw codes in the UI.
        registry = get_registry()

        for detector in registry.values():
            assert detector.region in Land_Names, f'Land `{detector.region}` has no full name in Land_Names'

# ################################################################################################################################
# ################################################################################################################################

class TestLandChoices:

    def test_international_comes_first(self) -> 'None':

        choices = get_land_choices()
        first_choice = choices[0]

        assert first_choice == (Land_International, Land_Names[Land_International])

    def test_countries_sort_by_full_name(self) -> 'None':

        # Everything after International must be in alphabetical order of full names.
        choices = get_land_choices()
        countries = choices[1:]

        names = []
        for _, name in countries:
            names.append(name)

        assert names == sorted(names)

    def test_every_choice_land_exists_in_the_registry(self) -> 'None':

        # The choices are built from the registry, so each land must have at least one registered detector.
        registry = get_registry()

        registry_lands = set()
        for detector in registry.values():
            registry_lands.add(detector.region)

        choices = get_land_choices()

        for land, _ in choices:
            assert land in registry_lands

# ################################################################################################################################
# ################################################################################################################################

class TestDetectorChoices:

    def test_every_registry_detector_appears_exactly_once(self) -> 'None':

        registry = get_registry()
        groups = get_detector_choices()

        names = []
        for _, group in groups:
            for name, _ in group:
                names.append(name)

        assert sorted(names) == sorted(registry)

    def test_groups_follow_land_choice_order(self) -> 'None':

        # Group headers must be the land full names, in the same order as the land choices.
        land_choices = get_land_choices()

        expected_headers = []
        for _, name in land_choices:
            expected_headers.append(name)

        groups = get_detector_choices()

        actual_headers = []
        for header, _ in groups:
            actual_headers.append(header)

        assert actual_headers == expected_headers

    def test_detectors_sort_by_label_within_each_group(self) -> 'None':

        groups = get_detector_choices()

        for header, group in groups:

            labels = []
            for _, label in group:
                labels.append(label)

            assert labels == sorted(labels), f'Group `{header}` is not sorted by label'

# ################################################################################################################################
# ################################################################################################################################
