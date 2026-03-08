#!/usr/bin/env python3
"""
Generate email draft to Dr. Keryn Pasch regarding publication strategy.
Output: deliverables/email_to_pasch.docx
"""

from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
import os

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "deliverables")
os.makedirs(OUTPUT_DIR, exist_ok=True)
OUTPUT_PATH = os.path.join(OUTPUT_DIR, "email_to_pasch.docx")


def build_document():
    doc = Document()

    for section in doc.sections:
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.right_margin = Inches(1)

    style = doc.styles["Normal"]
    style.font.name = "Calibri"
    style.font.size = Pt(12)
    style.paragraph_format.line_spacing = 1.15
    style.paragraph_format.space_after = Pt(6)

    # ── Email Headers ──
    headers = [
        ("From:", "Jacob (Jake) Thomas"),
        ("To:", "Dr. Keryn Pasch"),
        ("Subject:", "Publication Plan for the Dissertation"),
    ]
    for label, value in headers:
        p = doc.add_paragraph()
        run_label = p.add_run(label + " ")
        run_label.bold = True
        p.add_run(value)

    # Separator
    p = doc.add_paragraph()
    run = p.add_run("\u2014" * 40)
    run.font.color.rgb = None

    # ── Body ──
    doc.add_paragraph(
        "Hi Keryn,"
    )

    doc.add_paragraph(
        "I wanted to let you know what my publication plan looks like for the "
        "dissertation. It\u2019s going to be a little unconventional, but I\u2019ve thought it "
        "through carefully, and I\u2019m confident it\u2019s the right approach given the "
        "circumstances."
    )

    doc.add_paragraph(
        "Here\u2019s where things stand honestly: the data are from 2019\u20132021, the "
        "dissertation took seven years, and the field hasn\u2019t been waiting around. "
        "The traditional route\u2014two full-length journal articles, 6\u201312 months per "
        "round of review, revise, resubmit\u2014would mean another one to two years "
        "before anything sees daylight. By then, the pandemic alcohol marketing "
        "literature will have moved on. The window for this work to land is now, "
        "not 2028."
    )

    doc.add_paragraph(
        "So here\u2019s the plan. I\u2019m breaking the dissertation into four outputs that "
        "can move quickly and reach different audiences:"
    )

    # Numbered list
    items = [
        (
            'A popular history book ("The Drinking Age"), based on Part A. ',
            "I\u2019ve already written a full historical account of the alcohol industry\u2019s "
            "relationship with marketing regulation. There is genuinely nothing like "
            "it out there\u2014no single book tells this story in an accessible way. This "
            "is a unique contribution that no journal article could capture, and it\u2019s "
            "essentially ready to go."
        ),
        (
            "A methodology preprint and open-source software tool. ",
            "I\u2019m calling the method Embedding-to-Explanation Topic Modeling (E2E). "
            "It\u2019s the BERTopic + LLM pipeline I built for the dissertation\u2014it uses "
            "Claude now for the explanation step\u2014and I\u2019m releasing it as both a "
            "preprint and a web app. Publishing the preprint immediately establishes "
            "priority on the methodology and gives it a citable home right away. The "
            "tool is already packaged and documented."
        ),
        (
            "Two brief research reports, one for each study. ",
            "Study 1 covers the topic model and prevalence analysis; Study 2 covers "
            "the cross-lagged panel model linking industry tweets to user-generated "
            "content. Both cite the E2E preprint for methodology, which keeps them "
            "concise and focused on the findings. Brief reports are peer-reviewed "
            "and respected\u2014they\u2019re just faster."
        ),
        (
            "An HTML portfolio and dissection piece. ",
            "A visual, interactive summary showing how all the pieces fit together. "
            "This serves double duty: it\u2019s a demonstration piece for employers and "
            "collaborators, and it shows I can think strategically about research "
            "dissemination beyond just writing papers."
        ),
    ]
    for bold_part, rest in items:
        p = doc.add_paragraph(style="List Number")
        run = p.add_run(bold_part)
        run.bold = True
        p.add_run(rest)

    doc.add_paragraph(
        "The reason this works better than the conventional path comes down to a "
        "few things. Speed is the biggest\u2014the data are aging, and this strategy "
        "gets findings out in months, not years. The E2E methodology is genuinely "
        "novel and deserves standalone publication rather than being buried in a "
        "methods section. The book is something no journal could accommodate. And "
        "each piece cites and builds on the others, so the result is a coherent "
        "body of work: the preprint establishes priority on the computational "
        "approach, the brief reports provide the empirical evidence, the book "
        "provides historical context, and the portfolio ties it all together."
    )

    doc.add_paragraph(
        "I really do appreciate everything you\u2019ve done for me through this process, "
        "Keryn. Seven years is a long road, and your mentorship made the difference "
        "at more points than you probably realize. Thank you for that."
    )

    doc.add_paragraph(
        "I\u2019ll keep you posted as things move forward."
    )

    # Sign-off
    doc.add_paragraph("")
    doc.add_paragraph("Jake")

    doc.save(OUTPUT_PATH)
    print(f"Email draft saved to: {OUTPUT_PATH}")


if __name__ == "__main__":
    build_document()
