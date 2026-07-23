from organizer.io import safe_move


def test_safe_move_creates_unique_name(tmp_path):
    src_dir = tmp_path / "src"
    dst_dir = tmp_path / "dst"
    src_dir.mkdir()
    dst_dir.mkdir()

    src_file = src_dir / "file.txt"
    src_file.write_text("hello")

    dest_file = dst_dir / "file.txt"

    # First move should place file at dst/file.txt
    final1, moved1 = safe_move(src_file, dest_file)
    assert moved1 is True
    assert final1.exists()
    assert final1.name == "file.txt"

    # Create another source file with same name
    src_file2 = src_dir / "file.txt"
    src_file2.write_text("world")

    final2, moved2 = safe_move(src_file2, dest_file)
    assert moved2 is True
    assert final2.exists()
    assert final2.name != "file.txt"

    # Contents match expectations
    assert final1.read_text() in ("hello", "world")
