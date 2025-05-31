# main.py (at project root)
import sys
from src.budman_app.budman_app import BudManApp
def main():
    """Main entry point for the Budget Manager application."""
    try:
        app = BudManApp()
        app.run()  # Start the application
    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
    