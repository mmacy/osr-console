from random import randint, sample, choice
import pytest
from osrlib.dungeon import Dungeon, Location, Exit, Direction
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
    encounter = Encounter() # TODO: Set this up with real encounter
    location = Location(1, 10, 10, [exit_north], ["keyword1"], encounter)

    assert location.id == 1
    assert location.dimensions == {"width": 10, "length": 10}
    assert location.exits == [exit_north]
    assert location.keywords == ["keyword1"]
    assert location.encounter == encounter

# --- Test Dungeon class ---

def test_dungeon_initialization():
    exit_north = Exit(Direction.NORTH, 1)
    encounter = Encounter()  # You would set this up properly according to your Encounter class
    location1 = Location(1, 10, 10, [exit_north], ["keyword1"], encounter)
    location2 = Location(2, 6, 6, [], ["keyword2"], None)
    dungeon = Dungeon("Test Dungeon", "A test dungeon.", [location1, location2])

    assert dungeon.name == "Test Dungeon"
    assert dungeon.description == "A test dungeon."
    assert dungeon.locations == [location1, location2]

# --- Test Dungeon integrity ---

# --- SUCCESS conditions
def test_locations_have_exits():
    loc1 = Location(1, 10, 10, [Exit(Direction.NORTH, 2)])
    loc2 = Location(2, 10, 10, [Exit(Direction.SOUTH, 1)])
    dungeon = Dungeon("Test Dungeon", "A test description", [loc1, loc2])
    assert dungeon.validate_locations_have_exits()

def test_exits_have_valid_destinations():
    loc1 = Location(1, 10, 10, [Exit(Direction.NORTH, 2)])
    loc2 = Location(2, 10, 10, [Exit(Direction.SOUTH, 1)])
    dungeon = Dungeon("Test Dungeon", "A test description", [loc1, loc2])
    assert dungeon.validate_exits_have_valid_destinations()

def test_unique_exit_directions():
    loc1 = Location(1, 10, 10, [Exit(Direction.NORTH, 2), Exit(Direction.SOUTH, 3)])
    loc2 = Location(2, 10, 10, [Exit(Direction.SOUTH, 1)])
    loc3 = Location(3, 10, 10, [Exit(Direction.NORTH, 1)])
    dungeon = Dungeon("Test Dungeon", "A test description", [loc1, loc2, loc3])
    assert dungeon.validate_unique_exit_directions()

def test_no_island_locations():
    loc1 = Location(1, 10, 10, [Exit(Direction.NORTH, 2)])
    loc2 = Location(2, 10, 10, [Exit(Direction.SOUTH, 1), Exit(Direction.EAST, 3)])
    loc3 = Location(3, 10, 10, [Exit(Direction.WEST, 2)])
    dungeon = Dungeon("Test Dungeon", "A test description", [loc1, loc2, loc3])
    assert dungeon.validate_no_island_locations()

def test_no_island_locations_2():
    loc1 = Location(1, 10, 10, [Exit(Direction.NORTH, 2)])
    loc2 = Location(2, 10, 10, [Exit(Direction.SOUTH, 1), Exit(Direction.EAST, 3)])
    loc3 = Location(3, 10, 10, [Exit(Direction.NORTH, 4), Exit(Direction.WEST, 2)])
    loc4 = Location(4, 10, 10, [Exit(Direction.SOUTH, 3)])
    dungeon = Dungeon("Test Dungeon", "A test description", [loc1, loc2, loc3, loc4])
    assert dungeon.validate_no_island_locations()

# --- FAILURE conditions
def test_locations_have_exits_failure():
    loc1 = Location(1, 10, 10, [])
    dungeon = Dungeon("Test Dungeon", "A test description", [loc1])
    assert not dungeon.validate_locations_have_exits()

def test_exits_have_valid_destinations_failure():
    loc1 = Location(1, 10, 10, [Exit(Direction.NORTH, 999)])
    dungeon = Dungeon("Test Dungeon", "A test description", [loc1])
    assert not dungeon.validate_exits_have_valid_destinations()

def test_unique_exit_directions_failure():
    loc1 = Location(1, 10, 10, [Exit(Direction.NORTH, 2), Exit(Direction.NORTH, 3)])
    loc2 = Location(2, 10, 10, [Exit(Direction.SOUTH, 1)])
    loc3 = Location(3, 10, 10, [Exit(Direction.SOUTH, 1)])
    dungeon = Dungeon("Test Dungeon", "A test description", [loc1, loc2, loc3])
    assert not dungeon.validate_unique_exit_directions()

def test_no_island_locations_failure():
    # Location ID 2 is an island - there are exits TO it, but not FROM it.
    loc1 = Location(1, 10, 10, [Exit(Direction.NORTH, 2)])
    loc2 = Location(2, 10, 10, [Exit(Direction.SOUTH, 3)]) # No exit back to ID 1
    loc3 = Location(3, 10, 10, [Exit(Direction.NORTH, 4)]) # No exit back to ID 2
    loc4 = Location(4, 10, 10, [Exit(Direction.SOUTH, 3)])
    dungeon = Dungeon("Test Dungeon", "A test description", [loc1, loc2, loc3, loc4])
    assert not dungeon.validate_no_island_locations()

@pytest.mark.flaky(reruns=5, reruns_delay=5)
def test_random_dungeon():

    # Initialize empty list for locations
    locations = []

    # Generate 10 locations
    for i in range(1, 11):
        width = randint(1, 5) * 10  # Size between 10 and 50, in increments of 10
        height = randint(1, 5) * 10  # Size between 10 and 50, in increments of 10
        keywords = ["placeholder1", "placeholder2", "placeholder3"]

        # Generate random exits
        possible_directions = list(Direction)
        num_exits = randint(1, len(possible_directions))  # At least one exit
        directions = sample(possible_directions, num_exits)

        exits = []
        for direction in directions:
            destination = randint(1, 10)  # Random destination ID between 1 and 10
            while destination == i:  # Ensure destination is not the same as the location itself
                destination = randint(1, 10)
            exits.append(Exit(direction, destination))

        location = Location(i, width, height, exits, keywords)
        locations.append(location)

    # Ensure all locations are reachable from each other
    for loc in locations:
        for exit in loc.exits:
            dest_id = exit.destination
            dest_location = next((l for l in locations if l.id == dest_id), None)

            # Determine the reverse direction (simplified to just NORTH and SOUTH for this example)
            reverse_direction = Direction.SOUTH if exit.direction == Direction.NORTH else Direction.NORTH

            # Check if there's an exit back to the original location
            if not any(e.destination == loc.id for e in dest_location.exits):

                # Check if there is already an exit in the reverse direction to avoid duplicates
                if not any(e.direction == reverse_direction for e in dest_location.exits):
                    dest_location.exits.append(Exit(reverse_direction, loc.id))

    # Initialize Dungeon
    dungeon = Dungeon("Sample Dungeon", "A randomly generated dungeon.", locations)

    # Validate Dungeon
    assert dungeon.validate_dungeon()
