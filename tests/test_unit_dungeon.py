from random import randint, sample, choice
import json
import pytest
from osrlib.dungeon import Dungeon, Location, Exit, Direction, LocationNotFoundError
from osrlib.encounter import Encounter

# --- Test Exit class ---


def test_exit_initialization():
    exit_north = Exit(Direction.NORTH, 1)
    assert exit_north.direction == Direction.NORTH
    assert exit_north.destination == 1
    assert exit_north.locked == False


def test_exit_lock_unlock():
    exit_north = Exit(Direction.NORTH, 1)
    exit_north.lock()
    assert exit_north.locked == True
    exit_north.unlock()
    assert exit_north.locked == False


# --- Test Location class ---


def test_location_initialization():
    exit_north = Exit(Direction.NORTH, 1)
    encounter = Encounter()  # TODO: Set this up with real encounter
    location = Location(1, 10, 10, [exit_north], ["keyword1"], encounter)

    assert location.id == 1
    assert location.dimensions == {"width": 10, "length": 10}
    assert location.exits == [exit_north]
    assert location.keywords == ["keyword1"]
    assert location.encounter == encounter


def test_location_json():
    # Create an Exit object
    exit1 = Exit(Direction.NORTH, 2)
    exit2 = Exit(Direction.SOUTH, 1)

    # Create a Location object
    location = Location(
        id=1, width=10, length=10, exits=[exit1, exit2], keywords=["test", "location"]
    )

    # Get the JSON representation
    location_json = location.json

    # Parse it back to Python object
    location_dict = json.loads(location_json)

    # Validate individual fields
    assert location_dict["id"] == 1
    assert location_dict["dimensions"]["width"] == 10
    assert location_dict["dimensions"]["length"] == 10
    assert location_dict["keywords"] == ["test", "location"]

    # Validate exits
    assert len(location_dict["exits"]) == 2
    assert location_dict["exits"][0]["direction"] == "N"
    assert location_dict["exits"][0]["destination"] == 2
    assert location_dict["exits"][0]["locked"] == False

    # Validate that 'encounter' is None
    assert location_dict["encounter"] is None


# --- Test Dungeon class ---


def test_dungeon_initialization():
    exit_north = Exit(Direction.NORTH, 1)
    encounter = (
        Encounter()
    )  # You would set this up properly according to your Encounter class
    location1 = Location(1, 10, 10, [exit_north], ["keyword1"], encounter)
    location2 = Location(2, 6, 6, [], ["keyword2"], None)
    dungeon = Dungeon("Test Dungeon", "A test dungeon.", [location1, location2])

    assert dungeon.name == "Test Dungeon"
    assert dungeon.description == "A test dungeon."
    assert dungeon.locations == [location1, location2]


def test_set_start_location():
    exit1 = Exit(Direction.NORTH, 2)
    location1 = Location(1, exits=[exit1])
    dungeon = Dungeon(locations=[location1])

    with pytest.raises(LocationNotFoundError):
        dungeon.set_start_location(99)

    start_location = dungeon.set_start_location(1)
    assert start_location.id == 1


def test_move():
    exit1 = Exit(Direction.NORTH, 2)
    exit2 = Exit(Direction.SOUTH, 1)
    location1 = Location(1, exits=[exit1])
    location2 = Location(2, exits=[exit2])
    dungeon = Dungeon(locations=[location1, location2])
    dungeon.set_start_location(1)

    new_location = dungeon.move(Direction.NORTH)
    assert new_location.id == 2

    new_location = dungeon.move(Direction.SOUTH)
    assert new_location.id == 1

    assert dungeon.move(Direction.EAST) is None


def test_random_dungeon():
    # Create a random dungeon
    random_dungeon = Dungeon.get_random_dungeon(num_locations=20)

    # Validate Dungeon
    assert random_dungeon.validate_location_connections()
