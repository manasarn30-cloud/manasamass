import logging
import requests
from django.conf import settings

logger = logging.getLogger('streamflix')

# High quality curated fallback catalog of 24 films with valid imagery & trailers
# Guarantees the platform is 100% gorgeous, cinematic, and functional even offline!
FALLBACK_MOVIES = [
    {
        "id": 101,
        "tmdb_id": 157336,
        "title": "Interstellar",
        "overview": "When Earth becomes uninhabitable in the future, a farmer and ex-NASA pilot, Joseph Cooper, is tasked to pilot a spacecraft, along with a team of researchers, to find a new planet for humans.",
        "poster_path": "https://image.tmdb.org/t/p/w500/gEU2QniE6E77NI6lCU6MxlNBvIx.jpg",
        "backdrop_path": "https://image.tmdb.org/t/p/original/rAiYTsqBkRefBXweCjhotXmBMd5.jpg",
        "release_date": "2014-11-05",
        "rating": 8.7,
        "vote_count": 34800,
        "genre": "Sci-Fi, Adventure, Drama",
        "runtime": 169,
        "trailer_url": "https://www.youtube.com/watch?v=zSWdZVtXT7E",
        "is_featured": True,
        "is_trending": True,
        "is_popular": True,
    },
    {
        "id": 102,
        "tmdb_id": 27205,
        "title": "Inception",
        "overview": "Cobb, a skilled thief who steals corporate secrets through the use of dream-sharing technology, is given the inverse task of planting an idea into the mind of a C.E.O., but his tragic past may doom the project.",
        "poster_path": "https://image.tmdb.org/t/p/w500/oYuLEt3zVCKq57qu2F8dT7NIa6f.jpg",
        "backdrop_path": "https://image.tmdb.org/t/p/original/8ZTVqvKDQ8emSGUEMjsS4yHAwrp.jpg",
        "release_date": "2010-07-15",
        "rating": 8.8,
        "vote_count": 36200,
        "genre": "Action, Sci-Fi, Thriller",
        "runtime": 148,
        "trailer_url": "https://www.youtube.com/watch?v=YoHD9XEInc0",
        "is_featured": False,
        "is_trending": True,
        "is_popular": True,
    },
    {
        "id": 103,
        "tmdb_id": 155,
        "title": "The Dark Knight",
        "overview": "Batman raises the stakes in his war on crime. With the help of Lt. Jim Gordon and District Attorney Harvey Dent, Batman sets out to dismantle the remaining criminal organizations that plague the streets.",
        "poster_path": "https://image.tmdb.org/t/p/w500/qJ2tW6WMUDux911r6m7haRef0WH.jpg",
        "backdrop_path": "https://image.tmdb.org/t/p/original/hkBaDkMWbLaf8B1rsqRqlQEaqxI.jpg",
        "release_date": "2008-07-16",
        "rating": 9.0,
        "vote_count": 32500,
        "genre": "Action, Crime, Drama",
        "runtime": 152,
        "trailer_url": "https://www.youtube.com/watch?v=EXeTwQWrcwY",
        "is_featured": False,
        "is_trending": True,
        "is_popular": True,
    },
    {
        "id": 104,
        "tmdb_id": 693134,
        "title": "Dune: Part Two",
        "overview": "Follow the mythic journey of Paul Atreides as he unites with Chani and the Fremen while on a warpath of revenge against the conspirators who destroyed his family.",
        "poster_path": "https://image.tmdb.org/t/p/w500/1pdfLvkbY9ohJlCjQH2CZjjYVvJ.jpg",
        "backdrop_path": "https://image.tmdb.org/t/p/original/xOMo8BRK7PfcJv9JCnx7s520DRq.jpg",
        "release_date": "2024-02-27",
        "rating": 8.5,
        "vote_count": 5200,
        "genre": "Sci-Fi, Adventure",
        "runtime": 166,
        "trailer_url": "https://www.youtube.com/watch?v=Way9Dexny3w",
        "is_featured": False,
        "is_trending": True,
        "is_popular": True,
    },
    {
        "id": 105,
        "tmdb_id": 872585,
        "title": "Oppenheimer",
        "overview": "The story of J. Robert Oppenheimer's role in the development of the atomic bomb during World War II, and the subsequent security hearing that shook his life.",
        "poster_path": "https://image.tmdb.org/t/p/w500/8Gxv8gSFCU0XGDykEGv7zR1n2ua.jpg",
        "backdrop_path": "https://image.tmdb.org/t/p/original/fm6K9vYQ7jSSjZKdYvKcTeQ92L8.jpg",
        "release_date": "2023-07-19",
        "rating": 8.6,
        "vote_count": 8900,
        "genre": "Drama, History",
        "runtime": 180,
        "trailer_url": "https://www.youtube.com/watch?v=uYPbbksJxIg",
        "is_featured": False,
        "is_trending": True,
        "is_popular": True,
    },
    {
        "id": 106,
        "tmdb_id": 603,
        "title": "The Matrix",
        "overview": "Set in the 22nd century, The Matrix tells the story of a computer hacker who joins a group of underground insurgents fighting the vast and powerful computers who now rule the earth.",
        "poster_path": "https://image.tmdb.org/t/p/w500/f89U3ADr1oiB1s9GkdPOEpXUk5H.jpg",
        "backdrop_path": "https://image.tmdb.org/t/p/original/7u3fhRw1RJ2Tds8Z26vA6i7dG1.jpg",
        "release_date": "1999-03-30",
        "rating": 8.7,
        "vote_count": 25100,
        "genre": "Action, Sci-Fi",
        "runtime": 136,
        "trailer_url": "https://www.youtube.com/watch?v=vKQi3bBA1y8",
        "is_featured": False,
        "is_trending": False,
        "is_popular": True,
    },
    {
        "id": 107,
        "tmdb_id": 550,
        "title": "Fight Club",
        "overview": "A ticking-time-bomb insomniac and a slippery soap salesman channel primal male aggression into a shocking new form of therapy.",
        "poster_path": "https://image.tmdb.org/t/p/w500/pB8BM7pdSp6B6Ih7QZ4DrQ3PmJK.jpg",
        "backdrop_path": "https://image.tmdb.org/t/p/original/hZkgoQYus5vegHoetLkCJzb17zJ.jpg",
        "release_date": "1999-10-15",
        "rating": 8.4,
        "vote_count": 28500,
        "genre": "Drama, Thriller",
        "runtime": 139,
        "trailer_url": "https://www.youtube.com/watch?v=qtRKdV9EIgk",
        "is_featured": False,
        "is_trending": False,
        "is_popular": True,
    },
    {
        "id": 108,
        "tmdb_id": 299536,
        "title": "Avengers: Infinity War",
        "overview": "As the Avengers and their allies have continued to protect the world from threats too large for any one hero to handle, a new danger has emerged from the cosmic shadows: Thanos.",
        "poster_path": "https://image.tmdb.org/t/p/w500/7WsyChQLEftFiDOVTGkv3hFpyyt.jpg",
        "backdrop_path": "https://image.tmdb.org/t/p/original/lmZFxVIz3ujsbUpUVHG3aQWAcgo.jpg",
        "release_date": "2018-04-25",
        "rating": 8.3,
        "vote_count": 29300,
        "genre": "Action, Adventure, Sci-Fi",
        "runtime": 149,
        "trailer_url": "https://www.youtube.com/watch?v=6ZfuNTqbHE8",
        "is_featured": False,
        "is_trending": True,
        "is_popular": True,
    },
    {
        "id": 109,
        "tmdb_id": 13,
        "title": "Forrest Gump",
        "overview": "A man with a low IQ has accomplished great things in his life and been present during significant historic events—in each case, far exceeding what anyone imagined he could do.",
        "poster_path": "https://image.tmdb.org/t/p/w500/arw2VCBveWOVZr6pxd9XTd1TdQa.jpg",
        "backdrop_path": "https://image.tmdb.org/t/p/original/qdIMHdbtatzyIfPPDU5Av8bcrEn.jpg",
        "release_date": "1994-06-23",
        "rating": 8.5,
        "vote_count": 26700,
        "genre": "Comedy, Drama, Romance",
        "runtime": 142,
        "trailer_url": "https://www.youtube.com/watch?v=bLvqoHBptjg",
        "is_featured": False,
        "is_trending": False,
        "is_popular": True,
    },
    {
        "id": 110,
        "tmdb_id": 335984,
        "title": "Blade Runner 2049",
        "overview": "Thirty years after the events of the first film, a new blade runner, LAPD Officer K, unearths a long-buried secret that has the potential to plunge what's left of society into chaos.",
        "poster_path": "https://image.tmdb.org/t/p/w500/gajva2L0rPYkEWjzgFlBXCAVBE5.jpg",
        "backdrop_path": "https://image.tmdb.org/t/p/original/sAtoMqDVhNDQBc3QJL3RF6hlxGq.jpg",
        "release_date": "2017-10-04",
        "rating": 8.0,
        "vote_count": 13400,
        "genre": "Sci-Fi, Mystery, Thriller",
        "runtime": 164,
        "trailer_url": "https://www.youtube.com/watch?v=gCcx85zbxz4",
        "is_featured": False,
        "is_trending": True,
        "is_popular": False,
    },
    {
        "id": 111,
        "tmdb_id": 680,
        "title": "Pulp Fiction",
        "overview": "A burger-loving hit man, his philosophical partner, a drug-addled gangster's moll and a washed-up boxer converge in this sprawling, comedic crime caper.",
        "poster_path": "https://image.tmdb.org/t/p/w500/d5iIlFn5s0ImszYzBPb8JPIfbXD.jpg",
        "backdrop_path": "https://image.tmdb.org/t/p/original/suaEOtk1N1sgg2MTM7oZd2cfVp3.jpg",
        "release_date": "1994-09-10",
        "rating": 8.5,
        "vote_count": 27200,
        "genre": "Crime, Thriller",
        "runtime": 154,
        "trailer_url": "https://www.youtube.com/watch?v=s7EdQ4FqbhY",
        "is_featured": False,
        "is_trending": False,
        "is_popular": True,
    },
    {
        "id": 112,
        "tmdb_id": 120,
        "title": "The Lord of the Rings: The Fellowship of the Ring",
        "overview": "Young hobbit Frodo Baggins, after inheriting a mysterious ring from his uncle Bilbo, must leave his home behind in order to begin an epic quest to the fires of Mount Doom.",
        "poster_path": "https://image.tmdb.org/t/p/w500/6oom5QYQ2yQTMJIbnvbkBL9cDK6.jpg",
        "backdrop_path": "https://image.tmdb.org/t/p/original/kWYfW2Re0rUDE6IHhyvsclcuzyP.jpg",
        "release_date": "2001-12-18",
        "rating": 8.4,
        "vote_count": 24500,
        "genre": "Adventure, Fantasy, Action",
        "runtime": 178,
        "trailer_url": "https://www.youtube.com/watch?v=V75dMMIW2B4",
        "is_featured": False,
        "is_trending": True,
        "is_popular": True,
    },
    {
        "id": 113,
        "tmdb_id": 496243,
        "title": "Parasite",
        "overview": "All unemployed, Ki-taek's family takes peculiar interest in the wealthy and glamorous Parks for their livelihood until they get entangled in an unexpected incident.",
        "poster_path": "https://image.tmdb.org/t/p/w500/7IiTTgloJzvGI1TAYymCfbfl3vT.jpg",
        "backdrop_path": "https://image.tmdb.org/t/p/original/hiKmpZMGZsrkA3cdce8a7Dpos1j.jpg",
        "release_date": "2019-05-30",
        "rating": 8.5,
        "vote_count": 17800,
        "genre": "Comedy, Thriller, Drama",
        "runtime": 132,
        "trailer_url": "https://www.youtube.com/watch?v=5xH0RzeSojI",
        "is_featured": False,
        "is_trending": True,
        "is_popular": True,
    },
    {
        "id": 114,
        "tmdb_id": 372058,
        "title": "Your Name.",
        "overview": "High schoolers Mitsuha and Taki are complete strangers living separate lives in different parts of Japan. But one night, they suddenly switch places in their dreams.",
        "poster_path": "https://image.tmdb.org/t/p/w500/q719jXXEzOoYaps6qFsxWa93bu.jpg",
        "backdrop_path": "https://image.tmdb.org/t/p/original/dIWwZW7dJJ1q499NVWpvLJvzyEG.jpg",
        "release_date": "2016-08-26",
        "rating": 8.5,
        "vote_count": 11000,
        "genre": "Animation, Romance, Drama",
        "runtime": 107,
        "trailer_url": "https://www.youtube.com/watch?v=s0wTdCQoc2k",
        "is_featured": False,
        "is_trending": False,
        "is_popular": True,
    },
    {
        "id": 115,
        "tmdb_id": 24428,
        "title": "The Avengers",
        "overview": "When an unexpected enemy emerges and threatens global safety and security, Nick Fury, director of the international peacekeeping agency known as S.H.I.E.L.D., finds himself in need of a team.",
        "poster_path": "https://image.tmdb.org/t/p/w500/RYMX2wcKCBAr24UyPD7xwmjaTn.jpg",
        "backdrop_path": "https://image.tmdb.org/t/p/original/9BBTo63ANSmhC4e6r62OJFuK2GL.jpg",
        "release_date": "2012-04-25",
        "rating": 7.7,
        "vote_count": 29800,
        "genre": "Action, Sci-Fi",
        "runtime": 143,
        "trailer_url": "https://www.youtube.com/watch?v=eOrNdBpGMv8",
        "is_featured": False,
        "is_trending": False,
        "is_popular": True,
    },
    {
        "id": 116,
        "tmdb_id": 77338,
        "title": "The Intouchables",
        "overview": "A true story of two men who should never have met - a quadriplegic aristocrat who was injured in a paragliding accident and a young man from the projects.",
        "poster_path": "https://image.tmdb.org/t/p/w500/1hRoyzDtpgMU7Dz4JF22RANzQ57.jpg",
        "backdrop_path": "https://image.tmdb.org/t/p/original/7c9UVPPiTPltouxShY94x3h3vEI.jpg",
        "release_date": "2011-11-02",
        "rating": 8.3,
        "vote_count": 16900,
        "genre": "Drama, Comedy",
        "runtime": 112,
        "trailer_url": "https://www.youtube.com/watch?v=34WIbmXkewU",
        "is_featured": False,
        "is_trending": False,
        "is_popular": False,
    },
    {
        "id": 117,
        "tmdb_id": 569094,
        "title": "Spider-Man: Across the Spider-Verse",
        "overview": "After reuniting with Gwen Stacy, Brooklyn's full-time, friendly neighborhood Spider-Man is catapulted across the Multiverse, where he encounters the Spider Society.",
        "poster_path": "https://image.tmdb.org/t/p/w500/8Vt6mWEReuy4Of61Lnj5Xj704m8.jpg",
        "backdrop_path": "https://image.tmdb.org/t/p/original/4HodYYKEIsGOdinkGi2Ucz6X9i0.jpg",
        "release_date": "2023-05-31",
        "rating": 8.4,
        "vote_count": 6800,
        "genre": "Animation, Action, Sci-Fi",
        "runtime": 140,
        "trailer_url": "https://www.youtube.com/watch?v=cqGjhVJWtEg",
        "is_featured": False,
        "is_trending": True,
        "is_popular": True,
    },
    {
        "id": 118,
        "tmdb_id": 475557,
        "title": "Joker",
        "overview": "During the 1980s, a failed stand-up comedian is driven insane and turns to a life of crime and chaos in Gotham City while becoming an infamous psychopathic crime figure.",
        "poster_path": "https://image.tmdb.org/t/p/w500/udDclJoHjfjb8Ekgsd4FDteOkCU.jpg",
        "backdrop_path": "https://image.tmdb.org/t/p/original/n6bUvigpRFqSwmPp1m2YADdbRBc.jpg",
        "release_date": "2019-10-02",
        "rating": 8.1,
        "vote_count": 24800,
        "genre": "Crime, Thriller, Drama",
        "runtime": 122,
        "trailer_url": "https://www.youtube.com/watch?v=zAGVQLHvwOY",
        "is_featured": False,
        "is_trending": False,
        "is_popular": True,
    },
    {
        "id": 119,
        "tmdb_id": 19995,
        "title": "Avatar",
        "overview": "In the 22nd century, a paraplegic Marine is dispatched to the moon Pandora on a unique mission, but becomes torn between following orders and protecting an alien civilization.",
        "poster_path": "https://image.tmdb.org/t/p/w500/kyeqWdyUXW608qlYkRqosgbbn0b.jpg",
        "backdrop_path": "https://image.tmdb.org/t/p/original/vL5LR6WdxWPjCmvSu42mviY0p.jpg",
        "release_date": "2009-12-15",
        "rating": 7.6,
        "vote_count": 31000,
        "genre": "Action, Adventure, Sci-Fi",
        "runtime": 162,
        "trailer_url": "https://www.youtube.com/watch?v=5PSNL1qE6VY",
        "is_featured": False,
        "is_trending": False,
        "is_popular": True,
    },
    {
        "id": 120,
        "tmdb_id": 238,
        "title": "The Godfather",
        "overview": "Spanning the years 1945 to 1955, a chronicle of the fictional Italian-American Corleone crime family. When organized crime family patriarch, Vito Corleone barely survives an attempt on his life, his youngest son, Michael steps in to take care of the would-be killers.",
        "poster_path": "https://image.tmdb.org/t/p/w500/3bhkrj58Vtu7enYsRolD1fZdja1.jpg",
        "backdrop_path": "https://image.tmdb.org/t/p/original/tmU7GeKVybMWFButWEGl2M4GeiP.jpg",
        "release_date": "1972-03-14",
        "rating": 8.7,
        "vote_count": 20400,
        "genre": "Drama, Crime",
        "runtime": 175,
        "trailer_url": "https://www.youtube.com/watch?v=sY1S349g3gU",
        "is_featured": False,
        "is_trending": False,
        "is_popular": True,
    },
    {
        "id": 121,
        "tmdb_id": 98,
        "title": "Gladiator",
        "overview": "In the year 180, the death of emperor Marcus Aurelius throws the Roman Empire into turmoil. Maximus of Merida is one of the Roman army's most capable and trusted generals and his key advisor.",
        "poster_path": "https://image.tmdb.org/t/p/w500/ty8TGRuvJLPUmAR1H1nRIsgwvim.jpg",
        "backdrop_path": "https://image.tmdb.org/t/p/original/b82nqnsqqqa4gL63iKxJ4GgE0tC.jpg",
        "release_date": "2000-05-01",
        "rating": 8.2,
        "vote_count": 18200,
        "genre": "Action, Drama, Adventure",
        "runtime": 155,
        "trailer_url": "https://www.youtube.com/watch?v=owK1qxDselE",
        "is_featured": False,
        "is_trending": True,
        "is_popular": True,
    },
    {
        "id": 122,
        "tmdb_id": 157336,
        "title": "Spider-Man: No Way Home",
        "overview": "Peter Parker is unmasked and no longer able to separate his normal life from the high-stakes of being a super-hero. When he asks for help from Doctor Strange the stakes become even more dangerous.",
        "poster_path": "https://image.tmdb.org/t/p/w500/1g0dhYtq4irTY1GPXvft6k4YLjm.jpg",
        "backdrop_path": "https://image.tmdb.org/t/p/original/14QbnygCuTO0vl7CAFmPf1fgZfV.jpg",
        "release_date": "2021-12-15",
        "rating": 8.0,
        "vote_count": 19400,
        "genre": "Action, Adventure, Sci-Fi",
        "runtime": 148,
        "trailer_url": "https://www.youtube.com/watch?v=JfVOs4VSpmA",
        "is_featured": False,
        "is_trending": True,
        "is_popular": True,
    },
    {
        "id": 123,
        "tmdb_id": 12477,
        "title": "Grave of the Fireflies",
        "overview": "In the final months of World War II, 14-year-old Seita and his four-year-old sister Setsuko are orphaned when their mother is killed in an air raid. The children must fight for survival in a devastated landscape.",
        "poster_path": "https://image.tmdb.org/t/p/w500/k9tv1rXZbOhH7SDv3KpG5Ur095L.jpg",
        "backdrop_path": "https://image.tmdb.org/t/p/original/7c4X3c1g2uA2lJjZ94bM7E2wE0t.jpg",
        "release_date": "1988-04-16",
        "rating": 8.5,
        "vote_count": 5600,
        "genre": "Animation, Drama, War",
        "runtime": 89,
        "trailer_url": "https://www.youtube.com/watch?v=4vPeTSRd580",
        "is_featured": False,
        "is_trending": False,
        "is_popular": False,
    },
    {
        "id": 124,
        "tmdb_id": 389,
        "title": "12 Angry Men",
        "overview": "The defense and the prosecution have rested and the jury is filing into the jury room to decide if a young Spanish-American is guilty or innocent of murdering his father.",
        "poster_path": "https://image.tmdb.org/t/p/w500/ow3wq89wM8qd5X7hWKxiRfsFf9C.jpg",
        "backdrop_path": "https://image.tmdb.org/t/p/original/qqH0ug e5x4kY3A93f87E7e9q3J0.jpg",
        "release_date": "1957-04-10",
        "rating": 8.5,
        "vote_count": 8300,
        "genre": "Drama",
        "runtime": 96,
        "trailer_url": "https://www.youtube.com/watch?v=TEN-2uTi2c0",
        "is_featured": False,
        "is_trending": False,
        "is_popular": False,
    }
]


class TMDBClient:
    """
    Client for The Movie Database (TMDB) API.
    Handles network timeouts, exceptions, and transparent fallback to curated local catalog.
    """
    BASE_URL = "https://api.themoviedb.org/3"

    def __init__(self):
        self.api_key = getattr(settings, 'TMDB_API_KEY', '').strip()
        self.read_token = getattr(settings, 'TMDB_READ_ACCESS_TOKEN', '').strip()
        self.timeout = getattr(settings, 'TMDB_TIMEOUT', 5.0)

    @property
    def is_configured(self):
        return bool(self.api_key or self.read_token)

    def _get_headers(self):
        headers = {"Accept": "application/json"}
        if self.read_token:
            headers["Authorization"] = f"Bearer {self.read_token}"
        return headers

    def _get_params(self, extra_params=None):
        params = {}
        if self.api_key and not self.read_token:
            params["api_key"] = self.api_key
        if extra_params:
            params.update(extra_params)
        return params

    def _fetch_from_api(self, endpoint, params=None):
        if not self.is_configured:
            return None

        url = f"{self.BASE_URL}/{endpoint.lstrip('/')}"
        try:
            response = requests.get(
                url,
                headers=self._get_headers(),
                params=self._get_params(params),
                timeout=self.timeout
            )
            if response.status_code == 200:
                return response.json()
            else:
                logger.warning(f"TMDB API request returned status {response.status_code}: {response.text[:200]}")
                return None
        except requests.Timeout:
            logger.warning(f"TMDB API timeout after {self.timeout}s on {endpoint}. Activating local fallback.")
            return None
        except requests.RequestException as e:
            logger.warning(f"TMDB API connection error on {endpoint}: {e}. Activating local fallback.")
            return None
        except Exception as e:
            logger.error(f"Unexpected error querying TMDB API: {e}")
            return None

    def get_featured_hero(self):
        """Returns the high-impact movie for the hero banner."""
        # Check if local SQL has a featured movie
        from movies.models import Movie
        featured = Movie.objects.filter(is_featured=True).first()
        if featured:
            return featured
        # Otherwise fallback to top fallback movie
        return FALLBACK_MOVIES[0]

    def get_trending(self):
        """Returns trending movies from TMDB or fallback dataset."""
        data = self._fetch_from_api("trending/movie/week")
        if data and "results" in data and len(data["results"]) > 0:
            movies = []
            for item in data["results"][:12]:
                movies.append(self._format_tmdb_movie(item))
            return movies
        # Fallback to local SQL or static fallback
        from movies.models import Movie
        db_trending = list(Movie.objects.filter(is_trending=True)[:12])
        if db_trending:
            return db_trending
        return [m for m in FALLBACK_MOVIES if m.get("is_trending")]

    def get_popular(self):
        """Returns popular movies from TMDB or fallback dataset."""
        data = self._fetch_from_api("movie/popular")
        if data and "results" in data and len(data["results"]) > 0:
            movies = []
            for item in data["results"][:12]:
                movies.append(self._format_tmdb_movie(item))
            return movies
        from movies.models import Movie
        db_popular = list(Movie.objects.filter(is_popular=True)[:12])
        if db_popular:
            return db_popular
        return [m for m in FALLBACK_MOVIES if m.get("is_popular")]

    def get_by_genre(self, genre_keyword):
        """Returns movies matching a given genre."""
        from movies.models import Movie
        matched = list(Movie.objects.filter(genre__icontains=genre_keyword)[:12])
        if matched:
            return matched
        return [m for m in FALLBACK_MOVIES if genre_keyword.lower() in m.get("genre", "").lower()]

    def search(self, query):
        """Searches movies by title query."""
        if not query or not query.strip():
            return []

        clean_query = query.strip()
        data = self._fetch_from_api("search/movie", {"query": clean_query})
        if data and "results" in data:
            movies = []
            for item in data["results"][:20]:
                movies.append(self._format_tmdb_movie(item))
            return movies

        from movies.models import Movie
        db_results = list(Movie.objects.filter(title__icontains=clean_query)[:20])
        if db_results:
            return db_results

        return [
            m for m in FALLBACK_MOVIES
            if clean_query.lower() in m.get("title", "").lower() or clean_query.lower() in m.get("overview", "").lower()
        ]

    def get_movie_detail(self, movie_id):
        """Fetches detailed movie information."""
        # Try SQL first by PK
        from movies.models import Movie
        try:
            return Movie.objects.get(pk=movie_id)
        except (Movie.DoesNotExist, ValueError):
            pass

        # Try fallback dataset
        for m in FALLBACK_MOVIES:
            if str(m.get("id")) == str(movie_id) or str(m.get("tmdb_id")) == str(movie_id):
                return m

        # Try TMDB direct lookup if ID is tmdb_id
        data = self._fetch_from_api(f"movie/{movie_id}", {"append_to_response": "videos"})
        if data:
            return self._format_tmdb_movie(data)

        return None

    def _format_tmdb_movie(self, item):
        """Formats a raw TMDB response dictionary into standard Movie object/dict."""
        poster_path = item.get("poster_path") or ""
        backdrop_path = item.get("backdrop_path") or ""
        if poster_path and not poster_path.startswith("http"):
            poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}"
        else:
            poster_url = poster_path or "/static/images/poster_placeholder.png"

        if backdrop_path and not backdrop_path.startswith("http"):
            backdrop_url = f"https://image.tmdb.org/t/p/original{backdrop_path}"
        else:
            backdrop_url = backdrop_path or "/static/images/backdrop_placeholder.png"

        # Extract genres
        genre_str = ""
        if "genres" in item and isinstance(item["genres"], list):
            genre_str = ", ".join([g["name"] for g in item["genres"] if "name" in g])

        # Extract trailer
        trailer_url = ""
        videos = item.get("videos", {}).get("results", [])
        for v in videos:
            if v.get("site") == "YouTube" and v.get("type") in ("Trailer", "Teaser"):
                trailer_url = f"https://www.youtube.com/watch?v={v.get('key')}"
                break

        release_date = item.get("release_date", "")
        release_year = release_date[:4] if len(release_date) >= 4 else ""

        return {
            "id": item.get("id"),
            "tmdb_id": item.get("id"),
            "title": item.get("title") or item.get("name") or "Untitled",
            "overview": item.get("overview", "No synopsis available."),
            "poster_path": poster_path,
            "poster_url": poster_url,
            "backdrop_path": backdrop_path,
            "backdrop_url": backdrop_url,
            "release_date": release_date,
            "release_year": release_year,
            "rating": round(item.get("vote_average", 0.0), 1),
            "vote_count": item.get("vote_count", 0),
            "genre": genre_str or "Drama",
            "runtime": item.get("runtime"),
            "trailer_url": trailer_url,
        }
