"""Generate a beginner-friendly A-to-Z Word guide for the chat app."""

from pathlib import Path

from docx import Document
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor


OUTPUT = Path(__file__).with_name("LLM_Chat_App_A_to_Z_Guide.docx")
INK = "18343B"
TEAL = "247E78"
PALE = "E5F1EC"
PAPER = "F7F8F4"
WHITE = "FFFFFF"
MUTED = "526B70"


def set_cell_shading(cell, fill: str) -> None:
    properties = cell._tc.get_or_add_tcPr()
    shading = OxmlElement("w:shd")
    shading.set(qn("w:fill"), fill)
    properties.append(shading)


def set_cell_text(cell, value: str, *, bold: bool = False, color: str = INK) -> None:
    cell.text = ""
    paragraph = cell.paragraphs[0]
    paragraph.paragraph_format.space_after = Pt(0)
    run = paragraph.add_run(value)
    run.bold = bold
    run.font.name = "Aptos"
    run.font.size = Pt(9)
    run.font.color.rgb = RGBColor.from_string(color)
    cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER


def add_page_number(paragraph) -> None:
    paragraph.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    paragraph.add_run("Page ").font.size = Pt(8)
    field = OxmlElement("w:fldSimple")
    field.set(qn("w:instr"), "PAGE")
    paragraph._p.append(field)


def add_code(document: Document, code: str) -> None:
    paragraph = document.add_paragraph(style="Code Block")
    paragraph.paragraph_format.keep_together = True
    paragraph.add_run(code)


def add_bullet(document: Document, text: str) -> None:
    document.add_paragraph(text, style="List Bullet")


def add_number(document: Document, text: str) -> None:
    document.add_paragraph(text, style="List Number")


def add_table(document: Document, headers: list[str], rows: list[list[str]]) -> None:
    table = document.add_table(rows=1, cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.style = "Light Shading Accent 1"
    for index, header in enumerate(headers):
        set_cell_text(table.rows[0].cells[index], header, bold=True, color=WHITE)
        set_cell_shading(table.rows[0].cells[index], INK)
    for row_number, row in enumerate(rows):
        cells = table.add_row().cells
        for index, value in enumerate(row):
            set_cell_text(cells[index], value)
            if row_number % 2 == 1:
                set_cell_shading(cells[index], PAPER)
    document.add_paragraph()


def configure_styles(document: Document) -> None:
    styles = document.styles
    normal = styles["Normal"]
    normal.font.name = "Aptos"
    normal.font.size = Pt(10)
    normal.font.color.rgb = RGBColor.from_string(INK)
    normal.paragraph_format.space_after = Pt(6)
    normal.paragraph_format.line_spacing = 1.12

    for name, size in (("Title", 30), ("Heading 1", 20), ("Heading 2", 14), ("Heading 3", 11)):
        style = styles[name]
        style.font.name = "Aptos Display"
        style.font.size = Pt(size)
        style.font.bold = True
        style.font.color.rgb = RGBColor.from_string(INK if name != "Heading 2" else TEAL)
        style.paragraph_format.keep_with_next = True

    code = styles.add_style("Code Block", 1)
    code.font.name = "Consolas"
    code.font.size = Pt(8.5)
    code.font.color.rgb = RGBColor.from_string(INK)
    code.paragraph_format.left_indent = Inches(0.15)
    code.paragraph_format.right_indent = Inches(0.1)
    code.paragraph_format.space_before = Pt(3)
    code.paragraph_format.space_after = Pt(9)
    code.paragraph_format.line_spacing = 1.0


def add_heading(document: Document, text: str, level: int = 1) -> None:
    document.add_heading(text, level=level)


def build_document() -> None:
    document = Document()
    configure_styles(document)

    section = document.sections[0]
    section.top_margin = Inches(0.7)
    section.bottom_margin = Inches(0.65)
    section.left_margin = Inches(0.75)
    section.right_margin = Inches(0.75)
    section.header_distance = Inches(0.3)
    section.footer_distance = Inches(0.3)

    header = section.header.paragraphs[0]
    header.text = "LLM CHAT PRACTICE  |  BEGINNER BUILD GUIDE"
    header.runs[0].font.name = "Aptos"
    header.runs[0].font.size = Pt(8)
    header.runs[0].font.color.rgb = RGBColor.from_string(MUTED)
    add_page_number(section.footer.paragraphs[0])

    cover = document.add_paragraph()
    cover.paragraph_format.space_before = Pt(90)
    cover.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title = cover.add_run("Build a Local AI Chat App")
    title.bold = True
    title.font.name = "Aptos Display"
    title.font.size = Pt(30)
    title.font.color.rgb = RGBColor.from_string(INK)

    subtitle = document.add_paragraph()
    subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
    subtitle.paragraph_format.space_before = Pt(12)
    subtitle_run = subtitle.add_run("A complete, beginner-friendly A-to-Z guide")
    subtitle_run.font.size = Pt(16)
    subtitle_run.font.color.rgb = RGBColor.from_string(TEAL)

    summary = document.add_paragraph()
    summary.alignment = WD_ALIGN_PARAGRAPH.CENTER
    summary.paragraph_format.space_before = Pt(20)
    summary.add_run(
        "Learn how the browser, Python backend, MySQL chat memory, and a local "
        "Ollama model work together."
    )
    summary.paragraph_format.left_indent = Inches(0.7)
    summary.paragraph_format.right_indent = Inches(0.7)

    document.add_paragraph()
    add_table(
        document,
        ["Browser", "Python backend", "Local AI"],
        [[
            "HTML, CSS and JavaScript collect questions and display replies.",
            "FastAPI validates requests, keeps browser sessions separate, and stores chat history.",
            "Ollama runs llama3.2:3b on this computer. No paid cloud API key is needed.",
        ]],
    )
    note = document.add_paragraph()
    note.alignment = WD_ALIGN_PARAGRAPH.CENTER
    note.paragraph_format.space_before = Pt(18)
    note.add_run("Written for learning and local practice — not public production deployment.")

    document.add_page_break()
    add_heading(document, "How to use this guide")
    document.add_paragraph(
        "Follow the sections in order the first time. The app has already been built "
        "and tested on this computer; the guide explains both how its pieces were "
        "assembled and how to run, test, and change them safely."
    )
    add_table(
        document,
        ["Part", "What you will learn"],
        [
            ["1. Goal and architecture", "What the app does and how a message moves through it."],
            ["2. Prerequisites", "What must be installed and running on Windows."],
            ["3. Configuration", "How local environment settings connect MySQL and Ollama."],
            ["4. Build walkthrough", "How the frontend, backend, model call, and memory fit together."],
            ["5. Run and test", "How to start the app, ask follow-up questions, and run checks."],
            ["6. Troubleshooting", "What to do when the browser, MySQL, or model is unavailable."],
            ["7. Safe next steps", "How to learn by making small, reversible changes."],
        ],
    )

    add_heading(document, "1. What we built")
    document.add_paragraph(
        "This is a browser chat for learning about generative AI. You type into a "
        "web page, the Python server sends the question and recent conversation to a "
        "model, then the answer is shown in the page. MySQL stores the successful "
        "conversation so follow-up questions can use earlier messages."
    )
    add_heading(document, "The complete request path", 2)
    add_code(
        document,
        "You type a question\n"
        "  -> frontend/app.js sends JSON to POST /api/chat\n"
        "  -> app.py validates the text and reads this browser's recent history\n"
        "  -> practice.py sends the conversation to Ollama on this computer\n"
        "  -> Ollama runs llama3.2:3b and returns an answer\n"
        "  -> app.py saves the user/assistant pair in MySQL\n"
        "  -> the browser displays the answer",
    )
    document.add_paragraph(
        "The browser talks only to the local FastAPI server. The model connection "
        "and all provider credentials stay on the server side."
    )
    add_heading(document, "Files and their jobs", 2)
    add_table(
        document,
        ["File or folder", "Purpose"],
        [
            ["app.py", "FastAPI routes, input checks, session cookie, MySQL setup, history, and errors."],
            ["practice.py", "Chooses the LLM provider and sends messages through the OpenAI-compatible client."],
            ["frontend/index.html", "Page structure, headings, chat form, and notices."],
            ["frontend/styles.css", "Colors, spacing, layout, and responsive styling."],
            ["frontend/app.js", "Calls the backend, loads history, and renders messages."],
            [".env.local", "Private local settings such as the MySQL password; ignored by Git."],
            [".env.example", "Safe settings template with placeholders, not a real password or API key."],
            ["test_app.py", "Automated checks for memory, sessions, provider configuration, and validation."],
            ["make_setup_guide.py", "Source used to generate the PDF setup guide."],
        ],
    )

    document.add_page_break()
    add_heading(document, "2. Prerequisites: what needs to be installed")
    add_heading(document, "A. Python", 2)
    document.add_paragraph(
        "The app has been tested with Python 3.13 in its project environment. "
        "Use the environment already in the project folder, named myenv."
    )
    add_heading(document, "B. MySQL", 2)
    document.add_paragraph(
        "The MySQL server must be installed and running locally on 127.0.0.1, "
        "normally on port 3306. The configured MySQL account needs permission to "
        "create the practice database and its chat table the first time the app starts."
    )
    add_heading(document, "C. Ollama and its model", 2)
    document.add_paragraph(
        "Ollama is installed on this computer, and the llama3.2:3b model has been "
        "downloaded (about 2 GB). It runs on this computer and does not use a paid "
        "cloud API key. Ollama must be running before you send model requests."
    )
    add_code(
        document,
        "ollama --version\n"
        "ollama list",
    )
    document.add_paragraph(
        "In the model list, check that llama3.2:3b appears. Download it only if it "
        "is missing:"
    )
    add_code(document, "ollama pull llama3.2:3b")
    add_heading(document, "D. Python packages", 2)
    document.add_paragraph(
        "requirements.txt lists the app libraries: FastAPI, Uvicorn, the OpenAI "
        "compatible client, python-dotenv, and the MySQL connector."
    )

    add_heading(document, "3. Configure the app safely")
    add_heading(document, "A. Use the project folder", 2)
    add_code(
        document,
        'cd "C:\\Users\\raj.kumar.thakur\\Desktop\\Isha_class\\ex-1"',
    )
    add_heading(document, "B. Configure .env.local", 2)
    document.add_paragraph(
        "The app loads .env.local for local settings. Never paste passwords or real "
        "API keys into this guide, browser JavaScript, screenshots, or Git. This "
        "computer already has its private local configuration. Do not overwrite it. "
        "For a new computer, make a copy of the template once:"
    )
    add_code(document, "Copy-Item .env.example .env.local")
    document.add_paragraph(
        "Open .env.local in a text editor. Keep the local provider values like this, "
        "and enter your own MySQL password in the placeholder field:"
    )
    add_code(
        document,
        "LLM_PROVIDER=ollama\n"
        "LLM_MODEL=llama3.2:3b\n"
        "LLM_BASE_URL=http://127.0.0.1:11434/v1\n"
        "LLM_DEMO_MODE=false\n"
        "\n"
        "MYSQL_HOST=127.0.0.1\n"
        "MYSQL_PORT=3306\n"
        "MYSQL_DATABASE=genai_chat_practice\n"
        "MYSQL_USER=root\n"
        "MYSQL_PASSWORD=your-local-mysql-password\n"
        "COOKIE_SECURE=false",
    )
    document.add_paragraph(
        "No Ollama API key is required. The word root above is the local MySQL "
        "username from the practice setup, not an internet account. For real "
        "deployment, create a restricted MySQL user instead of using root."
    )
    add_heading(document, "C. Demo mode versus real local AI", 2)
    add_table(
        document,
        ["Setting", "Behavior"],
        [
            ["LLM_DEMO_MODE=true", "Returns a sample echo. No model is contacted."],
            ["LLM_DEMO_MODE=false", "Sends the conversation to the configured model."],
        ],
    )
    document.add_paragraph(
        "The working local setup uses false. If you change .env.local while the "
        "server is running, stop and restart the server so Python reloads the settings."
    )

    document.add_page_break()
    add_heading(document, "4. A-to-Z build walkthrough")
    document.add_paragraph(
        "This is the order used to assemble the app. It is also a sensible order "
        "for learning how to build another small AI project."
    )
    build_steps = [
        ("Step 1 — Define the smallest useful goal", "Decide what the app accepts and returns. Here it accepts text questions and returns text answers, with browser-specific memory."),
        ("Step 2 — Choose the model connection", "Use Ollama for local, no-cloud-key testing. Keep the provider behind a single function so a compatible hosted API can be selected later."),
        ("Step 3 — Create a safe Python environment", "Use myenv and install the packages listed in requirements.txt. Keep app libraries out of the global Python installation."),
        ("Step 4 — Store settings outside source code", "Load provider and database settings from .env.local. Keep that file ignored by Git and keep .env.example free of actual secrets."),
        ("Step 5 — Define the browser page", "Write the HTML structure for the app heading, conversation area, textarea, send button, and new-chat button."),
        ("Step 6 — Style the page", "Use CSS to arrange the chat, make messages readable, and show whether the app is in demo mode or using a local provider."),
        ("Step 7 — Connect the browser", "Use JavaScript fetch calls to send JSON to /api/chat, load /api/history, read /api/health, and call /api/clear."),
        ("Step 8 — Build the backend API", "Use FastAPI routes to serve the page and JSON endpoints. Validate messages, trim whitespace, and enforce a maximum message length."),
        ("Step 9 — Give each browser a session", "Create a random UUID cookie with HttpOnly and SameSite settings. This lets the server separate one browser's messages from another's."),
        ("Step 10 — Store successful turns", "Create the MySQL database and chat_messages table if missing. Store the user's question and assistant answer only after the model responds successfully."),
        ("Step 11 — Add chat memory", "Load up to the latest 20 messages for that browser, put them in chronological order, add the new question, and send the full list to the model."),
        ("Step 12 — Call the model", "In practice.py, configure the OpenAI-compatible client with the selected base URL and model. Ollama uses a local URL and a placeholder SDK key that is not a real secret."),
        ("Step 13 — Handle failures clearly", "Translate a missing Ollama server, missing model, provider key rejection, usage limit, and MySQL connection problem into explicit user-facing messages. A failed model request is not saved as a successful conversation."),
        ("Step 14 — Test the pieces", "Run automated tests for input validation, history, session separation, provider options, and failure behavior before changing the app further."),
        ("Step 15 — Run locally and observe", "Start MySQL and Ollama, start Uvicorn, use the browser, and look at the browser Network panel and the Uvicorn terminal when learning the request path."),
    ]
    for title, detail in build_steps:
        add_heading(document, title, 2)
        document.add_paragraph(detail)

    document.add_heading("The main model function in plain language", level=2)
    document.add_paragraph(
        "The browser and backend pass a list of role/content messages into "
        "ask_model(). The function either returns a demo echo or sends that list "
        "to the configured model and returns the assistant text. The backend saves "
        "the turn only after ask_model() succeeds."
    )
    add_code(
        document,
        "messages = [\n"
        '    {"role": "user", "content": "My name is Isha."},\n'
        '    {"role": "assistant", "content": "Nice to meet you, Isha."},\n'
        '    {"role": "user", "content": "What is my name?"},\n'
        "]",
    )

    document.add_page_break()
    add_heading(document, "5. Start the app on Windows")
    add_heading(document, "Before you start", 2)
    for text in [
        "MySQL is running locally.",
        "Ollama is open/running. Check it with ollama list.",
        "llama3.2:3b appears in the Ollama model list.",
        "The private .env.local file has the correct local MySQL settings and LLM_DEMO_MODE=false.",
    ]:
        add_bullet(document, text)
    add_heading(document, "Start the Python chat server", 2)
    document.add_paragraph(
        "Open PowerShell in the project folder and run these commands. Keep this "
        "PowerShell window open while you use the chat:"
    )
    add_code(
        document,
        'cd "C:\\Users\\raj.kumar.thakur\\Desktop\\Isha_class\\ex-1"\n'
        ".\\myenv\\Scripts\\Activate.ps1\n"
        "python -m uvicorn app:app --host 127.0.0.1 --port 8000",
    )
    document.add_paragraph(
        "If PowerShell says script execution is blocked, do not change a machine-wide "
        "policy just for this app. You can run the project interpreter directly:"
    )
    add_code(
        document,
        '& ".\\myenv\\Scripts\\python.exe" -m uvicorn app:app --host 127.0.0.1 --port 8000',
    )
    add_heading(document, "Open and use the page", 2)
    add_number(document, "Open http://127.0.0.1:8000 in a browser.")
    add_number(document, "Ask a simple question, such as: What is 2 + 2?")
    add_number(document, "Ask a related follow-up to check that the earlier turn is remembered.")
    add_number(document, "Use New chat to clear only this browser's stored conversation.")
    document.add_paragraph(
        "To stop the Python chat server, focus its PowerShell window and press "
        "Ctrl+C. Ollama can stay installed; it does not need to be re-downloaded."
    )

    add_heading(document, "Check that services respond", 2)
    add_code(
        document,
        "Test-NetConnection 127.0.0.1 -Port 8000\n"
        "Test-NetConnection 127.0.0.1 -Port 11434\n"
        "Test-NetConnection 127.0.0.1 -Port 3306",
    )
    document.add_paragraph(
        "Port 8000 is the chat web app, 11434 is Ollama, and 3306 is MySQL. "
        "The first time FastAPI starts, it creates the configured chat database "
        "and table if the MySQL user has permission."
    )

    document.add_page_break()
    add_heading(document, "6. How chat memory and API endpoints work")
    add_heading(document, "Memory is stored in MySQL", 2)
    document.add_paragraph(
        "An LLM call is normally independent: it does not remember previous HTTP "
        "requests by itself. This app creates the useful effect of memory by loading "
        "recent user/assistant rows for the current browser from MySQL and sending "
        "them again with each new question. It keeps at most 20 prior messages in "
        "the model context."
    )
    add_table(
        document,
        ["Endpoint", "Purpose"],
        [
            ["GET /api/health", "Reports the selected provider, model, and demo/live mode."],
            ["GET /api/history", "Returns messages for the current browser session."],
            ["POST /api/chat", "Validates a question, includes recent context, calls the model, and saves a successful turn."],
            ["POST /api/clear", "Deletes the current browser session's chat rows."],
            ["GET /docs", "Shows FastAPI's interactive API documentation."],
        ],
    )
    add_heading(document, "Example JSON request and reply", 2)
    add_code(
        document,
        'POST /api/chat\n'
        'Request:  {"message": "What is 2 + 2?"}\n'
        'Response: {"reply": "2 + 2 = 4"}',
    )
    add_heading(document, "Useful ways to inspect the app", 2)
    add_bullet(document, "Browser: open Developer Tools, then Network, and inspect /api/health and /api/chat.")
    add_bullet(document, "Python server: read the PowerShell output where Uvicorn is running.")
    add_bullet(document, "MySQL: inspect the genai_chat_practice database and chat_messages table using a MySQL client.")
    add_bullet(document, "API docs: open http://127.0.0.1:8000/docs while the server is running.")

    add_heading(document, "7. Automated checks")
    document.add_paragraph(
        "Open a second PowerShell window in the project folder, activate myenv, "
        "and run the tests:"
    )
    add_code(
        document,
        'cd "C:\\Users\\raj.kumar.thakur\\Desktop\\Isha_class\\ex-1"\n'
        ".\\myenv\\Scripts\\Activate.ps1\n"
        "python -m unittest -v test_app",
    )
    document.add_paragraph(
        "The tests use temporary, uniquely named MySQL databases and remove those "
        "test databases at the end. Run them only against your local practice MySQL "
        "server and a MySQL account with permission to create and drop databases. "
        "They mock model replies, so they do not use cloud API quota."
    )
    add_heading(document, "What has been tested on this computer", 2)
    add_table(
        document,
        ["Check", "Result"],
        [
            ["MySQL-backed app tests", "11 tests passed, including browser session separation and history."],
            ["Ollama provider request", "Verified using a mocked compatible endpoint in automated tests."],
            ["Real local inference", "Verified in the browser with llama3.2:3b; a simple arithmetic question returned an answer."],
            ["Hosted cloud providers", "Configuration and key checks are covered; no paid provider request was made."],
        ],
    )

    document.add_page_break()
    add_heading(document, "8. Troubleshooting")
    add_table(
        document,
        ["What you see", "What to check or do"],
        [
            ["Browser says it cannot connect / page refused connection", "Start Uvicorn in the project folder. Leave that PowerShell window open. Visit http://127.0.0.1:8000."],
            ["Cannot reach Ollama at 127.0.0.1:11434", "Open Ollama from the Start menu. Check Test-NetConnection 127.0.0.1 -Port 11434. If Ollama is installed but not running, start its app or run ollama serve in a separate terminal."],
            ["Ollama says the model is missing", "Run ollama list. If llama3.2:3b is absent, run ollama pull llama3.2:3b and retry."],
            ["Could not connect to MySQL", "Start the MySQL service, check port 3306, then verify MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, and database creation permissions in .env.local."],
            ["The chat only echoes the question", "This is demo mode. Set LLM_DEMO_MODE=false in .env.local and restart Uvicorn."],
            ["Python or Uvicorn command not found", "Activate .\\myenv\\Scripts\\Activate.ps1 in the project folder, or use .\\myenv\\Scripts\\python.exe directly."],
            ["Port 8000 is already in use", "Another app is listening there. Stop the earlier Uvicorn window with Ctrl+C, or use a different port and open that matching URL."],
            ["Question failed and is not in saved history", "This is intentional: unsuccessful model requests are not saved as completed turns. Read the error and the server's PowerShell log."],
        ],
    )
    add_heading(document, "Check service ports", 2)
    add_code(
        document,
        "Test-NetConnection 127.0.0.1 -Port 8000\n"
        "Test-NetConnection 127.0.0.1 -Port 11434\n"
        "Test-NetConnection 127.0.0.1 -Port 3306",
    )
    document.add_paragraph(
        "A successful port check says TcpTestSucceeded : True. A false result "
        "means that service is not listening at that address/port yet."
    )

    add_heading(document, "9. Optional: change model provider")
    document.add_paragraph(
        "The default should remain Ollama while you are learning because it works "
        "locally without a paid API key. Stop and restart Uvicorn after changing "
        "provider settings."
    )
    add_table(
        document,
        ["Provider", "Required settings", "Key / cost note"],
        [
            ["Ollama", "LLM_PROVIDER=ollama; model llama3.2:3b; URL http://127.0.0.1:11434/v1", "Local. No cloud API key."],
            ["LM Studio", "LLM_PROVIDER=lmstudio; URL http://127.0.0.1:1234/v1; model ID loaded in LM Studio", "Local. Start its Local Server."],
            ["OpenAI", "LLM_PROVIDER=openai; OPENAI_API_KEY; choose an available model", "Hosted. Real key and API billing may be required; ChatGPT subscription is separate."],
            ["OpenRouter", "LLM_PROVIDER=openrouter; OPENROUTER_API_KEY; choose a model ID", "Hosted. A real key is needed; check pricing and free-model availability."],
        ],
    )
    document.add_paragraph(
        "Never commit real keys. A dummy key cannot produce real hosted model "
        "answers. Free hosted model availability can change."
    )

    document.add_page_break()
    add_heading(document, "10. Safe learning roadmap")
    roadmap = [
        "Change the heading text in frontend/index.html and refresh the browser.",
        "Change a color or spacing rule in frontend/styles.css.",
        "Inspect a request in frontend/app.js and compare it with the FastAPI route in app.py.",
        "Ask a question and a follow-up; note how the message list includes earlier turns.",
        "Use New chat and confirm only this browser's history is cleared.",
        "Change one safe local setting at a time, restart the server, and observe the behavior.",
        "Add a test in test_app.py before changing core behavior.",
        "Read the error response and server log when a request fails; do not hide errors with fake successful replies.",
    ]
    for item in roadmap:
        add_number(document, item)
    add_heading(document, "Important safety boundary", 2)
    document.add_paragraph(
        "This app is for local practice. Before exposing it to the internet, it "
        "would need real user authentication and authorization, HTTPS, rate limits, "
        "CSRF protections, secure production secret management, privacy and retention "
        "rules, monitoring, backups, and a production database setup. Do not expose "
        "your local MySQL server or Ollama port publicly."
    )
    add_heading(document, "Quick start checklist", 2)
    for item in [
        "MySQL running on 127.0.0.1:3306",
        "Ollama running and llama3.2:3b listed by ollama list",
        ".env.local has the right private MySQL settings and LLM_DEMO_MODE=false",
        "Uvicorn running in the project folder on port 8000",
        "Browser open at http://127.0.0.1:8000",
        "A question and follow-up both received model answers",
    ]:
        add_bullet(document, item)

    document.core_properties.title = "LLM Chat App: A-to-Z Beginner Guide"
    document.core_properties.subject = "How to build, configure, run, and test a local AI chat app"
    document.core_properties.author = "LLM Chat Practice"
    document.save(OUTPUT)
    print(f"Created {OUTPUT}")


if __name__ == "__main__":
    build_document()
