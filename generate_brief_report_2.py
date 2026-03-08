#!/usr/bin/env python3
"""
Generate Brief Report for Study 2:
Alcohol Industry Marketing Influence on User-Generated Content During COVID-19
Output: deliverables/brief_report_study2.docx
"""

from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.style import WD_STYLE_TYPE
import os

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "deliverables")
os.makedirs(OUTPUT_DIR, exist_ok=True)
OUTPUT_PATH = os.path.join(OUTPUT_DIR, "brief_report_study2.docx")


def setup_styles(doc):
    """Configure document styles."""
    style = doc.styles["Normal"]
    font = style.font
    font.name = "Times New Roman"
    font.size = Pt(12)
    pf = style.paragraph_format
    pf.line_spacing = 1.15
    pf.space_after = Pt(6)
    pf.space_before = Pt(0)

    for i, (size, bold) in enumerate([(14, True), (12, True)], start=1):
        if f"Heading {i}" in doc.styles:
            h = doc.styles[f"Heading {i}"]
        else:
            h = doc.styles.add_style(f"Heading {i}", WD_STYLE_TYPE.PARAGRAPH)
        h.font.name = "Times New Roman"
        h.font.size = Pt(size)
        h.font.bold = bold
        h.font.color.rgb = RGBColor(0, 0, 0)
        h.paragraph_format.space_before = Pt(12)
        h.paragraph_format.space_after = Pt(6)
        h.paragraph_format.line_spacing = 1.15


def build_document():
    doc = Document()

    for section in doc.sections:
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.right_margin = Inches(1)

    setup_styles(doc)

    # ── Title ──
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(
        "Alcohol Industry Marketing Influence on User-Generated Content\n"
        "During COVID-19 Pandemic Lockdowns"
    )
    run.bold = True
    run.font.size = Pt(14)
    run.font.name = "Times New Roman"

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run("Jacob Edward Thomas & Keryn E. Pasch")
    run.font.name = "Times New Roman"
    run.font.size = Pt(12)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run("The University of Texas at Austin")
    run.italic = True
    run.font.name = "Times New Roman"
    run.font.size = Pt(12)

    # ── Abstract ──
    doc.add_heading("Abstract", level=1)
    doc.add_paragraph(
        "This study examined bidirectional associations between alcohol brand tweets and "
        "user-generated content about alcohol delivery and isolation drinking during COVID-19 "
        "lockdowns (March\u2013May 2020). Industry data comprised 704 tweets from 11 major alcohol "
        "brands classified under the Alcohol Delivery and Isolation Drinking (AD-ID) theme "
        "(Thomas & Pasch, 2025). User data comprised 486,786 tweets from 66,303 unique U.S. "
        "users referencing alcohol delivery or isolation drinking. Cross-lagged panel modeling "
        "across two time periods revealed a significant unidirectional pathway: potential "
        "exposure to alcohol brand AD-ID tweets predicted subsequent user-generated content "
        "about the same theme (\u03b2 = 0.05, p < 0.01), but user-generated content did not "
        "predict subsequent industry output (\u03b2 = 0.01, p = 0.639). Both variables exhibited "
        "high temporal stability. These findings suggest that alcohol industry messaging "
        "during the pandemic influenced public discourse about drinking during lockdowns, "
        "rather than the industry merely responding to organic public demand."
    )

    # ── Introduction ──
    doc.add_heading("Introduction", level=1)
    doc.add_paragraph(
        "The COVID-19 pandemic was associated with significant increases in alcohol-related "
        "morbidity and mortality, particularly among young adults. White et al. (2022) reported "
        "a sharp rise in alcohol-related deaths during the pandemic period, underscoring the "
        "urgency of understanding factors that may have contributed to increased consumption. "
        "Among these factors, alcohol marketing on social media has received growing scrutiny "
        "as a potential driver of pandemic drinking behaviors."
    )
    doc.add_paragraph(
        "In a companion study (Thomas & Pasch, 2025), we identified five marketing themes "
        "used by major alcohol brands on Twitter, including Alcohol Delivery and Isolation "
        "Drinking (AD-ID), which increased by 91.2% during lockdowns and remained elevated "
        "afterward. However, identifying thematic shifts in industry output does not establish "
        "whether those shifts influenced public behavior. It is equally plausible that brands "
        "were responding to organic consumer demand\u2014that the public began discussing delivery "
        "and isolation drinking first, and brands followed."
    )
    doc.add_paragraph(
        "The Differential Susceptibility to Media Effects Model (DSMM; Valkenburg & Peter, "
        "2013) provides a framework for understanding bidirectional media influence, positing "
        "that media effects are reciprocal and contingent on individual and contextual factors. "
        "Relatedly, the concept of sociogenesis (Holder, 2006) suggests that corporate "
        "marketing can shape population-level norms and behaviors. Testing these frameworks "
        "requires examining both directions of influence simultaneously."
    )
    doc.add_paragraph(
        "The present study addresses this gap by modeling the bidirectional association between "
        "industry AD-ID tweets and user-generated content about alcohol delivery and isolation "
        "drinking during the COVID-19 lockdown period. We hypothesized that industry output "
        "would predict subsequent user content, and examined whether user content would "
        "reciprocally predict industry output."
    )

    # ── Method ──
    doc.add_heading("Method", level=1)

    doc.add_heading("Data Sources", level=2)
    doc.add_paragraph(
        "Industry data were drawn from the PRL-TMS dataset (Thomas & Pasch, 2025), comprising "
        "tweets from 11 major alcohol brands. During the lockdown period, 704 tweets were "
        "classified as AD-ID content using GPT-4o. User data were drawn from the CML-COVID "
        "dataset, a large-scale collection of U.S. user tweets referencing alcohol delivery "
        "or isolation drinking during the same period. After preprocessing, the user dataset "
        "contained 486,786 tweets from 66,303 unique users. User tweets were classified as "
        "AD-ID-relevant using the same GPT-4o classification protocol applied to industry data."
    )

    doc.add_heading("Time Periods", level=2)
    doc.add_paragraph(
        "The lockdown period was divided into two waves to enable cross-lagged modeling: "
        "T1 (March 25\u2013April 30, 2020) and T2 (May 1\u201331, 2020). This division captured "
        "the peak lockdown period and the beginning of reopening in many U.S. states, "
        "providing temporal separation sufficient for lagged effects."
    )

    doc.add_heading("Measures", level=2)
    doc.add_paragraph(
        "Potential exposure to industry AD-ID marketing was operationalized as a composite "
        "index adapted from Henriksen et al.\u2019s (2010) tobacco marketing surveillance framework: "
        "friends_count \u00d7 tweet_count \u00d7 industry_AD-ID_count. This index captures the "
        "intersection of a user\u2019s network size (potential reach), their overall tweeting "
        "activity (platform engagement), and the volume of industry AD-ID content available "
        "for exposure. User-generated AD-ID content was measured as the count of each user\u2019s "
        "tweets classified as AD-ID-relevant in each period."
    )

    doc.add_heading("Analytic Strategy", level=2)
    doc.add_paragraph(
        "A cross-lagged panel model was estimated using generalized structural equation "
        "modeling (GSEM) in Stata to accommodate the non-normal distribution of count data. "
        "The model simultaneously estimated four pathways: (1) stability of potential exposure "
        "(T1 \u2192 T2), (2) stability of user-generated content (T1 \u2192 T2), (3) the cross-lagged "
        "effect of potential exposure on subsequent user content, and (4) the cross-lagged "
        "effect of user content on subsequent potential exposure. Cross-sectional covariances "
        "were estimated at both time points."
    )

    doc.add_heading("Bot Mitigation", level=2)
    doc.add_paragraph(
        "To reduce the influence of automated accounts, we removed users who posted more than "
        "50 tweets per day on average, required that users had tweets in both time periods, "
        "and excluded statistical outliers on key variables. These steps reduced the analytic "
        "sample while improving data quality."
    )

    # ── Results ──
    doc.add_heading("Results", level=1)

    # Results table
    table = doc.add_table(rows=5, cols=4, style="Table Grid")
    headers = ["Path", "\u03b2", "SE", "p"]
    for i, h in enumerate(headers):
        cell = table.rows[0].cells[i]
        cell.text = h
        for paragraph in cell.paragraphs:
            for run in paragraph.runs:
                run.bold = True
                run.font.size = Pt(10)
                run.font.name = "Times New Roman"

    rows = [
        ["Potential Exposure T1 \u2192 T2 (stability)", "0.85", "0.003", "< 0.01"],
        ["User AD-ID Content T1 \u2192 T2 (stability)", "2.76", "0.014", "< 0.01"],
        ["Potential Exposure T1 \u2192 User Content T2 (cross-lag)", "0.05", "0.017", "< 0.01"],
        ["User Content T1 \u2192 Potential Exposure T2 (cross-lag)", "0.01", "0.021", "0.639"],
    ]
    for r, row_data in enumerate(rows, start=1):
        for c, val in enumerate(row_data):
            cell = table.rows[r].cells[c]
            cell.text = val
            for paragraph in cell.paragraphs:
                for run in paragraph.runs:
                    run.font.size = Pt(10)
                    run.font.name = "Times New Roman"

    doc.add_paragraph("")

    doc.add_paragraph(
        "The cross-lagged panel model revealed a clear unidirectional pattern. The pathway "
        "from potential exposure to industry AD-ID tweets at T1 to user-generated AD-ID "
        "content at T2 was statistically significant (\u03b2 = 0.05, SE = 0.017, p < 0.01), "
        "indicating that greater potential exposure to industry marketing predicted subsequent "
        "increases in user-generated content about alcohol delivery and isolation drinking."
    )
    doc.add_paragraph(
        "The reverse pathway\u2014from user-generated AD-ID content at T1 to potential exposure "
        "at T2\u2014was not significant (\u03b2 = 0.01, SE = 0.021, p = 0.639), providing no evidence "
        "that public discourse drove subsequent industry output. Both autoregressive stability "
        "paths were large and significant: potential exposure (\u03b2 = 0.85, p < 0.01) and "
        "user-generated content (\u03b2 = 2.76, p < 0.01), indicating high temporal consistency "
        "in both variables. Cross-sectional covariances were positive and significant at both "
        "time points, confirming the expected concurrent association between industry marketing "
        "and public discourse."
    )

    # ── Discussion ──
    doc.add_heading("Discussion", level=1)
    doc.add_paragraph(
        "This study provides evidence that alcohol industry marketing during the COVID-19 "
        "pandemic influenced public discourse about pandemic-related drinking, rather than "
        "the reverse. The significant industry-to-public pathway, combined with the "
        "non-significant public-to-industry pathway, supports a unidirectional influence "
        "model consistent with the DSMM framework and sociogenesis theory. The alcohol "
        "industry did not merely respond to organic consumer conversation about delivery "
        "and isolation drinking; it actively shaped that conversation."
    )
    doc.add_paragraph(
        "The adaptation of Henriksen et al.\u2019s (2010) tobacco marketing surveillance measure "
        "to the social media context represents a methodological contribution. The potential "
        "exposure index\u2014combining network size, platform engagement, and marketing volume\u2014"
        "provides a scalable proxy for marketing reach that does not require direct measurement "
        "of individual exposure. The high temporal stability of this measure suggests it "
        "captures a durable characteristic of users\u2019 media environments."
    )
    doc.add_paragraph(
        "Together with the companion study (Thomas & Pasch, 2025), these findings paint a "
        "coherent picture: the alcohol industry amplified specific marketing themes during "
        "the pandemic (Study 1), and these amplified themes subsequently spread into public "
        "discourse (Study 2). This two-study sequence moves beyond description to provide "
        "evidence of a directional influence process."
    )
    doc.add_paragraph(
        "Several limitations should be noted. The potential exposure measure is an index, "
        "not a direct measure of actual viewing; users in the dataset were not confirmed to "
        "have seen specific industry tweets. The sample was limited to English-language, "
        "U.S.-based Twitter users, restricting generalizability. Bot mitigation procedures, "
        "while reducing noise, were not comprehensive and some automated accounts may remain. "
        "The cross-lagged design establishes temporal precedence but cannot confirm causal "
        "mechanisms, and the two-wave structure limits our ability to model more complex "
        "dynamic processes. Finally, we cannot confirm whether increased online discourse "
        "translated into actual changes in alcohol consumption behavior."
    )
    doc.add_paragraph(
        "Despite these limitations, the findings carry public health implications. If industry "
        "marketing can demonstrably shift public discourse about alcohol during a health crisis, "
        "regulatory attention to digital marketing practices during emergencies is warranted. "
        "Future research should examine whether exposure to pandemic-era alcohol marketing "
        "predicted actual consumption changes, and whether similar influence dynamics operate "
        "on platforms beyond Twitter."
    )

    # ── References ──
    doc.add_heading("References", level=1)

    refs = [
        "Henriksen, L., Feighery, E. C., Schleicher, N. C., & Fortmann, S. P. (2010). Receptivity to alcohol marketing predicts initiation of alcohol use. Journal of Adolescent Health, 42(1), 28\u201335.",
        "Holder, H. D. (2006). Alcohol and the Community: A Systems Approach to Prevention. Cambridge University Press.",
        "Jernigan, D. H., & Ross, C. S. (2020). The alcohol marketing landscape. Journal of Studies on Alcohol and Drugs, Supplement 19, 13\u201325.",
        "Martino, F., Brooks, R., Browne, J., Carah, N., Zorbas, C., Corben, K., ... & Backholer, K. (2021). Online marketing by big food and big alcohol during COVID-19 in Australia. BMC Public Health, 21(1), 1\u201315.",
        "Pollard, M. S., Tucker, J. S., & Green, H. D. (2020). Changes in adult alcohol use during COVID-19. JAMA Network Open, 3(9), e2022942.",
        "Thomas, J. E. (2025). TopicFlow: A BERTopic and Large Language Model Pipeline for Topic Discovery and Classification. Preprint.",
        "Thomas, J. E., & Pasch, K. E. (2025). Alcohol marketing themes on Twitter during the COVID-19 pandemic: A topic modeling analysis. Manuscript in preparation.",
        "Valkenburg, P. M., & Peter, J. (2013). The Differential Susceptibility to Media Effects Model. Journal of Communication, 63(2), 221\u2013243.",
        "White, A. M., Castle, I. J., Powell, P. A., Hingson, R. W., & Koob, G. F. (2022). Alcohol-related deaths during the COVID-19 pandemic. JAMA, 327(17), 1704\u20131706.",
    ]
    for ref in refs:
        p = doc.add_paragraph(ref)
        p.paragraph_format.first_line_indent = Inches(-0.5)
        p.paragraph_format.left_indent = Inches(0.5)
        p.paragraph_format.space_after = Pt(4)
        for run in p.runs:
            run.font.size = Pt(11)
            run.font.name = "Times New Roman"

    doc.save(OUTPUT_PATH)
    print(f"Brief Report (Study 2) saved to: {OUTPUT_PATH}")


if __name__ == "__main__":
    build_document()
