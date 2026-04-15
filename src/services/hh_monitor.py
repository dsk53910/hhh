import asyncio
import httpx
from typing import Dict, Any, Optional
from datetime import datetime

from src.core.config import get_settings
from src.utils.logger import get_logger
from src.utils.helpers import retry_async

logger = get_logger(__name__)


class HHService:
    """
    Client for interacting with the HH.ru API.
    Handles authentication, rate limiting, and basic request formatting.
    """

    def __init__(self):
        self.settings = get_settings()
        self.base_url = "https://api.hh.ru"
        self.headers = {
            "User-Agent": "HHHJobTracker/1.0 (dmitriy.hh.tracker@gmail.com)"
        }

        # Add authorization if API key is provided in config
        if self.settings.hh.api_key:
            self.headers["Authorization"] = f"Bearer {self.settings.hh.api_key}"

    @retry_async(
        max_retries=3, delay=2.0, exceptions=(httpx.RequestError, httpx.HTTPStatusError)
    )
    async def fetch_vacancies(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fetch a list of vacancies from HH.ru based on search parameters.

        Args:
            params: Dictionary of search parameters (e.g., {'text': 'Python', 'area': 1})

        Returns:
            JSON response from HH.ru containing 'items' (vacancies) and pagination info.
        """
        async with httpx.AsyncClient(
            base_url=self.base_url, headers=self.headers, timeout=10.0
        ) as client:
            logger.info("fetching_vacancies_from_hh", extra={"params": params})

            response = await client.get("/vacancies", params=params)

            # Handle rate limiting explicitly before raise_for_status
            if response.status_code == 429:
                logger.warning("hh_api_rate_limit_hit_sleeping")
                await asyncio.sleep(5)
                response.raise_for_status()  # This will trigger the @retry_async decorator

            if response.status_code >= 400:
                logger.error(f"HH API Error {response.status_code}: {response.text}")

            response.raise_for_status()
            return response.json()

    @retry_async(
        max_retries=2, delay=2.0, exceptions=(httpx.RequestError, httpx.HTTPStatusError)
    )
    async def apply_to_vacancy(
        self, vacancy_id: str, resume_id: str, message: str = ""
    ) -> bool:
        """
        Sends a POST request to HH.ru to apply for a vacancy.
        Requires a valid User Bearer token (not just app token).

        Args:
            vacancy_id: The HH.ru vacancy ID
            resume_id: The user's HH.ru resume ID
            message: Optional cover letter text

        Returns:
            True if applied successfully, False otherwise.
        """
        if not self.settings.hh.api_key:
            logger.error("Cannot apply: HH_API_KEY is not set.")
            return False

        url = "/negotiations"

        # HH API expects form-data or urlencoded for negotiations
        data = {"vacancy_id": vacancy_id, "resume_id": resume_id, "message": message}

        async with httpx.AsyncClient(
            base_url=self.base_url, headers=self.headers, timeout=10.0
        ) as client:
            logger.info(f"Applying to vacancy {vacancy_id} with resume {resume_id}")

            response = await client.post(url, data=data)

            if response.status_code == 201 or response.status_code == 200:
                logger.info(f"Successfully applied to vacancy {vacancy_id}")
                return True
            elif response.status_code == 403:
                logger.error(
                    f"Failed to apply (403): Token might not have negotiations scope or is invalid. {response.text}"
                )
                return False
            elif response.status_code == 400:
                # 400 Bad Request usually means "Already applied" or "Resume doesn't match requirements"
                logger.warning(f"Failed to apply (400): {response.text}")
                return False
            else:
                logger.error(
                    f"Unexpected response when applying ({response.status_code}): {response.text}"
                )
                response.raise_for_status()
                return False

    @retry_async(
        max_retries=2, delay=1.0, exceptions=(httpx.RequestError, httpx.HTTPStatusError)
    )
    async def get_area_suggestions(self, text: str) -> list[Dict[str, str]]:
        """
        Gets auto-complete suggestions from HH.ru for areas (cities, countries).
        """
        async with httpx.AsyncClient(
            base_url=self.base_url, headers=self.headers, timeout=5.0
        ) as client:
            response = await client.get("/suggests/areas", params={"text": text})
            if response.status_code == 200:
                data = response.json()
                return [
                    {"id": item.get("id"), "text": item.get("text")}
                    for item in data.get("items", [])
                ]
            return []
        """
        Fetch full details of a specific vacancy by ID.

        Args:
            vacancy_id: The HH.ru vacancy ID string.

        Returns:
            JSON response containing the full vacancy details.
        """
        async with httpx.AsyncClient(
            base_url=self.base_url, headers=self.headers, timeout=10.0
        ) as client:
            logger.info("fetching_vacancy_details", extra={"vacancy_id": vacancy_id})

            response = await client.get(f"/vacancies/{vacancy_id}")

            if response.status_code == 429:
                logger.warning("hh_api_rate_limit_hit_sleeping")
                await asyncio.sleep(5)
                response.raise_for_status()

            response.raise_for_status()
            return response.json()

    @retry_async(
        max_retries=2, delay=1.0, exceptions=(httpx.RequestError, httpx.HTTPStatusError)
    )
    async def get_keyword_suggestions(self, text: str) -> list[str]:
        """
        Gets auto-complete suggestions from HH.ru for a given partial keyword.
        """
        async with httpx.AsyncClient(
            base_url=self.base_url, headers=self.headers, timeout=5.0
        ) as client:
            response = await client.get(
                "/suggests/vacancy_search_keyword", params={"text": text}
            )
            if response.status_code == 200:
                data = response.json()
                return [item.get("text") for item in data.get("items", [])]
            return []

    @retry_async(
        max_retries=3, delay=2.0, exceptions=(httpx.RequestError, httpx.HTTPStatusError)
    )
    async def get_vacancy_details(self, vacancy_id: str) -> Dict[str, Any]:
        """
        Fetch full details of a specific vacancy by ID.
        """
        async with httpx.AsyncClient(
            base_url=self.base_url, headers=self.headers, timeout=10.0
        ) as client:
            logger.info("fetching_vacancy_details", extra={"vacancy_id": vacancy_id})

            response = await client.get(f"/vacancies/{vacancy_id}")

            if response.status_code == 429:
                logger.warning("hh_api_rate_limit_hit_sleeping")
                await asyncio.sleep(5)
                response.raise_for_status()

            response.raise_for_status()
            return response.json()
