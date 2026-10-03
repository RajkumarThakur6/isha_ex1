import os
import unittest
from unittest.mock import patch
from uuid import uuid4

import httpx
from fastapi.testclient import TestClient
from openai import APIConnectionError

import app as chat_app
import practice


class ChatAppTests(unittest.TestCase):
    def setUp(self):
        self.database_name = f"genai_chat_test_{uuid4().hex}"
        self.database_name_patch = patch.object(
            chat_app, "MYSQL_DATABASE", self.database_name
        )
        self.database_name_patch.start()
        chat_app.initialize_database()

    def tearDown(self):
        try:
            with chat_app.database_connection(server=True) as connection:
                cursor = connection.cursor()
                try:
                    cursor.execute(f"DROP DATABASE IF EXISTS `{self.database_name}`")
                finally:
                    cursor.close()
        finally:
            self.database_name_patch.stop()

    def test_chat_history_is_saved_and_separate_by_browser_session(self):
        received_messages = []

        def fake_ask_model(messages):
            received_messages.append(list(messages))
            return "Your name is Isha."

        with patch.object(chat_app, "ask_model", side_effect=fake_ask_model):
            with TestClient(chat_app.app) as first_browser:
                home = first_browser.get("/")
                self.assertEqual(home.status_code, 200)
                self.assertIn("practice_chat_session", first_browser.cookies)

                response = first_browser.post(
                    "/api/chat", json={"message": "My name is Isha."}
                )
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.json(), {"reply": "Your name is Isha."})

                history = first_browser.get("/api/history").json()["messages"]
                self.assertEqual(
                    history,
                    [
                        {"role": "user", "content": "My name is Isha."},
                        {"role": "assistant", "content": "Your name is Isha."},
                    ],
                )

                follow_up = first_browser.post(
                    "/api/chat", json={"message": "What is my name?"}
                )
                self.assertEqual(follow_up.status_code, 200)
                self.assertEqual(
                    received_messages[1][-1],
                    {"role": "user", "content": "What is my name?"},
                )
                self.assertEqual(len(received_messages[1]), 3)

                with TestClient(chat_app.app) as second_browser:
                    self.assertEqual(
                        second_browser.get("/api/history").json()["messages"], []
                    )

    def test_demo_mode_needs_no_provider_key(self):
        with patch.object(practice, "DEMO_MODE", True):
            with patch.object(practice, "OpenAI") as openai:
                reply = practice.ask_model(
                    [{"role": "user", "content": "Hello from the browser"}]
                )
        self.assertIn("Demo reply", reply)
        self.assertIn("Hello from the browser", reply)
        openai.assert_not_called()

    def test_health_endpoint_identifies_demo_mode_and_model(self):
        with patch.object(chat_app, "DEMO_MODE", True):
            with patch.object(chat_app, "PROVIDER", "ollama"):
                with TestClient(chat_app.app) as browser:
                    response = browser.get("/api/health")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["demo_mode"])
        self.assertEqual(response.json()["provider"], "ollama")
        self.assertEqual(response.json()["model"], practice.MODEL)

    def test_whitespace_only_messages_are_rejected(self):
        with TestClient(chat_app.app) as browser:
            response = browser.post("/api/chat", json={"message": "   "})
        self.assertEqual(response.status_code, 422)

    def test_failed_model_request_is_not_saved(self):
        with patch.object(
            chat_app,
            "ask_model",
            side_effect=RuntimeError("The model could not respond."),
        ):
            with TestClient(chat_app.app) as browser:
                response = browser.post("/api/chat", json={"message": "Hello"})
                self.assertEqual(response.status_code, 503)
                self.assertEqual(
                    browser.get("/api/history").json()["messages"], []
                )

    def test_unavailable_ollama_shows_local_setup_instructions(self):
        error = APIConnectionError(
            request=httpx.Request("POST", "http://127.0.0.1:11434/v1/chat/completions")
        )
        with patch.object(chat_app, "PROVIDER", "ollama"):
            with patch.object(chat_app, "BASE_URL", "http://127.0.0.1:11434/v1"):
                with patch.object(chat_app, "MODEL", "llama3.2:3b"):
                    with patch.object(chat_app, "ask_model", side_effect=error):
                        with TestClient(chat_app.app) as browser:
                            response = browser.post(
                                "/api/chat", json={"message": "Hello"}
                            )
                            self.assertEqual(response.status_code, 502)
                            self.assertIn("Cannot reach Ollama", response.json()["detail"])
                            self.assertIn(
                                "ollama pull llama3.2:3b",
                                response.json()["detail"],
                            )

    def test_clear_removes_only_current_browser_history(self):
        with patch.object(chat_app, "ask_model", return_value="Hello!"):
            with TestClient(chat_app.app) as first_browser:
                first_browser.post("/api/chat", json={"message": "Hello"})
                with TestClient(chat_app.app) as second_browser:
                    second_browser.post(
                        "/api/chat", json={"message": "Keep this"}
                    )
                    first_browser.post("/api/clear")
                    self.assertEqual(
                        first_browser.get("/api/history").json()["messages"], []
                    )
                    self.assertEqual(
                        len(second_browser.get("/api/history").json()["messages"]),
                        2,
                    )

    def test_ollama_uses_openai_compatible_client_without_cloud_key(self):
        fake_client = unittest.mock.Mock()
        fake_client.chat.completions.create.return_value.choices = [
            unittest.mock.Mock(message=unittest.mock.Mock(content="Hello!"))
        ]
        messages = [{"role": "user", "content": "Hi"}]

        with patch.dict(os.environ, {"OPENAI_API_KEY": "", "OPENROUTER_API_KEY": ""}):
            with patch.object(practice, "PROVIDER", "ollama"):
                with patch.object(practice, "BASE_URL", "http://127.0.0.1:11434/v1"):
                    with patch.object(practice, "MODEL", "llama3.2:3b"):
                        with patch.object(practice, "DEMO_MODE", False):
                            with patch.object(
                                practice, "OpenAI", return_value=fake_client
                            ) as openai:
                                self.assertEqual(
                                    practice.ask_model(messages), "Hello!"
                                )

        openai.assert_called_once_with(
            api_key="ollama",
            base_url="http://127.0.0.1:11434/v1/",
            timeout=120.0,
            max_retries=0,
        )
        fake_client.chat.completions.create.assert_called_once_with(
            model="llama3.2:3b",
            messages=messages,
            max_tokens=600,
        )

    def test_openrouter_requires_its_own_api_key(self):
        with patch.dict(os.environ, {"OPENROUTER_API_KEY": ""}):
            with patch.object(practice, "PROVIDER", "openrouter"):
                with self.assertRaisesRegex(
                    RuntimeError, "OPENROUTER_API_KEY is missing"
                ):
                    practice.ask_model([{"role": "user", "content": "Hi"}])

    def test_lm_studio_uses_its_local_openai_compatible_server(self):
        fake_client = unittest.mock.Mock()
        fake_client.chat.completions.create.return_value.choices = [
            unittest.mock.Mock(message=unittest.mock.Mock(content="Hello!"))
        ]
        messages = [{"role": "user", "content": "Hi"}]

        with patch.dict(os.environ, {"OPENAI_API_KEY": "", "OPENROUTER_API_KEY": ""}):
            with patch.object(practice, "PROVIDER", "lmstudio"):
                with patch.object(practice, "BASE_URL", "http://127.0.0.1:1234/v1"):
                    with patch.object(practice, "MODEL", "local-model"):
                        with patch.object(practice, "DEMO_MODE", False):
                            with patch.object(
                                practice, "OpenAI", return_value=fake_client
                            ) as openai:
                                self.assertEqual(
                                    practice.ask_model(messages), "Hello!"
                                )

        openai.assert_called_once_with(
            api_key="ollama",
            base_url="http://127.0.0.1:1234/v1/",
            timeout=120.0,
            max_retries=0,
        )
        fake_client.chat.completions.create.assert_called_once_with(
            model="local-model",
            messages=messages,
            max_tokens=600,
        )

    def test_openai_client_sends_messages_to_selected_model(self):
        fake_client = unittest.mock.Mock()
        fake_client.chat.completions.create.return_value.choices = [
            unittest.mock.Mock(message=unittest.mock.Mock(content="Hello!"))
        ]
        messages = [{"role": "user", "content": "Hi"}]

        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-only-key"}):
            with patch.object(practice, "PROVIDER", "openai"):
                with patch.object(practice, "BASE_URL", "https://api.openai.com/v1"):
                    with patch.object(practice, "MODEL", "gpt-4o-mini"):
                        with patch.object(practice, "DEMO_MODE", False):
                            with patch.object(
                                practice, "OpenAI", return_value=fake_client
                            ) as openai:
                                self.assertEqual(
                                    practice.ask_model(messages), "Hello!"
                                )

        openai.assert_called_once_with(
            api_key="test-only-key",
            base_url="https://api.openai.com/v1/",
            timeout=45.0,
            max_retries=1,
        )
        fake_client.chat.completions.create.assert_called_once_with(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=600,
        )


if __name__ == "__main__":
    unittest.main()
