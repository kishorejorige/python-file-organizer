def test_import_main():
    from organizer.main import main

    assert callable(main)