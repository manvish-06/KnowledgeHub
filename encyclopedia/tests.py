from django.test import TestCase
from django.test import TestCase


class WikiTests(TestCase):

    def test_home_page(self):

        response = self.client.get("/")

        self.assertEqual(
            response.status_code,
            200
        )

class SearchTests(TestCase):

    def test_search_page(self):

        response = self.client.get(
            "/search/?q=Python"
        )

        self.assertEqual(
            response.status_code,
            200
        )

