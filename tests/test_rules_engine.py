from organizer.engine import rules as rules_module


def test_default_rules_loads():
    defaults = rules_module.load_default_rules()
    assert isinstance(defaults, list)


def test_find_category_for_extension():
    rules = [
        {"folder": "Images", "extensions": [".jpg", ".png"]},
        {"folder": "Docs", "extensions": [".pdf"]},
    ]
    assert rules_module.find_category_for_extension(rules, ".jpg") == "Images"
    assert rules_module.find_category_for_extension(rules, ".PDF") == "Docs"
    assert rules_module.find_category_for_extension(rules, ".unknown") == "Others"
