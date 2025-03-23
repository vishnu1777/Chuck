class SortManager:
    """
    Handles sorting of inventory data based on different criteria.
    """

    def __init__(self, data):
        """
        Initialize with data to be sorted.
        :param data: List of dictionaries or objects that need sorting.
        """
        self.data = data

    def sort_by_lowest_price(self):
        """Sorts the data in ascending order based on price."""
        return sorted(self.data, key=lambda x: x.get("price", float("inf")))

    def sort_by_highest_price(self):
        """Sorts the data in descending order based on price."""
        return sorted(self.data, key=lambda x: x.get("price", float("-inf")), reverse=True)

    def sort_by_departure_time(self, ascending=True):
        """Sorts the data based on departure time."""
        return sorted(self.data, key=lambda x: x.get("departure_time"), reverse=not ascending)

    def execute_sort(self, method_name, **kwargs):
        """
        Dynamically calls the sorting method based on method_name.
        :param method_name: Name of the sorting method.
        :param kwargs: Additional arguments for sorting methods.
        """
        if hasattr(self, method_name) and callable(getattr(self, method_name)):
            return getattr(self, method_name)(**kwargs)
        else:
            raise AttributeError(f"❌ Sorting method '{method_name}' not found!")

# Example Usage
if __name__ == "__main__":
    sample_data = [
        {"price": 500, "departure_time": "10:00"},
        {"price": 300, "departure_time": "08:00"},
        {"price": 700, "departure_time": "12:00"},
    ]
    
    sorter = SortManager(sample_data)
    print("Sorted by lowest price:", sorter.sort_by_lowest_price())
    print("Sorted by highest price:", sorter.sort_by_highest_price())
    print("Sorted by departure time:", sorter.sort_by_departure_time(ascending=True))
