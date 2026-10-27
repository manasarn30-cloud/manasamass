from django.test import TestCase, Client, override_settings
from django.urls import reverse


class MonitoringAndErrorHandlingTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_health_check_endpoint_returns_json(self):
        response = self.client.get(reverse('health_check'))
        self.assertIn(response.status_code, [200, 503])
        data = response.json()
        self.assertIn('status', data)
        self.assertIn('checks', data)
        self.assertIn('django', data['checks'])
        self.assertIn('sql_database', data['checks'])
        self.assertIn('mongodb', data['checks'])
        self.assertIn('tmdb_api', data['checks'])

    def test_invalid_url_returns_http_404_status(self):
        # Testing real 404 behavior by requesting an invalid path
        response = self.client.get('/this-path-does-not-exist-xyz999/')
        self.assertEqual(response.status_code, 404)
        # Custom 404 page content check
        self.assertContains(response, "went off the grid", status_code=404)
        self.assertContains(response, "Ask the Assistant", status_code=404)

    def test_custom_error_pages_render_and_offer_assistant(self):
        test_codes = [400, 401, 403, 404, 429, 460, 500, 503]
        for code in test_codes:
            response = self.client.get(reverse('test_error', args=[code]))
            self.assertEqual(response.status_code, code, f"Test error view failed for code {code}")
            # Ensure "Ask the Assistant" or assistant trigger exists on error page
            self.assertContains(
                response,
                "Assistant",
                status_code=code,
                msg_prefix=f"Error {code} missing assistant button"
            )

    def test_request_logging_middleware_adds_request_id(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('X-Request-ID', response.headers)
        self.assertGreater(len(response.headers['X-Request-ID']), 0)
