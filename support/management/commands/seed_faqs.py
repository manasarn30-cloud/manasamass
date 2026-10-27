from django.core.management.base import BaseCommand
from support.models import FAQ


class Command(BaseCommand):
    help = 'Seeds initial Frequently Asked Questions (FAQs) into the SQL database.'

    def handle(self, *args, **options):
        faqs_data = [
            {
                "question": "How do I create an account?",
                "answer": "To create an account, click the 'Sign In' or 'Sign Up' button in the upper right navigation bar. On the registration page, enter a unique username, your valid email address, and a secure password of at least 8 characters. Click 'Create Account' to immediately access personalized features like My List.",
                "category": "Account & Authentication",
                "keywords": "register, registration, create account, sign up, join, new user, signup",
                "display_order": 1
            },
            {
                "question": "How do I sign in?",
                "answer": "Click the 'Sign In' link in the top right corner of the navigation bar. You can authenticate using either your registered username or your email address along with your password. If credentials match, you will be redirected to your dashboard.",
                "category": "Account & Authentication",
                "keywords": "login, sign in, log in, signin, authenticate, username, email",
                "display_order": 2
            },
            {
                "question": "What should I do if my password is incorrect?",
                "answer": "If you receive an invalid password alert, double-check Caps Lock and keyboard language settings. Ensure your username or email matches your registered details. If you cannot remember your password, you can contact our support team or file a ticket through the Support page to request assistance.",
                "category": "Account & Authentication",
                "keywords": "password, incorrect password, reset, forgot password, wrong password, recovery",
                "display_order": 3
            },
            {
                "question": "How do I log out?",
                "answer": "Click on your profile avatar or username in the top right navigation bar to open the user menu, then click 'Log Out'. For security, log out requests are submitted via HTTP POST to prevent accidental session termination.",
                "category": "Account & Authentication",
                "keywords": "logout, log out, sign out, exit, end session",
                "display_order": 4
            },
            {
                "question": "How do I search for movies?",
                "answer": "Click on 'Discover' or the search icon in the navigation bar. Enter any keywords from the title into the search bar. The system will filter available movies dynamically in real-time.",
                "category": "Streaming & Playback",
                "keywords": "search, find, look up, search bar, query, discover movies",
                "display_order": 5
            },
            {
                "question": "How do I filter movies by genre?",
                "answer": "Navigate to the 'Discover' page. Above the movie grid, you will find interactive genre filter chips (such as Action, Sci-Fi, Drama, Comedy, Thriller). Clicking a chip instantly narrows the catalog to movies matching that genre.",
                "category": "Streaming & Playback",
                "keywords": "filter, genre, category, action, comedy, sci-fi, drama, thriller",
                "display_order": 6
            },
            {
                "question": "How do I add a movie to My List?",
                "answer": "You must be signed in to use My List. On any movie card or detail page, click the 'Add to List' (+ icon) button. The movie will immediately be saved to your private SQL-backed library, and the button will update to 'In My List'.",
                "category": "Lists & Navigation",
                "keywords": "my list, add to list, save movie, watchlist, favorite, bookmark",
                "display_order": 7
            },
            {
                "question": "How do I remove a movie from My List?",
                "answer": "Navigate to 'My List' from the top navigation bar. Click the 'Remove' button on the movie card you wish to delete. You can also toggle the button off directly on the movie's detail page.",
                "category": "Lists & Navigation",
                "keywords": "remove movie, delete from list, remove from my list, unbookmark",
                "display_order": 8
            },
            {
                "question": "Why is a movie poster not loading?",
                "answer": "Poster images load through external content distribution networks (such as TMDB CDN) or local assets. If your network blocks third-party CDNs or has a high packet loss, posters may take longer or display our high-contrast fallback artwork. Refreshing the page often resolves temporary network glitches.",
                "category": "Platform Errors & Status Codes",
                "keywords": "poster, image broken, poster not loading, artwork missing, thumbnail",
                "display_order": 9
            },
            {
                "question": "What happens if the movie API is unavailable?",
                "answer": "StreamFlix includes an intelligent local fallback architecture. If the third-party TMDB API experiences downtime, rate limits, or connectivity timeouts (5-second threshold), StreamFlix seamlessly transitions to our curated local SQL movie dataset so your browsing experience is never interrupted.",
                "category": "Platform Errors & Status Codes",
                "keywords": "tmdb, api unavailable, fallback, api error, movie api down, timeout",
                "display_order": 10
            },
            {
                "question": "Why am I seeing a 404 error?",
                "answer": "An HTTP 404 (Not Found) status indicates that the URL you requested does not exist on our server. This typically happens due to a mistyped web address, an expired link, or a title that has been reorganized. Click 'Return Home' or ask our Assistant for assistance.",
                "category": "Platform Errors & Status Codes",
                "keywords": "404, not found, page not found, missing page, broken link, error 404",
                "display_order": 11
            },
            {
                "question": "What does a 500 error mean?",
                "answer": "An HTTP 500 (Internal Server Error) code means our web server encountered an unexpected situation that prevented it from fulfilling your request. Our automated logging captures these occurrences for immediate developer review. Try refreshing in a few moments.",
                "category": "Platform Errors & Status Codes",
                "keywords": "500, server error, internal server error, crash, error 500, broken server",
                "display_order": 12
            },
            {
                "question": "What does a 401 error mean?",
                "answer": "An HTTP 401 (Unauthorized) response means that the requested resource requires user authentication. To resolve this, simply sign in with your StreamFlix credentials or create a new account.",
                "category": "Platform Errors & Status Codes",
                "keywords": "401, unauthorized, unauthenticated, login required, error 401",
                "display_order": 13
            },
            {
                "question": "What is error 460?",
                "answer": "Error 460 is a custom StreamFlix application diagnostic convention (not a standard RFC HTTP status). It represents an internal diagnostic exception or simulation triggered for support triage and resilience verification.",
                "category": "Platform Errors & Support",
                "keywords": "460, error 460, streamflix error, diagnostic error, status 460, custom error",
                "display_order": 14
            },
            {
                "question": "How do I create a support ticket?",
                "answer": "You can create a support ticket at any time by visiting the 'Support' page and filling out the ticket form. Alternatively, if our AI Chatbot Assistant is unable to answer your inquiry, it will offer to open a support ticket for you automatically.",
                "category": "Support & Technical Diagnostics",
                "keywords": "ticket, support ticket, help desk, contact support, open ticket, report issue",
                "display_order": 15
            },
            {
                "question": "How is my chatbot conversation handled?",
                "answer": "Your conversation with the StreamFlix Assistant is stored securely in MongoDB for session persistence, diagnostic review, and service improvement. We never log sensitive user credentials, payment details, or passwords. Conversation records are kept strictly confidential.",
                "category": "Support & Technical Diagnostics",
                "keywords": "chatbot, privacy, conversation log, mongodb, data handling, assistant history",
                "display_order": 16
            },
            {
                "question": "What are error codes 403, 429, and 503?",
                "answer": "403 (Forbidden) means access is denied even if authenticated (e.g. attempting to view someone else's ticket). 429 (Too Many Requests) indicates rate limiting due to too many rapid requests. 503 (Service Unavailable) indicates the server is undergoing temporary maintenance or capacity overload.",
                "category": "Platform Errors & Status Codes",
                "keywords": "403, 429, 503, forbidden, rate limit, too many requests, service unavailable",
                "display_order": 17
            },
            {
                "question": "Does StreamFlix host full-length movie files?",
                "answer": "No. StreamFlix is an editorial streaming portal and discovery application. We provide verified trailers, official metadata, ratings, synopses, and direct links through TMDB and official studios rather than redistributing copyrighted video streams.",
                "category": "Streaming & Playback",
                "keywords": "full movie, stream, copyright, video player, license, watch movie",
                "display_order": 18
            }
        ]

        count = 0
        for item in faqs_data:
            faq, created = FAQ.objects.update_or_create(
                question=item["question"],
                defaults={
                    "answer": item["answer"],
                    "category": item["category"],
                    "keywords": item["keywords"],
                    "display_order": item["display_order"],
                    "is_active": True,
                }
            )
            count += 1

        self.stdout.write(self.style.SUCCESS(f"Successfully seeded {count} FAQs into the database."))
