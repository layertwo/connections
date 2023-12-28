from connections.model import Coordinates, convert_airport_to_coords


def test_convert_airport_to_coords():
    coords = convert_airport_to_coords("SEA")
    assert coords == Coordinates(latitude=47.449, longitude=-122.309306)
