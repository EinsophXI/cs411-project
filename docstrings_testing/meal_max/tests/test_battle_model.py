import pytest

from meal_max.models.battle_model import BattleModel
from meal_max.models.kitchen_model import Meal


#Ignore all comments
@pytest.fixture()
def battle_model():
    """Fixture to provide a new instance of BattleModel for each test."""
    return BattleModel()

@pytest.fixture
def mock_update_play_count(mocker):
    """Mock the update_play_count function for testing purposes."""
    return mocker.patch("meal_max.models.battle_model.update_meal_stats")

"""Fixtures providing sample songs for the tests."""
@pytest.fixture
def sample_meal1():
    return Meal(1, "Ratatouille", "****", 5.40, "LOW")

@pytest.fixture
def sample_meal2():
    return Meal(2, "Beef Wellington", "*****", 35.10, "HIGH")

@pytest.fixture
def sample_battle(sample_meal1, sample_meal2):
    return [sample_meal1, sample_meal2]

def test_prep_combatant(battle_model, sample_meal1):
    """Test adding a song to the playlist."""
    battle_model.prep_combatant(sample_meal1)
    assert len(battle_model.combatants) == 1
    assert battle_model.combatants[0].meal == 'Ratatouille'

def test_not_enough_contestants(battle_model, sample_meal1):
    battle_model.prep_combatant(sample_meal1)
    assert len(battle_model.combatants) == 1
    with pytest.raises(ValueError, match="Two combatants must be prepped for a battle."):
        battle_model.battle()

def test_too_many_meals(battle_model, sample_battle, sample_meal1):
    battle_model.combatants.extend(sample_battle)
    assert len(battle_model.combatants) == 2
    with pytest.raises(ValueError, match="Combatant list is full, cannot add more combatants."):
        battle_model.prep_combatant(sample_meal1)



def test_clear_combatants(battle_model, sample_battle):
    battle_model.combatants.extend(sample_battle)
    assert len(battle_model.combatants) == 2
    battle_model.clear_combatants()
    assert len(battle_model.combatants) == 0

##################################################
# Song Retrieval Test Cases
##################################################

def test_get_battle_score(battle_model, sample_battle):
    """Test successfully retrieving a song from the playlist by track number."""
    battle_model.combatants.extend(sample_battle)
    assert battle_model.get_battle_score(sample_battle[0]) == 18.6
    assert battle_model.get_battle_score(sample_battle[1]) == 174.5


def test_get_all_meals(battle_model, sample_battle):
    """Test successfully retrieving all songs from the playlist."""
    battle_model.combatants.extend(sample_battle)

    all_meals = battle_model.get_combatants()
    assert len(all_meals) == 2
    assert all_meals[0].id == 1
    assert all_meals[1].id == 2

def test_battle(battle_model, sample_battle):
    battle_model.combatants.extend(sample_battle)
    assert battle_model.battle() == "Beef Wellington" or "Ratatouille"