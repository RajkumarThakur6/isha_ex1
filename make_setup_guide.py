"""Generate the beginner PDF for running the local LLM chat app."""

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    Preformatted,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

OUTPUT = Path(__file__).with_name("OpenAI_Chat_App_Setup_Guide.pdf")

INK = colors.HexColor("#18343B")
TEAL = colors.HexColor("#247E78")
MUTED = colors.HexColor("#526B70")
PALE = colors.HexColor("#E5F1EC")
PAPER = colors.HexColor("#F7F8F4")
CORAL = colors.HexColor("#D96C4F")


def build_pdf() -> None:
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="CoverTitle",
            parent=styles["Title"],
            fontName="Helvetica-Bold",
            fontSize=27,
            leading=33,
            textColor=INK,
            alignment=TA_CENTER,
            spaceAfter=13,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Deck",
            parent=styles["Normal"],
            fontSize=12,
            leading=18,
            textColor=MUTED,
            alignment=TA_CENTER,
        )
    )
    styles.add(
        ParagraphStyle(
            name="H1Custom",
            parent=styles["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=21,
            leading=26,
            textColor=INK,
            spaceAfter=10,
        )
    )
    styles.add(
        ParagraphStyle(
            name="H2Custom",
            parent=styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=13,
            leading=17,
            textColor=TEAL,
            spaceBefore=8,
            spaceAfter=5,
        )
    )
    styles.add(
        ParagraphStyle(
            name="BodyCustom",
            parent=styles["BodyText"],
            fontSize=9.5,
            leading=14,
            textColor=INK,
            spaceAfter=6,
        )
    )
    styles.add(
        ParagraphStyle(
            name="SmallCustom",
            parent=styles["BodyText"],
            fontSize=8,
            leading=11,
            textColor=MUTED,
            spaceAfter=4,
        )
    )
    styles.add(
        ParagraphStyle(
            name="CodeCustom",
            fontName="Courier",
            fontSize=8,
            leading=11,
            textColor=INK,
            backColor=PAPER,
            borderColor=colors.HexColor("#D7E2DE"),
            borderWidth=0.5,
            borderPadding=8,
            leftIndent=4,
            rightIndent=4,
            spaceBefore=3,
            spaceAfter=8,
        )
    )

    doc = SimpleDocTemplate(
        str(OUTPUT),
        pagesize=letter,
        rightMargin=0.68 * inch,
        leftMargin=0.68 * inch,
        topMargin=0.64 * inch,
        bottomMargin=0.62 * inch,
        title="LLM Chat App: Beginner Setup Guide",
        author="LLM Chat Practice",
    )
    story = []

    story.extend(
        [
            Spacer(1, 0.45 * inch),
            Paragraph("Your First Local AI Chat App", styles["CoverTitle"]),
            Paragraph(
                "A gentle, practical guide to connecting a browser interface "
                "to a Python backend and an AI model.",
                styles["Deck"],
            ),
            Spacer(1, 0.35 * inch),
        ]
    )

    flow_rows = [
        [
            Paragraph("<b>1 · Browser</b><br/>HTML, CSS and JavaScript", styles["BodyCustom"]),
            Paragraph("<b>2 · Backend</b><br/>FastAPI validates and routes", styles["BodyCustom"]),
            Paragraph("<b>3 · Model</b><br/>Ollama or a hosted provider replies", styles["BodyCustom"]),
        ],
        [
            Paragraph("Collects a message and shows the answer.", styles["SmallCustom"]),
            Paragraph("Keeps provider settings private; stores chat history.", styles["SmallCustom"]),
            Paragraph("Receives only server-to-server API requests.", styles["SmallCustom"]),
        ],
    ]
    flow = Table(flow_rows, colWidths=[2.28 * inch] * 3, rowHeights=[0.54 * inch, 0.65 * inch])
    flow.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), PALE),
                ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#D7E2DE")),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.white),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
                ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    story.extend([flow, Spacer(1, 0.25 * inch)])
    story.append(Paragraph("What you will build", styles["H2Custom"]))
    story.append(
        Paragraph(
            "A small, locally run learning app. The browser sends a message to "
            "<font name='Courier'>/api/chat</font>; Python adds the current browser's "
            "saved conversation and calls the configured provider; the reply comes back to the browser. "
            "MySQL stores chats separately using a private, HttpOnly browser cookie.",
            styles["BodyCustom"],
        )
    )
    story.append(Paragraph("Project map", styles["H2Custom"]))
    file_rows = [
        ["File / folder", "Purpose"],
        ["app.py", "FastAPI backend, API routes, cookie session and MySQL storage."],
        ["practice.py", "OpenAI-compatible client; connects to Ollama, OpenAI, or OpenRouter."],
        ["frontend/", "Browser interface: HTML, CSS and JavaScript."],
        [".env.local", "Private provider key and local settings; do not commit."],
        ["MySQL database", "Local MySQL server stores chat messages."],
        ["requirements.txt", "Python packages needed by the app and tests."],
    ]
    file_table = Table(file_rows, colWidths=[1.65 * inch, 5.19 * inch], repeatRows=1)
    file_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), INK),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTNAME", (0, 1), (0, -1), "Courier"),
                ("FONTSIZE", (0, 0), (-1, -1), 8.4),
                ("LEADING", (0, 0), (-1, -1), 11),
                ("TEXTCOLOR", (0, 1), (-1, -1), INK),
                ("BACKGROUND", (0, 1), (-1, -1), PAPER),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [PAPER, colors.white]),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#D7E2DE")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 7),
                ("RIGHTPADDING", (0, 0), (-1, -1), 7),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    story.extend([file_table, PageBreak()])

    story.append(Paragraph("1. Set it up on Windows", styles["H1Custom"]))
    story.append(
        Paragraph(
            "Open PowerShell in the project folder. Create an isolated Python "
            "environment, activate it, and install the project packages:",
            styles["BodyCustom"],
        )
    )
    story.append(
        Preformatted(
            "py -m venv .venv\n"
            ".\\.venv\\Scripts\\Activate.ps1\n"
            "python -m pip install -r requirements.txt",
            styles["CodeCustom"],
        )
    )
    story.append(
        Paragraph(
            "If PowerShell blocks activation, use "
            "<font name='Courier'>.\\.venv\\Scripts\\python.exe</font> in place of "
            "<font name='Courier'>python</font> in the commands below.",
            styles["SmallCustom"],
        )
    )
    story.append(Paragraph("Install Ollama and configure the app", styles["H2Custom"]))
    story.append(
        Paragraph(
            "Install Ollama for Windows from ollama.com/download/windows. After "
            "installation, Ollama runs locally; open PowerShell and download the "
            "Llama 3.2 model used by this app. Its first download can take time and "
            "disk space.",
            styles["BodyCustom"],
        )
    )
    story.append(
        Preformatted(
            "ollama pull llama3.2:3b\n"
            "ollama run llama3.2:3b",
            styles["CodeCustom"],
        )
    )
    story.append(
        Paragraph(
            "The second command starts a simple terminal chat; type /bye to leave. "
            "Copy .env.example to .env.local for a new setup; if .env.local already "
            "exists, preserve its MySQL values and update only the LLM settings. "
            "The app leaves any existing .env file untouched. Your local MySQL "
            "service must also be running.",
            styles["BodyCustom"],
        )
    )
    story.append(
        Preformatted(
            "LLM_PROVIDER=ollama\n"
            "LLM_MODEL=llama3.2:3b\n"
            "LLM_BASE_URL=http://127.0.0.1:11434/v1\n"
            "LLM_DEMO_MODE=false\n"
            "MYSQL_HOST=127.0.0.1\n"
            "MYSQL_PORT=3306\n"
            "MYSQL_DATABASE=genai_chat_practice\n"
            "MYSQL_USER=root\n"
            "MYSQL_PASSWORD=your-local-mysql-password\n"
            "COOKIE_SECURE=false",
            styles["CodeCustom"],
        )
    )
    story.append(
        Paragraph(
            "Ollama runs the model on your computer and does not need a cloud API "
            "key or paid API account. LM Studio is another local option: set "
            "<font name='Courier'>LLM_PROVIDER=lmstudio</font>, "
            "<font name='Courier'>LLM_BASE_URL=http://127.0.0.1:1234/v1</font>, "
            "and <font name='Courier'>LLM_MODEL</font> to the model ID loaded in "
            "LM Studio, then start its Local Server. For hosted alternatives, set "
            "<font name='Courier'>LLM_PROVIDER=openai</font> and "
            "<font name='Courier'>OPENAI_API_KEY</font>, or use "
            "<font name='Courier'>LLM_PROVIDER=openrouter</font> and "
            "<font name='Courier'>OPENROUTER_API_KEY</font>. Hosted usage may cost "
            "money; check provider pricing and limits. OpenRouter free-model "
            "availability can change. Demo mode is optional: set "
            "<font name='Courier'>LLM_DEMO_MODE=true</font> to return sample echoes "
            "without making any model request. Never put real keys or passwords in "
            "JavaScript, HTML, a screenshot, or Git. The .env.local file is ignored "
            "by Git. If using OpenAI, create a key at "
            "<link href='https://platform.openai.com/api-keys' color='#247E78'>"
            "platform.openai.com/api-keys</link>, then check API billing at "
            "<link href='https://platform.openai.com/settings/organization/billing/overview' color='#247E78'>"
            "the OpenAI billing page</link>. API usage is billed separately from a "
            "ChatGPT subscription.",
            styles["BodyCustom"],
        )
    )
    story.append(Paragraph("Start the backend and frontend", styles["H2Custom"]))
    story.append(
        Preformatted(
            "python -m uvicorn app:app --reload --host 127.0.0.1 --port 8000",
            styles["CodeCustom"],
        )
    )
    story.append(
        Paragraph(
            "Open <b>http://127.0.0.1:8000</b> in your browser. FastAPI serves the "
            "frontend and backend from the same local server, so no separate frontend "
            "server or CORS setup is needed. Press Ctrl+C in PowerShell to stop.",
            styles["BodyCustom"],
        )
    )
    story.append(Paragraph("Try it and run the tests", styles["H2Custom"]))
    story.append(
        Preformatted(
            "python -m unittest -v test_app",
            styles["CodeCustom"],
        )
    )
    story.append(
        Paragraph(
            "The tests use a fake model reply and a temporary MySQL database: they "
            "check routing, history, and browser session separation without hosted "
            "API requests or quota. "
            "<font name='Courier'>http://127.0.0.1:8000/docs</font> shows the backend API.",
            styles["BodyCustom"],
        )
    )
    story.append(PageBreak())

    story.append(Paragraph("2. How the browser connects to Python", styles["H1Custom"]))
    steps = [
        ("1", "The browser loads the page from FastAPI at /."),
        ("2", "frontend/app.js sends JSON to POST /api/chat."),
        ("3", "FastAPI validates the message and reads the browser's session history from MySQL."),
        ("4", "practice.py sends the message list to the selected OpenAI-compatible provider."),
        ("5", "The backend saves the user message and reply, then returns JSON to the browser."),
        ("6", "The browser renders the reply as text (not executable HTML)."),
    ]
    step_data = [[Paragraph(f"<b>{n}</b>", styles["BodyCustom"]), Paragraph(text, styles["BodyCustom"])] for n, text in steps]
    step_table = Table(step_data, colWidths=[0.45 * inch, 6.39 * inch])
    step_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, -1), PALE),
                ("TEXTCOLOR", (0, 0), (0, -1), TEAL),
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#D7E2DE")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
            ]
        )
    )
    story.extend([step_table, Spacer(1, 10)])
    story.append(Paragraph("Useful backend endpoints", styles["H2Custom"]))
    endpoint_rows = [
        ["Method + path", "What it does"],
        ["GET /api/health", "Shows the server, model, and whether it is in demo or live mode."],
        ["GET /api/history", "Returns the current browser session's saved messages."],
        ["POST /api/chat", "Validates a message, asks the configured provider, and saves a successful turn."],
        ["POST /api/clear", "Clears only the current browser session's chat."],
    ]
    endpoint_table = Table(endpoint_rows, colWidths=[2.0 * inch, 4.84 * inch], repeatRows=1)
    endpoint_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), INK),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTNAME", (0, 1), (0, -1), "Courier"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("LEADING", (0, 0), (-1, -1), 10.5),
                ("BACKGROUND", (0, 1), (-1, -1), PAPER),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [PAPER, colors.white]),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#D7E2DE")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 7),
                ("RIGHTPADDING", (0, 0), (-1, -1), 7),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    story.extend([endpoint_table, Spacer(1, 10)])
    story.append(
        Paragraph(
            "The frontend and backend are same-origin: JavaScript calls relative "
            "paths such as <font name='Courier'>/api/chat</font>. The browser sends "
            "an HttpOnly session cookie automatically. JavaScript never receives "
            "the provider secret or a caller-chosen database session ID.",
            styles["BodyCustom"],
        )
    )
    story.append(
        Preformatted(
            "Browser  -- POST /api/chat {\"message\": \"Hi\"} -->  FastAPI\n"
            "FastAPI  -- server-side model request --> Ollama / hosted provider\n"
            "Browser  <-- {\"reply\": \"Hello!\"} ---------------- FastAPI",
            styles["CodeCustom"],
        )
    )
    story.append(PageBreak())

    story.append(Paragraph("3. Chat memory, errors, and safe habits", styles["H1Custom"]))
    story.append(Paragraph("How follow-up questions work", styles["H2Custom"]))
    story.append(
        Paragraph(
            "The model does not automatically know what you asked on an earlier request. "
            "This app loads up to the last 20 saved messages for the current browser "
            "session, adds the new question, and sends that list together. A successful "
            "user/assistant pair is saved to MySQL. Each browser gets a random, "
            "HttpOnly session cookie; /clear deletes only that session's rows. "
            "Restarting the server does not delete MySQL history.",
            styles["BodyCustom"],
        )
    )
    story.append(Paragraph("If something goes wrong", styles["H2Custom"]))
    error_rows = [
        ["What you see", "What to check"],
        ["Replies only echo your prompt", "Demo mode is on; set LLM_DEMO_MODE=false and restart."],
        ["Cannot reach Ollama", "Install/start Ollama, run ollama pull llama3.2:3b, then retry."],
        ["Hosted provider key is missing", "Set OPENAI_API_KEY or OPENROUTER_API_KEY in .env.local."],
        ["Provider rejected the key", "Check the key, account access, and provider settings."],
        ["Rate or usage limit reached", "Check the selected provider's usage limits and billing."],
        ["Could not connect to a hosted provider", "Check internet access and provider settings."],
        ["Page does not load", "Confirm Uvicorn is still running and visit http://127.0.0.1:8000."],
    ]
    error_table = Table(error_rows, colWidths=[2.0 * inch, 4.84 * inch], repeatRows=1)
    error_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), CORAL),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("LEADING", (0, 0), (-1, -1), 10.5),
                ("BACKGROUND", (0, 1), (-1, -1), PAPER),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [PAPER, colors.white]),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#D7E2DE")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 7),
                ("RIGHTPADDING", (0, 0), (-1, -1), 7),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    story.extend([error_table, Spacer(1, 8)])
    story.append(Paragraph("Learning code, not public deployment", styles["H2Custom"]))
    story.append(
        Paragraph(
            "This is a local practice app, not a ready-to-publish multi-user service. "
            "Before putting it on the public internet, add user authentication and "
            "authorization, HTTPS, rate limiting, CSRF protection, secure secret "
            "storage, privacy/retention controls, monitoring, and a production database. "
            "Use COOKIE_SECURE=true only behind HTTPS. Keep Uvicorn bound to "
            "127.0.0.1 while learning.",
            styles["BodyCustom"],
        )
    )
    story.append(Paragraph("A good learning sequence", styles["H2Custom"]))
    story.append(
        Paragraph(
            "Recommended no-key first test: Ollama with llama3.2:3b. For hosted "
            "models, check current availability and price before use. 1) Send one message. "
            "2) Read the JSON reply. 3) Ask a follow-up. "
            "4) Inspect the browser Network panel and the /api/chat request. "
            "5) Find the matching route in app.py and the provider call in practice.py. "
            "6) Change LLM_MODEL or LLM_PROVIDER and observe what happens.",
            styles["BodyCustom"],
        )
    )

    def draw_page(canvas, document):
        canvas.saveState()
        canvas.setStrokeColor(colors.HexColor("#D7E2DE"))
        canvas.line(0.68 * inch, 0.48 * inch, 7.82 * inch, 0.48 * inch)
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(MUTED)
        canvas.drawString(0.68 * inch, 0.31 * inch, "LLM Chat Practice · Ollama / OpenAI-compatible + FastAPI")
        canvas.drawRightString(7.82 * inch, 0.31 * inch, f"Page {document.page}")
        canvas.restoreState()

    doc.build(story, onFirstPage=draw_page, onLaterPages=draw_page)
    print(f"Created {OUTPUT}")


if __name__ == "__main__":
    build_pdf()
