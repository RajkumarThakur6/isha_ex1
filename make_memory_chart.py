from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Inches, Pt


OUTPUT = "LLM_API_Beginner_Guide.pptx"
WIDTH = 13.333
HEIGHT = 7.5
PAGE_COUNT = 6

INK = "18343B"
MUTED = "526B70"
PAPER = "F7F8F4"
WHITE = "FFFFFF"
LINE = "D7E2DE"
TEAL = "247E78"
CORAL = "D96C4F"
GOLD = "D3A637"
BLUE = "4C91A1"
MINT = "E5F1EC"
PALE_CORAL = "F9EBE5"
PALE_GOLD = "F7F1DF"
PALE_BLUE = "E9F2F4"


def color(value):
    return RGBColor.from_string(value)


def add_box(slide, x, y, width, height, fill, outline=None, shape=MSO_SHAPE.RECTANGLE):
    item = slide.shapes.add_shape(
        shape, Inches(x), Inches(y), Inches(width), Inches(height)
    )
    item.fill.solid()
    item.fill.fore_color.rgb = color(fill)
    item.line.color.rgb = color(outline or fill)
    return item


def add_text(
    slide,
    text,
    x,
    y,
    width,
    height,
    size,
    fill=INK,
    bold=False,
    font="Aptos",
    align=PP_ALIGN.LEFT,
):
    item = slide.shapes.add_textbox(
        Inches(x), Inches(y), Inches(width), Inches(height)
    )
    frame = item.text_frame
    frame.clear()
    frame.word_wrap = True
    frame.margin_left = Inches(0.04)
    frame.margin_right = Inches(0.04)
    frame.margin_top = Inches(0.02)
    frame.margin_bottom = Inches(0.02)
    frame.vertical_anchor = MSO_ANCHOR.MIDDLE
    for index, line in enumerate(text.split("\n")):
        paragraph = frame.paragraphs[0] if index == 0 else frame.add_paragraph()
        paragraph.text = line
        paragraph.alignment = align
        paragraph.space_after = Pt(3)
        for run in paragraph.runs:
            run.font.name = font
            run.font.size = Pt(size)
            run.font.bold = bold
            run.font.color.rgb = color(fill)
    return item


def add_base(slide, page, title, subtitle):
    slide.background.fill.solid()
    slide.background.fill.fore_color.rgb = color(PAPER)
    add_box(slide, 0, 0, WIDTH, 0.1, TEAL)
    add_text(slide, "LLM API / PYTHON STARTER", 0.62, 0.3, 3.3, 0.25,
             10, TEAL, True)
    add_text(slide, title, 0.62, 0.68, 12.0, 0.55,
             27, INK, True, "Georgia")
    add_text(slide, subtitle, 0.65, 1.28, 12.0, 0.4, 12, MUTED)
    add_text(slide, f"{page:02d}  /  {PAGE_COUNT:02d}", 11.55, 7.08, 1.15, 0.2,
             9, MUTED, True, align=PP_ALIGN.RIGHT)


def add_card(slide, x, y, width, height, title, body, accent, tint=WHITE):
    add_box(slide, x, y, width, height, tint, LINE)
    add_box(slide, x, y, 0.1, height, accent)
    add_text(slide, title, x + 0.24, y + 0.16, width - 0.45, 0.35,
             15, accent, True)
    add_text(slide, body, x + 0.24, y + 0.58, width - 0.48, height - 0.72,
             12, INK)


def add_code_panel(slide, x, y, width, height, title, code, accent=TEAL):
    add_box(slide, x, y, width, height, WHITE, LINE)
    add_box(slide, x, y, width, 0.1, accent)
    add_text(slide, title, x + 0.22, y + 0.2, width - 0.44, 0.32,
             12, accent, True)
    add_box(slide, x + 0.18, y + 0.65, width - 0.36, height - 0.83,
            PAPER, PAPER)
    add_text(slide, code, x + 0.34, y + 0.75, width - 0.68, height - 1.0,
             11, INK, False, "Consolas")


def slide_one(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_base(slide, 1, "Your First LLM API Chat",
             "A beginner-friendly guide: connect Python to an AI model, ask a question, and keep the conversation.")
    add_box(slide, 0.65, 2.0, 12.0, 3.2, INK, INK)
    add_text(slide, "A simple request travels through five steps", 0.98, 2.28,
             10.9, 0.4, 20, WHITE, True, "Georgia")

    steps = [
        ("YOU", "Ask a question", TEAL),
        ("PYTHON", "Builds the request", BLUE),
        ("API KEY", "Proves access", GOLD),
        ("LLM", "Generates a reply", CORAL),
        ("ANSWER", "Returns to Python", TEAL),
    ]
    x_positions = [0.98, 3.32, 5.66, 8.0, 10.34]
    for index, (label, description, accent) in enumerate(steps):
        x = x_positions[index]
        add_box(slide, x, 3.12, 1.9, 1.25, WHITE, WHITE)
        add_text(slide, label, x + 0.1, 3.28, 1.7, 0.32,
                 13, accent, True, align=PP_ALIGN.CENTER)
        add_text(slide, description, x + 0.12, 3.68, 1.66, 0.44,
                 10, INK, False, align=PP_ALIGN.CENTER)
        if index < len(steps) - 1:
            add_text(slide, ">", x + 1.98, 3.53, 0.32, 0.4,
                     20, "A8D8CC", True, align=PP_ALIGN.CENTER)

    add_text(slide, "KEY IDEA", 0.72, 5.58, 1.15, 0.26, 10, CORAL, True)
    add_text(slide, "Your Python app connects to a model using the provider's API.",
             1.85, 5.51, 9.95, 0.36, 15, INK, True)
    add_text(slide, "The examples use Gemini; the same building blocks apply to many LLM providers.",
             0.72, 6.15, 11.8, 0.35, 12, MUTED)


def slide_two(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_base(slide, 2, "Four Things Your App Needs",
             "Think of asking an AI model like sending a message through a service.")
    cards = [
        (0.68, "1 / API KEY", "A secret password for your app to access a provider.\nKeep it private.", TEAL, MINT),
        (3.78, "2 / PYTHON SDK", "A package that makes it easier for Python to talk to that provider.", BLUE, PALE_BLUE),
        (6.88, "3 / MODEL", "The particular AI model you choose, such as a supported Gemini model.", GOLD, PALE_GOLD),
        (9.98, "4 / PROMPT", "The question or instruction you send to the model.", CORAL, PALE_CORAL),
    ]
    for x, title, body, accent, tint in cards:
        add_card(slide, x, 2.12, 2.68, 2.8, title, body, accent, tint)

    add_box(slide, 0.68, 5.35, 12.0, 0.92, INK, INK)
    add_text(slide, "API KEY  +  SDK  +  MODEL  +  PROMPT   ->   AI RESPONSE",
             0.95, 5.56, 11.45, 0.4, 16, WHITE, True,
             "Consolas", PP_ALIGN.CENTER)
    add_text(slide, "The API key gives access; it is not the model name.",
             0.72, 6.48, 11.7, 0.3, 12, MUTED, True)


def slide_three(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_base(slide, 3, "Read the Python: One Chat Turn",
             "This uses the Gemini Python SDK, as in your practice script. Other providers use different SDK syntax.")
    code = (
        "import os\n"
        "from dotenv import load_dotenv\n"
        "from google import genai\n\n"
        "load_dotenv()  # read values from .env\n"
        "api_key = os.getenv(\"GEMINI_API_KEY\")\n"
        "client = genai.Client(api_key=api_key)\n\n"
        "chat = client.chats.create(\n"
        "    model=\"gemini-3.8-flash\"\n"
        ")\n"
        "response = chat.send_message(\"Say hello\")\n"
        "print(response.text)"
    )
    add_code_panel(slide, 0.68, 1.92, 6.0, 4.65,
                   "THE REQUEST", code, TEAL)
    add_card(slide, 7.02, 1.92, 5.65, 1.05,
             "CLIENT", "Sets up a connection using your API key.", TEAL, MINT)
    add_card(slide, 7.02, 3.17, 5.65, 1.05,
             "SEND", "Sends your prompt to the chosen model.", BLUE, PALE_BLUE)
    add_card(slide, 7.02, 4.42, 5.65, 1.05,
             "RESPONSE", "Contains the text the model generated.", CORAL, PALE_CORAL)
    add_text(slide, "You can change the prompt and model without changing the basic request flow.",
             7.08, 5.78, 5.45, 0.58, 12, MUTED, True)


def slide_four(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_base(slide, 4, "How Chat Memory Works",
             "The model does not automatically know what you said earlier. Your app sends the conversation history again.")
    add_box(slide, 0.72, 2.0, 5.5, 3.9, WHITE, LINE)
    add_text(slide, "SAVED CHAT HISTORY", 1.0, 2.25, 4.95, 0.33,
             13, TEAL, True)
    add_box(slide, 1.0, 2.85, 4.95, 0.88, MINT, MINT)
    add_text(slide, "You: My name is Isha.", 1.2, 3.04, 4.55, 0.4,
             14, INK, False, "Consolas")
    add_box(slide, 1.0, 3.92, 4.95, 0.88, PALE_BLUE, PALE_BLUE)
    add_text(slide, "AI: Nice to meet you, Isha!", 1.2, 4.11, 4.55, 0.4,
             14, INK, False, "Consolas")
    add_text(slide, "Saved locally in .chat_memory.json", 1.0, 5.18,
             4.95, 0.36, 11, MUTED)

    add_text(slide, "+", 6.35, 3.24, 0.55, 0.55, 26, GOLD, True,
             align=PP_ALIGN.CENTER)
    add_box(slide, 7.02, 2.55, 2.2, 1.48, PALE_GOLD, PALE_GOLD)
    add_text(slide, "NEW QUESTION", 7.18, 2.83, 1.88, 0.28,
             11, GOLD, True, align=PP_ALIGN.CENTER)
    add_text(slide, "What is my name?", 7.18, 3.22, 1.88, 0.45,
             12, INK, False, align=PP_ALIGN.CENTER)
    add_text(slide, "->", 9.36, 3.02, 0.48, 0.42, 20, TEAL, True,
             align=PP_ALIGN.CENTER)
    add_box(slide, 9.95, 2.55, 2.45, 1.48, INK, INK)
    add_text(slide, "HISTORY + QUESTION", 10.1, 2.83, 2.15, 0.3,
             10, WHITE, True, align=PP_ALIGN.CENTER)
    add_text(slide, "Sent to the model", 10.12, 3.22, 2.1, 0.4,
             12, WHITE, False, align=PP_ALIGN.CENTER)
    add_card(slide, 7.02, 4.38, 5.38, 1.38,
             "IN YOUR SCRIPT", "Load saved turns when chat starts; save new turns after a reply. Use /clear to start over.",
             CORAL, PALE_CORAL)
    add_text(slide, "That is why Gemini can answer the follow-up about Isha.",
             0.78, 6.3, 11.7, 0.34, 13, INK, True)


def slide_five(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_base(slide, 5, "Keep Your Key Safe; Know Your Limits",
             "A real API key is private. Usage limits and prices are controlled by the provider and your account.")
    add_box(slide, 0.7, 2.0, 5.85, 3.75, WHITE, LINE)
    add_box(slide, 0.7, 2.0, 0.1, 3.75, TEAL)
    add_text(slide, "SAFE KEY HABITS", 0.98, 2.25, 5.2, 0.36,
             15, TEAL, True)
    add_text(slide,
             "1. Put the key in a .env file\n"
             "2. Read it with os.getenv(...)\n"
             "3. Add .env to .gitignore\n"
             "4. Never print or share the real key",
             1.0, 2.86, 5.05, 1.65, 14, INK)
    add_box(slide, 1.0, 4.75, 5.05, 0.58, MINT, MINT)
    add_text(slide, "GEMINI_API_KEY=your-key-goes-here",
             1.15, 4.88, 4.75, 0.3, 11, INK, False, "Consolas")

    add_box(slide, 6.82, 2.0, 5.85, 3.75, WHITE, LINE)
    add_box(slide, 6.82, 2.0, 0.1, 3.75, CORAL)
    add_text(slide, "WHEN YOU SEE A QUOTA ERROR", 7.1, 2.25,
             5.2, 0.36, 15, CORAL, True)
    add_text(slide,
             "The provider may limit how many requests you can make.\n\n"
             "RESOURCE_EXHAUSTED means a usage limit was reached.\n\n"
             "Wait for the reset time or check your provider's plan. Your script should show the error clearly.",
             7.12, 2.82, 5.05, 2.45, 13, INK)
    add_text(slide, "Never put your real API key in a screenshot, chat, or source code.",
             0.78, 6.2, 11.8, 0.4, 13, INK, True)


def slide_six(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_base(slide, 6, "Can I Use a Different LLM Provider?",
             "Yes. Keep the idea; change the provider-specific setup. Always check that provider's current documentation.")
    add_box(slide, 0.72, 2.0, 5.85, 3.2, MINT, MINT)
    add_text(slide, "SAME BASIC IDEAS", 1.02, 2.27, 5.1, 0.36,
             15, TEAL, True)
    add_text(slide,
             "• A private API key\n"
             "• A Python app sends a prompt\n"
             "• A model generates a reply\n"
             "• Your app can send chat history",
             1.05, 2.92, 5.0, 1.7, 14, INK)

    add_box(slide, 6.82, 2.0, 5.85, 3.2, PALE_BLUE, PALE_BLUE)
    add_text(slide, "CHANGES BY PROVIDER", 7.12, 2.27, 5.1, 0.36,
             15, BLUE, True)
    add_text(slide,
             "• Python package / SDK\n"
             "• Client setup and key name\n"
             "• Available model names\n"
             "• Request and response syntax",
             7.15, 2.92, 5.0, 1.7, 14, INK)

    add_box(slide, 0.72, 5.52, 11.95, 0.85, INK, INK)
    add_text(slide, "Learn one provider first. Then switch using its own SDK guide and examples.",
             1.0, 5.75, 11.35, 0.38, 15, WHITE, True,
             align=PP_ALIGN.CENTER)
    add_text(slide, "API keys are issued by providers; one provider's key usually cannot access another provider's model.",
             0.78, 6.56, 11.8, 0.34, 11, MUTED, True)


def main():
    presentation = Presentation()
    presentation.slide_width = Inches(WIDTH)
    presentation.slide_height = Inches(HEIGHT)
    slide_one(presentation)
    slide_two(presentation)
    slide_three(presentation)
    slide_four(presentation)
    slide_five(presentation)
    slide_six(presentation)
    presentation.save(OUTPUT)
    print(f"Created {OUTPUT}")


if __name__ == "__main__":
    main()
