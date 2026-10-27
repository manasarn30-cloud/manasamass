import json
from unittest.mock import patch
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from support.models import FAQ, SupportTicket
from support.assistant import detect_error_code, format_error_explanation, match_faq, process_user_message


class SupportAndChatbotTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user('alice', 'alice@example.com', 'Pass1234!')
        self.user2 = User.objects.create_user('bob', 'bob@example.com', 'Pass1234!')

        self.faq1 = FAQ.objects.create(
            question="How do I add a movie to My List?",
            answer="Click the '+' button on any movie card or detail page.",
            category="Lists & Navigation",
            keywords="my list, add, save movie"
        )
        self.faq2 = FAQ.objects.create(
            question="Why am I seeing a 404 error?",
            answer="An HTTP 404 status indicates that the URL requested does not exist.",
            category="Platform Errors & Status Codes",
            keywords="404, not found, broken link"
        )

    def test_faqs_retrieved_from_sql(self):
        response = self.client.get(reverse('faq'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "How do I add a movie to My List?")
        self.assertContains(response, "Why am I seeing a 404 error?")

    def test_faq_search_filters_correctly(self):
        response = self.client.get(reverse('faq'), {'q': '404'})
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.faq2, response.context['faqs'])
        self.assertNotIn(self.faq1, response.context['faqs'])

    def test_all_eight_error_codes_explained(self):
        required_codes = ["400", "401", "403", "404", "429", "460", "500", "503"]
        for code in required_codes:
            detected = detect_error_code(f"What does error {code} mean?")
            self.assertEqual(detected, code, f"Failed to detect error code {code}")
            explanation = format_error_explanation(code)
            self.assertIsNotNone(explanation, f"No explanation for code {code}")
            self.assertIn("What it means:", explanation)
            self.assertIn("Common causes:", explanation)
            self.assertIn("What you can try:", explanation)

    def test_faq_matching_accuracy(self):
        faq, score = match_faq("How can I add movies to my list?")
        self.assertIsNotNone(faq)
        self.assertEqual(faq.id, self.faq1.id)
        self.assertGreater(score, 0.4)

    def test_chatbot_answers_faq(self):
        response = self.client.post(
            reverse('chatbot_api'),
            data=json.dumps({
                'message': 'How do I add a movie to My List?',
                'conversation_id': 'test_conv_123'
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['type'], 'faq_answer')
        self.assertIn('Click the \'+\' button', data['reply'])

    def test_chatbot_explains_error_460(self):
        response = self.client.post(
            reverse('chatbot_api'),
            data=json.dumps({
                'message': 'What is error 460?',
                'conversation_id': 'test_conv_123'
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['type'], 'error_explanation')
        self.assertIn('460', data['reply'])
        self.assertIn('StreamFlix', data['reply'])

    def test_chatbot_offers_ticket_for_unknown_question(self):
        response = self.client.post(
            reverse('chatbot_api'),
            data=json.dumps({
                'message': 'How do I bake a chocolate cake with quantum physics?',
                'conversation_id': 'test_conv_123'
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['type'], 'ticket_offer')
        self.assertTrue(data['ticket_offer'])

    def test_chatbot_ticket_creation_confirmation(self):
        self.client.login(username='alice', password='Pass1234!')
        response = self.client.post(
            reverse('chatbot_api'),
            data=json.dumps({
                'message': 'Yes, please open a support ticket for this issue',
                'conversation_id': 'test_conv_123',
                'state': 'ticket_offered'
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['type'], 'ticket_created')
        self.assertTrue(data['ticket_ref'].startswith('SF-TICK-'))
        self.assertTrue(SupportTicket.objects.filter(reference_number=data['ticket_ref']).exists())

    def test_support_ticket_creation_via_form(self):
        self.client.login(username='alice', password='Pass1234!')
        response = self.client.post(reverse('create_ticket'), {
            'subject': 'Subtitle audio sync issue',
            'category': 'Streaming & Playback',
            'priority': 'Medium',
            'description': 'The audio seems 2 seconds ahead of subtitles on Interstellar.'
        })
        self.assertEqual(response.status_code, 302)
        ticket = SupportTicket.objects.filter(subject='Subtitle audio sync issue').first()
        self.assertIsNotNone(ticket)
        self.assertEqual(ticket.user, self.user1)
        self.assertTrue(ticket.reference_number.startswith('SF-TICK-'))

    def test_support_ticket_privacy_prevent_unauthorized_access(self):
        ticket = SupportTicket.objects.create(
            user=self.user1,
            subject='Alice Private Issue',
            description='This belongs to Alice only.'
        )

        # Alice can view her ticket
        self.client.login(username='alice', password='Pass1234!')
        response = self.client.get(reverse('ticket_detail', args=[ticket.reference_number]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Alice Private Issue')

        # Bob attempts to view Alice's ticket -> 403 Forbidden!
        self.client.login(username='bob', password='Pass1234!')
        response = self.client.get(reverse('ticket_detail', args=[ticket.reference_number]))
        self.assertEqual(response.status_code, 403)

    def test_chatbot_feedback_submission(self):
        response = self.client.post(
            reverse('chatbot_feedback'),
            data=json.dumps({
                'conversation_id': 'test_conv_123',
                'message_id': 'msg_001',
                'rating': 'helpful',
                'feedback_text': 'Great answer!'
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])
