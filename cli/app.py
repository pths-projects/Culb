from typer import Typer

app = Typer(name="CLI helper")

@app.command("test")
def test_cli():
    """Простая тестовая команда"""
    print("✅ CLI работает!")python cli/db_operations.py --help


if __name__ == "__main__":
    app()