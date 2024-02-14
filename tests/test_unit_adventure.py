import pytest, os, json
from osrlib.adventure import Adventure
from osrlib.dungeon import Dungeon
from osrlib.party import Party
from osrlib.enums import OpenAIModelVersion
from osrlib.utils import logger
import osrlib.osrlib_pb2 as protobufs

@pytest.fixture
def sample_adventure() -> Adventure:
    # Create a small adventure with a couple dungeons
    dungeon1 = Dungeon.get_random_dungeon("Random Dungeon 1", "First-level dungeon for test_unit_adventure.py.", num_locations=2, level=1, openai_model=OpenAIModelVersion.NONE)
    dungeon2 = Dungeon.get_random_dungeon("Random Dungeon 2", "Second-level dungeon for test_unit_adventure.py.", num_locations=2, level=2, openai_model=OpenAIModelVersion.NONE)
    return Adventure(name="Test Adventure", description="A small test adventure.", dungeons=[dungeon1, dungeon2])

def test_adventure_to_dict(sample_adventure):
    default_party = Party.get_default_party()
    sample_adventure.set_active_party(default_party)
    sample_adventure.set_active_dungeon(sample_adventure.dungeons[0])

    adventure_dict = sample_adventure.to_dict()

    # Verify that the adventure attributes are correctly serialized
    assert adventure_dict["name"] == "Test Adventure"
    assert adventure_dict["description"] == "A small test adventure."
    assert len(adventure_dict["dungeons"]) == 2
    assert adventure_dict["active_dungeon"]["name"] == sample_adventure.dungeons[0].name
    assert adventure_dict["active_party"]["name"] == default_party.name

def test_adventure_from_dict(sample_adventure):
    default_party = Party.get_default_party()
    sample_adventure.set_active_party(default_party)
    sample_adventure.set_active_dungeon(sample_adventure.dungeons[0])

    adventure_dict = sample_adventure.to_dict()

    # Deserialize the dictionary back into an Adventure instance
    rehydrated_adventure = Adventure.from_dict(adventure_dict)

    # Verify that the rehydrated adventure has the same attributes as the original
    assert rehydrated_adventure.name == sample_adventure.name
    assert rehydrated_adventure.description == sample_adventure.description
    assert len(rehydrated_adventure.dungeons) == len(sample_adventure.dungeons)
    assert rehydrated_adventure.active_dungeon.name == sample_adventure.dungeons[0].name
    assert rehydrated_adventure.active_party.name == default_party.name

def test_save_adventure(sample_adventure, tmp_path):
    """
    Test that an adventure can be successfully saved to a JSON file.
    """
    default_party = Party.get_default_party()
    sample_adventure.set_active_party(default_party)
    sample_adventure.set_active_dungeon(sample_adventure.dungeons[0])

    # Save the adventure to a temporary file
    file_path = sample_adventure.save_adventure(file_path=str(tmp_path / "test_adventure.json"))

    # Verify that the file exists
    assert os.path.exists(file_path)

    # Verify the contents of the file
    with open(file_path, "r") as file:
        data = json.load(file)
        assert data["name"] == "Test Adventure"
        assert data["description"] == "A small test adventure."

def test_load_adventure(sample_adventure, tmp_path):
    """
    Test that an adventure can be successfully loaded from a JSON file.
    """
    default_party = Party.get_default_party()
    sample_adventure.set_active_party(default_party)
    sample_adventure.set_active_dungeon(sample_adventure.dungeons[0])

    # Save the adventure to a temporary file
    file_path = sample_adventure.save_adventure(file_path=str(tmp_path / "test_adventure.json"))

    # Load the adventure from the file
    loaded_adventure = Adventure.load_adventure(file_path=file_path)

    # Verify that the loaded adventure matches the original
    assert loaded_adventure.name == sample_adventure.name
    assert loaded_adventure.description == sample_adventure.description
    assert len(loaded_adventure.dungeons) == len(sample_adventure.dungeons)
    assert loaded_adventure.active_dungeon.name == sample_adventure.dungeons[0].name
    assert loaded_adventure.active_party.name == default_party.name

def test_adventure_proto():
    adventure_proto = protobufs.Adventure()
    adventure_proto.name = "Proto Adventure"
    logger.debug(adventure_proto.name)
