

from typing import Dict, Any, Optional, Union, List
category_histogram : Optional[Dict[str, int]] = None
class CategoryCounter(dict):
    """A custom dictionary to count occurrences of budget categories."""
    def __missing__(self, key):
        self[key] = 0
        return 0
    def count(self, key: str) -> str:
        """Increment the count for key, return key."""
        self[key] += 1
        return key

def clear_category_histogram():
    """Clear the category histogram."""
    global category_histogram
    category_histogram = CategoryCounter()
    return category_histogram


if __name__ == "__main__":
    try:
        ch = clear_category_histogram()
        ci = "Consumable Goods"
        food = '.'.join([ci,"food"])
        print(f"{food} = {ch[food]}") 
        print(f"{ci} = {ch[ci]}") 
        ch.count(ci)
        print(f"{ci} = {ch[ci]}")
        ch.count("Consumable Goods")
        print(f"{ci} = {ch[ci]}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

exit(0)


