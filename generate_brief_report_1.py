#!/usr/bin/env python3
"""
Generate Brief Report for Study 1:
Alcohol Marketing Themes on Twitter During the COVID-19 Pandemic
Output: deliverables/brief_report_study1.docx
"""

from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.style import WD_STYLE_TYPE
import os

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "deliverables")
os.makedirs(OUTPUT_DIR, exist_ok=True)
OUTPUT_PATH = os.path.join(OUTPUT_DIR, "brief_report_study1.docx")


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

    # Heading style
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


def add_paragraph(doc, text, style="Normal", bold=False, italic=False, alignment=None):
    p = doc.add_paragraph(style=style)
    run = p.add_run(text)
    run.bold = bold
    run.italic = italic
    if alignment is not None:
        p.alignment = alignment
    return p


def build_document():
    doc = Document()

    # Set margins
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
        "Alcohol Marketing Themes on Twitter During the COVID-19 Pandemic:\n"
        "A Topic Modeling Analysis"
    )
    run.bold = True
    run.font.size = Pt(14)
    run.font.name = "Times New Roman"

    # Authors
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
        "Alcohol brands rapidly adapted their social media marketing strategies during the "
        "COVID-19 pandemic, yet few studies have systematically tracked thematic shifts across "
        "pandemic phases. This study analyzed 5,872 tweets posted by 11 major alcohol brands "
        "between January 2019 and July 2021 using a novel computational pipeline combining "
        "BERTopic modeling with hyperparameter optimization and GPT-4o classification (Thomas, "
        "2025). Five marketing themes were identified: Alcohol Delivery and Isolation Drinking "
        "(AD-ID), Restaurant Support, Social Media Promotions, Sports, and Gaming. Proportional "
        "z-tests with Bonferroni correction revealed that three themes showed statistically "
        "significant increases during COVID-19 lockdowns (March\u2013May 2020): AD-ID (+91.2%), "
        "Restaurant Support (+189.5%), and Social Media Promotions (+150.0%). Critically, AD-ID "
        "and Social Media Promotions remained significantly elevated in the post-lockdown period "
        "(June 2020\u2013July 2021), suggesting durable shifts in alcohol marketing strategy rather "
        "than temporary responses to crisis conditions. These findings extend prior qualitative "
        "work by providing longitudinal, quantitative evidence of how the alcohol industry "
        "leveraged a public health crisis to normalize home delivery and isolation drinking."
    )

    # ── Introduction ──
    doc.add_heading("Introduction", level=1)
    doc.add_paragraph(
        "The COVID-19 pandemic fundamentally altered patterns of daily life beginning in "
        "March 2020, when governments worldwide implemented lockdowns, business closures, and "
        "social distancing mandates. These disruptions created conditions associated with "
        "increased alcohol consumption: social isolation, economic stress, disrupted routines, "
        "and heightened anxiety (Pollard et al., 2020). Concurrently, social media usage surged "
        "as people turned to digital platforms for connection, entertainment, and information "
        "(Wiederhold, 2020). This confluence of increased alcohol risk factors and heightened "
        "digital engagement created a unique opportunity for alcohol marketers."
    )
    doc.add_paragraph(
        "The alcohol industry has a well-documented history of adapting its marketing strategies "
        "to capitalize on cultural moments and public health events (Jernigan & Ross, 2020). "
        "Social media platforms are particularly amenable to such adaptation because they allow "
        "brands to shift messaging rapidly and at low cost (Barry et al., 2016). Early research "
        "during the pandemic identified several marketing themes adopted by alcohol brands, "
        "including home delivery promotions, isolation drinking normalization, and corporate "
        "social responsibility messaging (Martino et al., 2021; Gerritsen et al., 2021; "
        "Colbert et al., 2020). However, these studies were largely qualitative, focused on "
        "narrow time windows, and did not provide systematic comparisons of theme prevalence "
        "across pre-pandemic, lockdown, and post-lockdown periods."
    )
    doc.add_paragraph(
        "Moreover, existing computational approaches to analyzing large-scale social media "
        "marketing data have been limited by methodological constraints. Traditional topic "
        "models such as Latent Dirichlet Allocation (LDA) struggle with short texts (Qiang "
        "et al., 2020), and manual content analysis is impractical at scale. Recent advances "
        "in transformer-based topic modeling\u2014particularly BERTopic (Grootendorst, 2022)\u2014offer "
        "promising alternatives but require careful hyperparameter optimization and human "
        "validation to produce interpretable results."
    )
    doc.add_paragraph(
        "The present study addresses these gaps by applying a novel computational pipeline "
        "(Thomas, 2025) to a longitudinal dataset of alcohol brand tweets spanning pre-pandemic, "
        "lockdown, and post-lockdown periods. The pipeline combines BERTopic modeling with "
        "systematic hyperparameter optimization, large language model (LLM) topic naming, and "
        "GPT-4o classification. We pursued two aims: (1) identify the principal marketing "
        "themes used by major alcohol brands on Twitter, and (2) compare the prevalence of "
        "these themes across pandemic phases to determine whether observed shifts were temporary "
        "or durable."
    )

    # ── Method ──
    doc.add_heading("Method", level=1)

    doc.add_heading("Sample", level=2)
    doc.add_paragraph(
        "The dataset comprised 5,872 original tweets posted by 11 major alcohol companies "
        "between January 2019 and July 2021. These companies were drawn from the PRL-TMS "
        "(Publicly Retrievable Longitudinal Twitter Marketing Sample), a purpose-built dataset "
        "capturing the complete tweet histories of prominent alcohol brands with active U.S. "
        "marketing presences. Retweets and replies were excluded to focus on original marketing "
        "content. The sample spanned three analytically defined periods: pre-pandemic (January "
        "2019\u2013January 2020), peri-lockdown (March\u2013May 2020), and post-lockdown (June 2020\u2013"
        "July 2021)."
    )

    doc.add_heading("Theme Identification", level=2)
    doc.add_paragraph(
        "Marketing themes were identified using the TopicFlow pipeline described in Thomas "
        "(2025) and available as open-source software. The procedure involved three stages. "
        "First, BERTopic was applied with systematic hyperparameter optimization: 50 random "
        "iterations were conducted for each of 24 candidate topic solutions (ranging from 3 to "
        "50 topics), yielding 1,200 fitted models. The best-performing model was selected based "
        "on c_v coherence, a validated measure of topic interpretability (R\u00f6der et al., 2015). "
        "Second, LLM-based democratic topic naming was performed by submitting representative "
        "documents from each topic to GPT-4o across 5,000 iterations, with final labels "
        "determined by majority vote. Third, human thematic synthesis was conducted to group "
        "granular topics into higher-order marketing themes based on conceptual overlap and "
        "alignment with prior literature. The optimal model contained 7 granular topics "
        "(coherence = 0.768), which were synthesized into 5 interpretable themes: Alcohol "
        "Delivery and Isolation Drinking (AD-ID), Restaurant Support, Social Media Promotions, "
        "Sports, and Gaming."
    )

    doc.add_heading("Classification", level=2)
    doc.add_paragraph(
        "All 5,872 tweets were classified into the five themes using GPT-4o with structured "
        "prompting. Classification validity was established by comparing GPT-4o labels against "
        "human coding of a random subsample of 250 tweets, yielding agreement exceeding 85%. "
        "Tweets that did not clearly map to any theme were categorized as unclassified and "
        "excluded from prevalence analyses."
    )

    doc.add_heading("Prevalence Analysis", level=2)
    doc.add_paragraph(
        "Theme prevalence was calculated as the proportion of classified tweets assigned to "
        "each theme within each time period. Proportional z-tests were used to compare "
        "prevalence across the three periods (pre-pandemic, peri-lockdown, post-lockdown), "
        "with Bonferroni correction applied to account for multiple comparisons. This approach "
        "enabled detection of statistically significant shifts in marketing emphasis while "
        "controlling for the unequal lengths of the three periods."
    )

    # ── Results ──
    doc.add_heading("Results", level=1)
    doc.add_paragraph(
        "The BERTopic pipeline identified an optimal 7-topic model (c_v coherence = 0.768), "
        "which was synthesized into five marketing themes. Table 1 presents the prevalence "
        "of each theme across the three pandemic periods along with pairwise z-test results."
    )

    # Results table
    table = doc.add_table(rows=6, cols=7, style="Table Grid")
    table.autofit = True
    headers = ["Theme", "Pre (%)", "Peri (%)", "Post (%)",
               "Pre\u2192Peri z (p)", "Pre\u2192Post z (p)", "Peri\u2192Post z (p)"]
    for i, h in enumerate(headers):
        cell = table.rows[0].cells[i]
        cell.text = h
        for paragraph in cell.paragraphs:
            for run in paragraph.runs:
                run.bold = True
                run.font.size = Pt(9)
                run.font.name = "Times New Roman"

    data = [
        ["AD-ID", "5.7", "10.9", "9.8",
         "3.42 (<0.001)", "4.12 (<0.001)", "0.62 (1.000)"],
        ["Restaurant\nSupport", "3.8", "11.0", "4.2",
         "5.21 (<0.001)", "0.58 (1.000)", "4.78 (<0.001)"],
        ["Social Media\nPromotions", "8.0", "20.0", "14.5",
         "6.12 (<0.001)", "5.44 (<0.001)", "2.61 (0.027)"],
        ["Sports", "22.4", "18.6", "21.8",
         "1.52 (0.386)", "0.38 (1.000)", "1.38 (0.502)"],
        ["Gaming", "4.1", "5.2", "4.8",
         "0.88 (1.000)", "0.92 (1.000)", "0.34 (1.000)"],
    ]
    for r, row_data in enumerate(data, start=1):
        for c, val in enumerate(row_data):
            cell = table.rows[r].cells[c]
            cell.text = val
            for paragraph in cell.paragraphs:
                for run in paragraph.runs:
                    run.font.size = Pt(9)
                    run.font.name = "Times New Roman"

    doc.add_paragraph("")  # spacer

    doc.add_paragraph(
        "Three themes demonstrated statistically significant increases from the pre-pandemic "
        "to the peri-lockdown period. AD-ID prevalence rose from 5.7% to 10.9%, an increase "
        "of 91.2% (z = 3.42, p < 0.001). Restaurant Support increased from 3.8% to 11.0%, "
        "a 189.5% increase (z = 5.21, p < 0.001). Social Media Promotions rose from 8.0% to "
        "20.0%, a 150.0% increase (z = 6.12, p < 0.001). These increases were substantively "
        "large, reflecting a rapid reorientation of marketing emphasis during lockdowns."
    )
    doc.add_paragraph(
        "Critically, not all increases were transient. AD-ID prevalence remained significantly "
        "elevated in the post-lockdown period (9.8%) relative to pre-pandemic levels (z = 4.12, "
        "p < 0.001), and the peri-to-post decline was not significant (z = 0.62, p = 1.000). "
        "Social Media Promotions similarly remained elevated post-lockdown (14.5%) relative to "
        "pre-pandemic (z = 5.44, p < 0.001), though there was a significant decline from the "
        "peri-lockdown peak (z = 2.61, p = 0.027). In contrast, Restaurant Support returned to "
        "near-baseline levels in the post-lockdown period (4.2%; peri\u2192post z = 4.78, "
        "p < 0.001), suggesting this was a temporary crisis response. Sports and Gaming themes "
        "showed no significant changes across any period."
    )

    # ── Discussion ──
    doc.add_heading("Discussion", level=1)
    doc.add_paragraph(
        "This study provides the first longitudinal, quantitative analysis of alcohol marketing "
        "theme prevalence on social media across pre-pandemic, lockdown, and post-lockdown "
        "periods. The findings support the hypothesis that alcohol brands rapidly amplified "
        "specific marketing themes during COVID-19 lockdowns and, importantly, demonstrate that "
        "some of these shifts persisted beyond the acute crisis period."
    )
    doc.add_paragraph(
        "The durability of the AD-ID theme is particularly concerning from a public health "
        "perspective. Alcohol delivery and isolation drinking messaging nearly doubled during "
        "lockdowns and remained at elevated levels even after restrictions eased. This pattern "
        "suggests that the pandemic may have accelerated a structural shift in how the alcohol "
        "industry markets its products\u2014normalizing home delivery and solitary consumption as "
        "routine rather than crisis-specific behaviors. This finding aligns with and extends "
        "qualitative observations by Martino et al. (2021) and Gerritsen et al. (2021), who "
        "identified similar themes but could not assess their trajectory over time."
    )
    doc.add_paragraph(
        "The transient nature of Restaurant Support messaging is consistent with a corporate "
        "social responsibility interpretation: brands promoted restaurant partnerships during "
        "acute closures but reverted to other strategies once the immediate crisis passed. "
        "Social Media Promotions, while declining from their lockdown peak, remained "
        "significantly elevated, suggesting that brands learned the effectiveness of digital "
        "engagement strategies and continued to invest in them."
    )
    doc.add_paragraph(
        "Methodologically, this study demonstrates the utility of the TopicFlow pipeline "
        "(Thomas, 2025) for analyzing marketing content at scale. The combination of BERTopic "
        "with systematic hyperparameter optimization, LLM-based naming, and validated GPT-4o "
        "classification provides a reproducible framework that addresses key limitations of "
        "both manual content analysis and traditional topic models. The pipeline\u2019s open-source "
        "availability facilitates replication and extension to other marketing domains."
    )
    doc.add_paragraph(
        "Several limitations warrant acknowledgment. The sample included only 11 alcohol "
        "companies on a single platform (Twitter), limiting generalizability to broader industry "
        "practices or other social media environments. The observational design cannot establish "
        "a causal link between marketing exposure and alcohol consumption behaviors. "
        "Classification, while validated against human labels, relied on LLM inference and may "
        "contain systematic biases. Future research should link marketing theme exposure to "
        "behavioral outcomes using prospective designs and extend analyses to platforms such as "
        "Instagram and TikTok, where alcohol marketing is increasingly concentrated."
    )

    # ── References ──
    doc.add_heading("References", level=1)

    refs = [
        "Barry, A. E., Bates, A. M., Olusanya, O., Vinal, C. E., Martin, E., Peoples, J. E., ... & Montano, J. R. (2016). Alcohol marketing on Twitter and Instagram: Evidence of directly advertising to youth/adolescents. Alcohol and Alcoholism, 51(4), 487\u2013492.",
        "Colbert, S., Wilkinson, C., Thornton, L., & Richmond, R. (2020). COVID-19 and alcohol in Australia: Industry changes and public health impacts. Drug and Alcohol Review, 39(5), 435\u2013440.",
        "Gerritsen, S., Hasse, B., Jonsson, L., & Wall, M. (2021). Alcohol marketing during the first wave of COVID-19 in Aotearoa New Zealand and Sweden. BMC Public Health, 21, 1\u201312.",
        "Grootendorst, M. (2022). BERTopic: Neural topic modeling with a class-based TF-IDF procedure. arXiv preprint arXiv:2203.05794.",
        "Henriksen, L., Feighery, E. C., Schleicher, N. C., & Fortmann, S. P. (2010). Receptivity to alcohol marketing predicts initiation of alcohol use. Journal of Adolescent Health, 42(1), 28\u201335.",
        "Jernigan, D. H., & Ross, C. S. (2020). The alcohol marketing landscape: Alcohol industry size, structure, strategies, and public health responses. Journal of Studies on Alcohol and Drugs, Supplement 19, 13\u201325.",
        "Martino, F., Brooks, R., Browne, J., Carah, N., Zorbas, C., Corben, K., ... & Backholer, K. (2021). The nature and extent of online marketing by big food and big alcohol during the COVID-19 pandemic in Australia. BMC Public Health, 21(1), 1\u201315.",
        "Pollard, M. S., Tucker, J. S., & Green, H. D. (2020). Changes in adult alcohol use and consequences during the COVID-19 pandemic in the US. JAMA Network Open, 3(9), e2022942.",
        "Qiang, J., Qian, Z., Li, Y., Yuan, Y., & Wu, X. (2020). Short text topic modeling techniques, applications, and performance: A survey. IEEE Transactions on Knowledge and Data Engineering, 34(3), 1427\u20131445.",
        "R\u00f6der, M., Both, A., & Hinneburg, A. (2015). Exploring the space of topic coherence measures. Proceedings of the Eighth ACM International Conference on Web Search and Data Mining, 399\u2013408.",
        "Thomas, J. E. (2025). TopicFlow: A BERTopic and Large Language Model Pipeline for Topic Discovery and Classification. Preprint.",
        "White, A. M., Castle, I. J., Powell, P. A., Hingson, R. W., & Koob, G. F. (2022). Alcohol-related deaths during the COVID-19 pandemic. JAMA, 327(17), 1704\u20131706.",
        "Wiederhold, B. K. (2020). Using social media to our advantage: Alleviating anxiety during a pandemic. Cyberpsychology, Behavior, and Social Networking, 23(4), 197\u2013198.",
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
    print(f"Brief Report (Study 1) saved to: {OUTPUT_PATH}")


if __name__ == "__main__":
    build_document()
