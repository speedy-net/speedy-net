from django.conf import settings as django_settings

if (django_settings.TESTS):
    from haversine import haversine, Unit

    from speedy.core.base.test.models import SiteTestCase


    class HaversineOnlyEnglishTestCase(SiteTestCase):
        def set_up(self):
            super().set_up()
            self.london = (51.5072, -0.1276)
            self.paris = (48.8566, 2.3522)
            self.frankfurt = (50.1109, 8.6821)
            self.san_francisco = (37.7749, -122.4194)
            self.seoul = (37.5665, 126.9780)
            self.sydney = (-33.8688, 151.2093)
            self.new_york = (40.7128, -74.0060)
            self.honolulu = (21.3099, -157.8581)
            self.tel_aviv = (32.0853, 34.7818)
            self.auckland = (-36.8509, 174.7645)
            self.herzliya = (32.1624, 34.8447)
            self.san_francisco_360 = (37.7749, -122.4194 + 360.0)  # Needs normalization.
            self.equator_point_1 = (0.0, 0.0)
            self.equator_point_2 = (0.0, 0.0 + 180.0)
            self.equator_point_3 = (0.0, 0.0 - 90.0)
            self.equator_point_4 = (0.0, 0.0 + 90.0)
            self.equator_point_5 = (0.0, 0.0 + 60.0)
            self.north_pole_1 = (90.0, 0.0)
            self.north_pole_2 = (90.0, 90.0)
            self.north_pole_3 = (90.0, 180.0)
            self.north_pole_4 = (90.0, -90.0)
            self.south_pole_1 = (-90.0, 0.0)
            self.south_pole_2 = (-90.0, 90.0)
            self.south_pole_3 = (-90.0, 180.0)
            self.south_pole_4 = (-90.0, -90.0)
            self.london_other_side_1 = (51.5072 * -1.0, -0.1276 + 180.0)
            self.london_other_side_2 = (51.5072 - 180.0, -0.1276)  # Needs normalization.
            self.london_other_side_3 = (51.5072 + 180.0, -0.1276)  # Needs normalization.

        def test_distance_between_locations_to_themselves(self):
            self.assertIs(expr1=(0.0 == haversine(point1=self.london, point2=self.london, unit=Unit.KILOMETERS)), expr2=True)
            self.assertIs(expr1=(0.0 == haversine(point1=self.paris, point2=self.paris, unit=Unit.KILOMETERS)), expr2=True)
            self.assertIs(expr1=(0.0 == haversine(point1=self.frankfurt, point2=self.frankfurt, unit=Unit.KILOMETERS)), expr2=True)
            self.assertIs(expr1=(0.0 == haversine(point1=self.san_francisco, point2=self.san_francisco, unit=Unit.KILOMETERS)), expr2=True)
            self.assertIs(expr1=(0.0 == haversine(point1=self.seoul, point2=self.seoul, unit=Unit.KILOMETERS)), expr2=True)
            self.assertIs(expr1=(0.0 == haversine(point1=self.sydney, point2=self.sydney, unit=Unit.KILOMETERS)), expr2=True)
            self.assertIs(expr1=(0.0 == haversine(point1=self.new_york, point2=self.new_york, unit=Unit.KILOMETERS)), expr2=True)
            self.assertIs(expr1=(0.0 == haversine(point1=self.honolulu, point2=self.honolulu, unit=Unit.KILOMETERS)), expr2=True)
            self.assertIs(expr1=(0.0 == haversine(point1=self.tel_aviv, point2=self.tel_aviv, unit=Unit.KILOMETERS)), expr2=True)
            self.assertIs(expr1=(0.0 == haversine(point1=self.auckland, point2=self.auckland, unit=Unit.KILOMETERS)), expr2=True)
            self.assertIs(expr1=(0.0 == haversine(point1=self.herzliya, point2=self.herzliya, unit=Unit.KILOMETERS)), expr2=True)

        def test_known_distance_between_locations(self):
            self.assertIs(expr1=(343.530 < haversine(point1=self.london, point2=self.paris, unit=Unit.KILOMETERS) < 343.531), expr2=True)
            self.assertIs(expr1=(343.530 < haversine(point1=self.paris, point2=self.london, unit=Unit.KILOMETERS) < 343.531), expr2=True)
            self.assertIs(expr1=(477.892 < haversine(point1=self.paris, point2=self.frankfurt, unit=Unit.KILOMETERS) < 477.893), expr2=True)
            self.assertIs(expr1=(8616.468 < haversine(point1=self.london, point2=self.san_francisco, unit=Unit.KILOMETERS) < 8616.469), expr2=True)
            self.assertIs(expr1=(8549.659 < haversine(point1=self.frankfurt, point2=self.seoul, unit=Unit.KILOMETERS) < 8549.660), expr2=True)
            self.assertIs(expr1=(16993.955 < haversine(point1=self.london, point2=self.sydney, unit=Unit.KILOMETERS) < 16993.956), expr2=True)
            self.assertIs(expr1=(16993.955 < haversine(point1=self.sydney, point2=self.london, unit=Unit.KILOMETERS) < 16993.956), expr2=True)
            self.assertIs(expr1=(11947.677 < haversine(point1=self.sydney, point2=self.san_francisco, unit=Unit.KILOMETERS) < 11947.678), expr2=True)
            self.assertIs(expr1=(4129.091 < haversine(point1=self.new_york, point2=self.san_francisco, unit=Unit.KILOMETERS) < 4129.092), expr2=True)
            self.assertIs(expr1=(5570.250 < haversine(point1=self.new_york, point2=self.london, unit=Unit.KILOMETERS) < 5570.251), expr2=True)
            self.assertIs(expr1=(5570.250 < haversine(point1=self.london, point2=self.new_york, unit=Unit.KILOMETERS) < 5570.251), expr2=True)
            self.assertIs(expr1=(11631.681 < haversine(point1=self.london, point2=self.honolulu, unit=Unit.KILOMETERS) < 11631.682), expr2=True)
            self.assertIs(expr1=(11963.489 < haversine(point1=self.frankfurt, point2=self.honolulu, unit=Unit.KILOMETERS) < 11963.490), expr2=True)
            self.assertIs(expr1=(13927.318 < haversine(point1=self.tel_aviv, point2=self.honolulu, unit=Unit.KILOMETERS) < 13927.319), expr2=True)
            self.assertIs(expr1=(3556.371 < haversine(point1=self.tel_aviv, point2=self.london, unit=Unit.KILOMETERS) < 3556.372), expr2=True)
            self.assertIs(expr1=(2156.016 < haversine(point1=self.auckland, point2=self.sydney, unit=Unit.KILOMETERS) < 2156.017), expr2=True)
            self.assertIs(expr1=(18336.325 < haversine(point1=self.auckland, point2=self.london, unit=Unit.KILOMETERS) < 18336.326), expr2=True)
            self.assertIs(expr1=(18336.325 < haversine(point1=self.london, point2=self.auckland, unit=Unit.KILOMETERS) < 18336.326), expr2=True)
            self.assertIs(expr1=(7076.238 < haversine(point1=self.auckland, point2=self.honolulu, unit=Unit.KILOMETERS) < 7076.239), expr2=True)
            self.assertIs(expr1=(10.420 < haversine(point1=self.tel_aviv, point2=self.herzliya, unit=Unit.KILOMETERS) < 10.421), expr2=True)

        def test_san_francisco_360_distances_raises_exception(self):
            with self.assertRaises(ValueError) as cm:
                self.assertIs(expr1=(-0.000001 < haversine(point1=self.san_francisco, point2=self.san_francisco_360, unit=Unit.KILOMETERS) < 0.000001), expr2=True)
            self.assertEqual(first=str(cm.exception), second="Longitude {longitude} is out of range [-180, 180]".format(longitude=self.san_francisco_360[1]))
            with self.assertRaises(ValueError) as cm:
                self.assertIs(expr1=(8616.468 < haversine(point1=self.london, point2=self.san_francisco_360, unit=Unit.KILOMETERS) < 8616.469), expr2=True)
            self.assertEqual(first=str(cm.exception), second="Longitude {longitude} is out of range [-180, 180]".format(longitude=self.san_francisco_360[1]))

        def test_san_francisco_360_distances_ok(self):
            self.assertIs(expr1=(-0.000001 < haversine(point1=self.san_francisco, point2=self.san_francisco_360, unit=Unit.KILOMETERS, normalize=True) < 0.000001), expr2=True)
            self.assertIs(expr1=(8616.468 < haversine(point1=self.london, point2=self.san_francisco_360, unit=Unit.KILOMETERS, normalize=True) < 8616.469), expr2=True)

        def test_distance_between_points_on_the_equator(self):
            self.assertIs(expr1=(20015.114 < haversine(point1=self.equator_point_1, point2=self.equator_point_2, unit=Unit.KILOMETERS) < 20015.115), expr2=True)  # Maximal distance on Earth.
            self.assertIs(expr1=(20015.114 < haversine(point1=self.equator_point_3, point2=self.equator_point_4, unit=Unit.KILOMETERS) < 20015.115), expr2=True)  # Maximal distance on Earth.
            self.assertIs(expr1=(6671.704 < haversine(point1=self.equator_point_1, point2=self.equator_point_5, unit=Unit.KILOMETERS) < 6671.705), expr2=True)  # One third of the maximal distance on Earth.
            self.assertIs(expr1=(10007.557 < haversine(point1=self.equator_point_1, point2=self.equator_point_4, unit=Unit.KILOMETERS) < 10007.558), expr2=True)  # Half of the maximal distance on Earth.

        def test_distance_between_poles(self):
            for north_pole in (self.north_pole_1, self.north_pole_2, self.north_pole_3, self.north_pole_4):
                self.assertIs(expr1=(-0.000001 < haversine(point1=self.north_pole_1, point2=north_pole, unit=Unit.KILOMETERS) < 0.000001), expr2=True)

            for south_pole in (self.south_pole_1, self.south_pole_2, self.south_pole_3, self.south_pole_4):
                self.assertIs(expr1=(-0.000001 < haversine(point1=self.south_pole_1, point2=south_pole, unit=Unit.KILOMETERS) < 0.000001), expr2=True)

            for north_pole in (self.north_pole_1, self.north_pole_2, self.north_pole_3, self.north_pole_4):
                for south_pole in (self.south_pole_1, self.south_pole_2, self.south_pole_3, self.south_pole_4):
                    self.assertIs(expr1=(20015.114 < haversine(point1=north_pole, point2=south_pole, unit=Unit.KILOMETERS) < 20015.115), expr2=True)  # Maximal distance on Earth.

            for north_pole in (self.north_pole_1, self.north_pole_2, self.north_pole_3, self.north_pole_4):
                for equator_point in (self.equator_point_1, self.equator_point_2, self.equator_point_3, self.equator_point_4, self.equator_point_5):
                    self.assertIs(expr1=(10007.557 < haversine(point1=north_pole, point2=equator_point, unit=Unit.KILOMETERS) < 10007.558), expr2=True)  # Half of the maximal distance on Earth.

            for south_pole in (self.south_pole_1, self.south_pole_2, self.south_pole_3, self.south_pole_4):
                for equator_point in (self.equator_point_1, self.equator_point_2, self.equator_point_3, self.equator_point_4, self.equator_point_5):
                    self.assertIs(expr1=(10007.557 < haversine(point1=equator_point, point2=south_pole, unit=Unit.KILOMETERS) < 10007.558), expr2=True)  # Half of the maximal distance on Earth.

        def test_london_other_side_distance_raises_exception(self):
            for london_other_side in (self.london_other_side_2, self.london_other_side_3):
                with self.assertRaises(ValueError) as cm:
                    self.assertIs(expr1=(-0.000001 < haversine(point1=self.london_other_side_1, point2=london_other_side, unit=Unit.KILOMETERS) < 0.000001), expr2=True)
                self.assertEqual(first=str(cm.exception), second="Latitude {latitude} is out of range [-90, 90]".format(latitude=london_other_side[0]))
                with self.assertRaises(ValueError) as cm:
                    self.assertIs(expr1=(20015.114 < haversine(point1=self.london, point2=london_other_side, unit=Unit.KILOMETERS) < 20015.115), expr2=True)  # Maximal distance on Earth.
                self.assertEqual(first=str(cm.exception), second="Latitude {latitude} is out of range [-90, 90]".format(latitude=london_other_side[0]))

        def test_london_other_side_distance_ok(self):
            for london_other_side in (self.london_other_side_1,):
                self.assertIs(expr1=(-0.000001 < haversine(point1=self.london_other_side_1, point2=london_other_side, unit=Unit.KILOMETERS) < 0.000001), expr2=True)
                self.assertIs(expr1=(20015.114 < haversine(point1=self.london, point2=london_other_side, unit=Unit.KILOMETERS) < 20015.115), expr2=True)  # Maximal distance on Earth.
            for london_other_side in (self.london_other_side_1, self.london_other_side_2, self.london_other_side_3):
                self.assertIs(expr1=(-0.000001 < haversine(point1=self.london_other_side_1, point2=london_other_side, unit=Unit.KILOMETERS, normalize=True) < 0.000001), expr2=True)
                self.assertIs(expr1=(20015.114 < haversine(point1=self.london, point2=london_other_side, unit=Unit.KILOMETERS, normalize=True) < 20015.115), expr2=True)  # Maximal distance on Earth.


