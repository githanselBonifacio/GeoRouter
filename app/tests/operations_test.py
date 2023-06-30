import unittest

from utils.operations import swap_list_items, change_list_items


class OperationsTest(unittest.TestCase):
    def test_swap_list_items(self):
        lst = [[1, 2, 3, 4], [5, 6, 7], [8, 9, 10], [11, 12]]
        response = [[1, 2, 3, 4], [5, 6, 12], [8, 9, 10], [11, 7]]
        self.assertEqual(
            swap_list_items(lst, (1, 2), (3, 1)),
            response
        )

    def test_change_list_items(self):
        lst = [[1, 2, 3, 4], [5, 6, 7], [8, 9, 10], [11, 12]]
        response = [[1, 2, 3, 4], [5, 6], [8, 9, 10], [11, 12, 7]]
        self.assertEqual(
            change_list_items(lst, (1, 2), (3, 1)),
            response
        )


if __name__ == '__main__':
    unittest.main()
