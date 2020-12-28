from django.test import TestCase


class ErrorPageTestCase(TestCase):
    def test_404(self):
        # Ensure that the 404 template is not itself causing an error. It
        # looks weird that we're checking for a 200 status code, but we're
        # actually fetching a view that just displays the template with a 200
        # status. If it's not 200 we have an error being caused by the 404
        # page!
        response = self.client.get('/404/')
        self.assertEqual(response.status_code, 200)

    def test_500(self):
        # Ensure that the 404 template is not itself causing an error. It
        # looks weird that we're checking for a 200 status code, but we're
        # actually fetching a view that just displays the template with a 200
        # status. If it's not 200 we have an error being caused by the 404 page!
        response = self.client.get('/500/')
        self.assertEqual(response.status_code, 200)
