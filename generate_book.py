#!/usr/bin/env python3
"""
Generate 'The Drinking Age: How the Alcohol Industry Shaped America'
by Jacob Edward Thomas — a popular-history book based on dissertation Part A.
"""

import os
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn


def set_run_font(run, name="Times New Roman", size=12, bold=False, italic=False, color=None):
    run.font.name = name
    run.font.size = Pt(size)
    run.bold = bold
    run.italic = italic
    if color:
        run.font.color.rgb = RGBColor(*color)
    # Ensure Times New Roman works for East-Asian fallback
    r = run._element
    rPr = r.get_or_add_rPr()
    rFonts = rPr.find(qn("w:rFonts"))
    if rFonts is None:
        rFonts = rPr.makeelement(qn("w:rFonts"), {})
        rPr.insert(0, rFonts)
    rFonts.set(qn("w:ascii"), name)
    rFonts.set(qn("w:hAnsi"), name)


def add_paragraph(doc, text, font_size=12, bold=False, italic=False,
                  alignment=WD_ALIGN_PARAGRAPH.JUSTIFY, space_after=6,
                  space_before=0, first_line_indent=None, line_spacing=1.15):
    p = doc.add_paragraph()
    p.alignment = alignment
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.space_before = Pt(space_before)
    p.paragraph_format.line_spacing = line_spacing
    if first_line_indent is not None:
        p.paragraph_format.first_line_indent = Inches(first_line_indent)
    run = p.add_run(text)
    set_run_font(run, size=font_size, bold=bold, italic=italic)
    return p


def add_chapter_title(doc, title):
    doc.add_page_break()
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(72)
    p.paragraph_format.space_after = Pt(24)
    run = p.add_run(title)
    set_run_font(run, size=16, bold=True)


def add_illustration(doc, caption):
    """Add a centered, italic illustration placeholder."""
    add_paragraph(doc, caption, font_size=11, italic=True,
                  alignment=WD_ALIGN_PARAGRAPH.CENTER, space_after=12,
                  space_before=12, first_line_indent=None)


def add_body(doc, text):
    paragraphs = text.strip().split("\n\n")
    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        if para.startswith("[Illustration") or para.startswith("[Image"):
            add_illustration(doc, para)
        else:
            add_paragraph(doc, para, first_line_indent=0.3)


def build_title_page(doc):
    # Spacer
    for _ in range(6):
        add_paragraph(doc, "", space_after=0)

    add_paragraph(doc, "THE DRINKING AGE", font_size=28, bold=True,
                  alignment=WD_ALIGN_PARAGRAPH.CENTER, space_after=4)
    add_paragraph(doc, "How the Alcohol Industry Shaped America", font_size=16,
                  italic=True, alignment=WD_ALIGN_PARAGRAPH.CENTER, space_after=36)
    add_paragraph(doc, "Jacob Edward Thomas", font_size=14,
                  alignment=WD_ALIGN_PARAGRAPH.CENTER, space_after=24)
    add_paragraph(
        doc,
        "Based on doctoral research at The University of Texas at Austin, 2025",
        font_size=11, italic=True,
        alignment=WD_ALIGN_PARAGRAPH.CENTER, space_after=0
    )


# ---------------------------------------------------------------------------
# CHAPTER CONTENT
# ---------------------------------------------------------------------------

INTRODUCTION = (
    "Every civilization that has left a record has also left evidence of drinking "
    "(Standage, 2006; Gately, 2008; Phillips, 2014). The Sumerians brewed beer before they "
    "invented the wheel. The Egyptians paid their pyramid workers in ale. The Romans planted "
    "vineyards at the farthest edges of their empire, and when those legions finally marched "
    "home, the vines stayed behind and kept growing. Alcohol is not merely old. It is one of "
    "the most resilient industries in the history of commerce \u2014 older than banking, older "
    "than organized religion, older than writing itself (Dietler, 2020)."
    "\n\n"
    "This book is about how that industry came to define so much of American life. It is a "
    "story that begins in the Neolithic period, winds through ancient temples and medieval "
    "taverns, crosses the Atlantic on slave ships loaded with rum, and arrives in the "
    "twenty-first century on a smartphone screen at two in the morning. Along the way, it "
    "touches war and politics, race and gender, science and advertising, prohibition and "
    "excess. It is a story of astonishing adaptability. Every time human beings invented a "
    "new way to communicate \u2014 from clay tablets to color printing to cable television to "
    "social media \u2014 the alcohol industry figured out how to use it, often before anyone "
    "else did (Richards, 2022)."
    "\n\n"
    "America occupies a special place in this narrative. No other country has swung so "
    "violently between drunkenness and temperance, between celebration and criminalization. "
    "The United States tried to outlaw alcohol entirely, failed spectacularly, and then spent "
    "the next century building the most sophisticated alcohol marketing apparatus the world "
    "has ever seen. Americans consume roughly fifty billion dollars\u2019 worth of alcohol each "
    "year, and the advertising that sustains that consumption has become so embedded in the "
    "culture that most people no longer notice it. Beer sponsors the Super Bowl. Wine anchors "
    "the lifestyle brand. Spirits fuel the celebrity endorsement machine. And beneath all of "
    "it runs a history that is far darker and more complex than the glossy advertisements "
    "suggest."
    "\n\n"
    "This is not a temperance tract, and it is not a celebration of drinking culture. It is "
    "an attempt to tell the story plainly \u2014 to trace how an ancient commodity became a "
    "modern juggernaut and to understand the human costs along the way. The chapters that "
    "follow move roughly chronologically, from the first fermented beverages to the digital "
    "feeds of the COVID-19 era. They draw on archaeological evidence, historical records, "
    "advertising archives, and the lived experiences of the people who made, sold, regulated, "
    "and consumed alcohol across thousands of years. Many histories of alcohol have been "
    "written, and several were invaluable in preparing this account (Standage, 2006; Gately, "
    "2008; Phillips, 2014). However, no previous work has focused specifically on the "
    "evolution of alcohol marketing practices and how these coincide with cultural norms of "
    "alcohol use in society (Lawrence, 1984)."
    "\n\n"
    "If there is a single thread that connects all of it, it is this: the alcohol industry "
    "has always understood, better than almost any other commercial enterprise, that selling "
    "a drink is really about selling a story. The stories change. The selling never stops."
)

CHAPTER_1 = (
    "Somewhere in the Yellow River valley, around seven thousand years before the common "
    "era, someone stored a mixture of rice, honey, and hawthorn fruit in a clay vessel and "
    "forgot about it. When they came back, the liquid had changed. It fizzed. It tasted "
    "strange and sweet and warm. It made them feel different. That anonymous moment \u2014 "
    "reconstructed from chemical residue found on pottery fragments in Jiahu, China \u2014 is "
    "the oldest physical evidence of intentional fermentation that archaeologists have yet "
    "discovered (McGovern et al., 2004). It is also the beginning of a nine-thousand-year "
    "commercial enterprise."
    "\n\n"
    "Alcohol emerged independently on nearly every inhabited continent (Dietler, 2020). The "
    "Sumerians had a goddess of beer, Ninkasi, and the oldest surviving recipe in human "
    "history is a hymn to her that doubles as a brewing manual. The Egyptians refined the "
    "process and distributed beer as wages to the laborers who built the great monuments at "
    "Giza. In sub-Saharan Africa, communities brewed sorghum beer for communal ceremonies. "
    "In Mesoamerica, pulque \u2014 the fermented sap of the agave plant \u2014 held sacred "
    "significance for the Aztecs, who regulated its consumption with laws that punished "
    "public drunkenness by death. In Neolithic Europe, pagan cultures consumed alcohol "
    "during elaborate ceremonies honoring the changing of seasons (Lipscomb, 2020). Many "
    "hearths within settlements near Stonehenge are filled with animal bones and broken "
    "pottery vessels associated with fermented beverages, suggesting that feasts and abundant "
    "drinking were common during the period (Albarella et al., 2011). Even the Bible suggests "
    "consuming alcohol ritualistically to harbor a peaceful death or to cope with pain and "
    "adversity (Proverbs 31:6\u20137; Carrol et al., 2008)."
    "\n\n"
    "But it was in the Mediterranean world that alcohol first became something recognizable "
    "as an industry. The ancient Greeks did not merely drink wine (Oliver et al., 2011; "
    "Robinson et al., 2015). They organized their social and intellectual lives around it. "
    "Archaeological records indicate that citizens of ancient Greece often consumed wine with "
    "meals and mixed wine with their drinking water for fortification (Garnier et al., 2016). "
    "The symposium \u2014 literally \u201cdrinking together\u201d \u2014 was the central institution "
    "of Athenian civic culture, the place where politics, philosophy, and poetry happened. "
    "Homer\u2019s Iliad is drenched in wine. Agamemnon organizes an elaborate feast, complete "
    "with libations of wine, in an attempt to gain favor from the gods and inspire his army "
    "toward victory in the Trojan War (Fagles et al., 1998). The Greek soldiers at Troy "
    "received daily rations, and the poem treats this as entirely unremarkable, which tells "
    "us that by the eighth century BCE, wine was already a logistical staple of warfare."
    "\n\n"
    "Rome took everything the Greeks had built and scaled it up. Wine was a staple in the "
    "diet of nearly all Roman citizens and a part of the ration for legionaries (Davies, "
    "1971). Vineyards followed the legions into Gaul, Iberia, and the Rhine Valley, "
    "establishing wine-growing regions that still produce today. Romans began to standardize "
    "the cultivation of grapes and formulas for wine, culminating in the first known treatise "
    "on producing alcohol: De Agri Cultura by Marcus Porcius Cato, circa 160 BCE (Cato et "
    "al., 1934). It contained detailed instructions on vine cultivation, pressing, "
    "fermentation, and storage \u2014 practical advice written for landowners who understood "
    "that wine was not just a beverage but a commodity."
    "\n\n"
    "With abundant supply driven by industrial-scale production, drinking behaviors during "
    "classical antiquity shifted from predominantly ritualistic to the everyday mundane, and "
    "sometimes problematic (Laes et al., 2013). Rome also gave us the first recorded warnings "
    "about alcohol\u2019s dangers. Seneca wrote that habitual drunkenness weakens the mind and "
    "that its consequences are felt long after the drinking has stopped (Motto et al., 1990). "
    "The irony was that Seneca himself lived in a society where wine was as common as water "
    "\u2014 more common, actually, since Roman water supplies were often unreliable."
    "\n\n"
    "What the ancient world established was a pattern that would repeat for millennia. "
    "Alcohol was simultaneously sacred and profane, celebrated and feared, regulated and "
    "indulged. It was nutrition for the poor and luxury for the rich. It was medicine, "
    "currency, social lubricant, and poison. And it was, from the very beginning, a business. "
    "Nine thousand years before the first television commercial, the alcohol industry was "
    "already doing what it does best: adapting to the world as it found it and selling "
    "whatever version of the drink that world would buy."
)

CHAPTER_2 = (
    "In the centuries after Rome\u2019s fall, Europe did not stop drinking. If anything, it "
    "drank more. The medieval period was an age of ale \u2014 thick, dark, nutritious, and "
    "ubiquitous. Clean water was scarce in most European cities, and ale became an important "
    "source of nutrition for the population at large (Dyer, 1988; Carlin et al., 1998). "
    "Drunkenness became widespread among all sections of society (Glatt, 1977). Monasteries "
    "brewed ale in enormous quantities, both for their own consumption and for sale. The "
    "Benedictine and Trappist monks became, without intending to, some of the most "
    "accomplished brewers in history."
    "\n\n"
    "The medieval period also left behind something else: the earliest recognizable forms of "
    "alcohol marketing. In 1389, King Richard II of England enacted a law stipulating that "
    "places selling alcohol must hang a sign to indicate that fact, which led to competition "
    "between establishments to have the most distinguished and attractive looking signs "
    "(Richards, 2022). Suggesting alcohol merchants declare themselves was not an idea "
    "original to Richard II; some historians suggest it was appropriated from ancient Chinese "
    "lore of villagers hoisting their wine banner when they had fresh wine to trade (Liao, "
    "1959). Nevertheless, Richard II\u2019s medieval law likely contributed to a culture of "
    "extravagant marketing competition within the alcohol industry that echoes to this day, "
    "and English pubs continue the tavern-sign tradition."
    "\n\n"
    "[Illustration 1: Southwark, a neighborhood in London near the southern end of London "
    "Bridge, historically known for drinking establishments. Image depicts a tavern \u2014 "
    "Bear Inn, 1616. Tavern sign is highlighted. From Shelley, H. C. (1909).]"
    "\n\n"
    "[Illustration 2: Present-day tavern sign of The George Inn (also in Southwark, London), "
    "one of the oldest drinking establishments in London still operating according to the "
    "National Heritage List for England (n.d.).]"
    "\n\n"
    "Across the English Channel, the Flemish were pushing further. In the late 1300s, a "
    "brewery named Den Hoorn was established in Belgium (Kelly-Holmes, 2016). Over the "
    "following centuries, the brewery changed hands, and in 1717 it was purchased by "
    "Sebastian Artois, who renamed it boasting his namesake: Stella Artois (Persyn et al., "
    "2011). Its horn logo, derived from that original fourteenth-century name, is one of the "
    "oldest continuously used commercial symbols in the world \u2014 an unbroken thread of "
    "marketing that stretches back more than seven hundred years."
    "\n\n"
    "[Illustration 3: Stella Artois (n.d.) logo sporting the golden horn.]"
    "\n\n"
    "Meanwhile, town criers could be heard all over Europe shouting local news, royal decree, "
    "and even announcements promoting deals at local alcohol establishments. So-called "
    "\u201cwine criers\u201d living in France during the rule of King Philip Augustus (1180 to "
    "1223) were permitted to shout outside of taverns and charge the owner a fee for bringing "
    "in customers (Presbrey, 1929; Richards, 2022)."
    "\n\n"
    "Then came the transformation that would reshape the industry forever. Distillation \u2014 "
    "the process of heating a fermented liquid to separate and concentrate its alcohol \u2014 "
    "had been practiced by Islamic alchemists for centuries, primarily for producing perfumes "
    "and medicines. When this knowledge migrated into Christian Europe, fifteenth-century "
    "German apothecaries appropriated these sacred centuries-old Islamic methods (Tschanz, "
    "2003; Edriss et al., 2017) into a potent product marketed as a health tonic, called "
    "Gebrant wein \u2014 burnt wine, or brandy (Gately, 2008)."
    "\n\n"
    "The breakthrough came in 1500, when German doctor Hieronymus Brunschwig published his "
    "Liber de arte distillandi de simplicibus, the first printed book devoted entirely to "
    "distillation, which achieved widespread circulation (Bruschwig et al., 1500). "
    "Gutenberg\u2019s press had been operating for only half a century, and Brunschwig was among "
    "the first to use the new technology to spread technical knowledge on an industrial "
    "scale. Reminiscent of how Cato\u2019s De Agri Cultura shifted the paradigm of wine "
    "consumption across the Roman Empire 1,660 years before, Brunschwig\u2019s book enabled "
    "the development of a global spirit industry."
    "\n\n"
    "The implications were enormous. Distilled spirits were stronger, more portable, and "
    "more durable than beer or wine. They could survive long sea voyages. They could be "
    "produced from almost any fermentable material. They were, in a word, scalable. And they "
    "arrived just in time for the age of exploration, when European ships began crossing the "
    "Atlantic. The spirits industry and the colonial enterprise grew up together, and neither "
    "was innocent."
)

CHAPTER_3 = (
    "The story of rum is the story of empire, and it is written in blood. By the seventeenth "
    "century, distilled spirits were available throughout the western world (Phillips, 2014). "
    "The emerging triangular trade routes linking Europe, Africa, and the Americas exploited "
    "the natural sugar resources of the Caribbean and served as a catalyst that furthered the "
    "proliferation of spirits worldwide (Higman, 2000). Ships carried manufactured goods "
    "from Europe to the west coast of Africa, where they were exchanged for enslaved human "
    "beings. Those men, women, and children were transported in chains across the Atlantic "
    "to Caribbean sugar plantations, where they were forced to cultivate the sugarcane that "
    "produced molasses. The molasses was shipped to New England, where it was distilled into "
    "rum. The rum was sold back to Europe and Africa, and the cycle began again (McCusker, "
    "1970)."
    "\n\n"
    "[Illustration 4: Caribbean sugarcane plantations tended to by enslaved Africans, typical "
    "of transatlantic triangular trade of the time. From Ten views in the island of Antigua "
    "in the Yale Center for British Art (n.d.).]"
    "\n\n"
    "[Illustration 5: Caribbean distillery tended to by enslaved Africans, typical of "
    "transatlantic triangular trade of the time. From Ten views in the island of Antigua "
    "in the Yale Center for British Art (n.d.).]"
    "\n\n"
    "Rum was not incidental to this system. It was the engine. The profits from rum sales "
    "financed the purchase of more enslaved people. The rum itself was used as currency on "
    "the African coast, traded directly for human lives. Every bottle of colonial rum carried "
    "within it an invisible ledger of suffering."
    "\n\n"
    "America was built, in part, on this trade. During the founding of America, many of the "
    "founding fathers had historical associations with the alcohol industry. George "
    "Washington owned a distillery at Mount Vernon tended to by enslaved distillers (Breen, "
    "2004). Washington\u2019s distillery was one of the largest of its time, was very successful, "
    "and contributed to his wealth. Washington was also known to have used alcohol as a "
    "political tool, distributing large amounts of free rum, wine, and beer during his 1758 "
    "campaign for the Virginia House of Burgesses (Chernow, 2011). Thomas Jefferson owned a "
    "vineyard at Monticello, though he was not nearly as successful in the alcohol industry "
    "as Washington (Hailman, 2006). Nevertheless, Jefferson was a well-known enthusiast and "
    "importer of European wine, leaving a legendary collection in his estate\u2019s cellar, and "
    "he left his mark leading one of the first attempts at cultivating fine wine in America "
    "(Meacham, 2012)."
    "\n\n"
    "The industrial revolution advanced the alcohol industry in numerous ways during the "
    "eighteenth and nineteenth centuries. In 1775, the oldest American distillery still in "
    "operation was founded \u2014 Buffalo Trace \u2014 producing whiskey from corn (Pacult, 2021). "
    "Corn was first domesticated by indigenous peoples in southern Mexico and is considered "
    "a sacred crop to many American Indian cultures (Huff, 2006), which suggests that "
    "American alcohol distillers appropriated corn in ways reminiscent of German distillers "
    "appropriating Islamic alchemy two hundred years earlier. Many modern American whiskey "
    "producers have roots in this era: Robert Samuels began making the whiskey that would "
    "become Maker\u2019s Mark Bourbon, and Jacob Beam came to Kentucky and sold whiskey that "
    "would later be named Jim Beam (Veach, 2013)."
    "\n\n"
    "The industrial revolution also ignited the advertising industry. The first commercial "
    "broadsides appeared in the United States in 1835, direct mail advertising was firmly "
    "established in the 1840s, newspaper advertisements took off in the 1860s after color "
    "newspapers began circulating, and the 1890s brought widespread color advertising in "
    "magazines (Richards, 2022). At every stage, the alcohol industry was on the frontier of "
    "each of these emerging media technologies."
    "\n\n"
    "[Illustration 6: Early Broadside Advertising Alcohol. From Duke University Libraries "
    "(1868).]"
    "\n\n"
    "[Illustration 7: Early Billboard Advertising Alcohol. From Duke University Libraries "
    "(1916).]"
    "\n\n"
    "[Illustration 8: Early Alcohol Direct Mail. From Duke University Libraries (1910).]"
    "\n\n"
    "[Illustration 9: Early Color Newspaper Advertising Alcohol. From Duke University "
    "Libraries (1912).]"
    "\n\n"
    "By the turn of the twentieth century, alcohol was woven into the economic, political, "
    "and social fabric of America so thoroughly that it seemed impossible to extract. Millions "
    "of jobs depended on it. Entire regional economies revolved around it. The federal "
    "government relied on excise taxes from alcohol for a significant portion of its revenue. "
    "And the industry\u2019s advertising apparatus had made drinking synonymous with celebration, "
    "masculinity, patriotism, and freedom. But a counter-movement was gathering force."
)

CHAPTER_4 = (
    "The story of alcohol in America cannot be told honestly without talking about race. "
    "The alcohol industry in the United States during the time of emancipation and Jim Crow "
    "(late nineteenth century to mid-twentieth century) was heavily racially segregated and "
    "regulated. The sale and consumption of alcohol was often prohibited or restricted for "
    "Black Americans, both legally through discriminatory laws and socially through racial "
    "discrimination in bars and other establishments (Guffey, 2012). Despite these "
    "restrictions, some Black Americans were able to establish their own successful "
    "businesses in the industry. The A. Smith Bowman Distillery, founded in 1934 shortly "
    "after Prohibition ended, was one of the few Black-owned distilleries in the United "
    "States (Sanfield, 2005). However, many Black-owned bars and nightclubs were targeted "
    "for closure by law enforcement and white supremacist groups who used nuisance laws, "
    "zoning regulations, and hostile raids to shut them down (Godsil, 2006; Trounstine, "
    "2018). Jim Crow laws, combined with the rapid growth of the alcohol industry, "
    "concentrated wealth and industry leadership into nearly exclusively white capitalists, "
    "driven by rum as a product of slavery and corn whiskey as a product of colonial "
    "genocide of indigenous people. While the Bowman Distillery stayed in the family for "
    "generations, white capitalists representing the Sazerac Company eventually forced the "
    "Bowmans out in a series of mergers and acquisitions helmed by billionaire William A. "
    "Goldring in the late twentieth century (Cunningham, 2003)."
    "\n\n"
    "The temperance movement had been building since the early nineteenth century, driven by "
    "a coalition of religious conservatives, women\u2019s rights activists, progressive reformers, "
    "and \u2014 it must be said \u2014 outright racists and nativists who associated alcohol with "
    "immigrant communities they despised (Aaron et al., 1981; Andersen, 2013). The movement "
    "was contradictory and complicated, but it was effective. And in 1920, the Eighteenth "
    "Amendment to the Constitution prohibited the manufacture, sale, and transportation of "
    "intoxicating beverages across the entire United States (National Archives, 2022)."
    "\n\n"
    "Prohibition was called \u201cthe noble experiment,\u201d and it was a catastrophe. It did not "
    "stop Americans from drinking. It simply drove the industry underground, handing control "
    "to organized crime syndicates (Mappen, 2013). Speakeasies proliferated \u2014 estimates "
    "suggest there were more than thirty thousand in New York City alone."
    "\n\n"
    "What is less often discussed is how the major alcohol companies survived Prohibition. "
    "Anheuser-Busch officially pivoted to producing \u201cnear beer,\u201d a low-alcohol beverage "
    "that complied with the law. But the company also sold malt syrup, marketed with a wink "
    "to home brewers who understood exactly what it was for (Klein, 2019). Schlitz employed "
    "the same strategy, maintaining a significant operation producing malt extract that "
    "enabled illegal production of full-proof beer (Okrent, 2010)."
    "\n\n"
    "[Illustration 10: Prohibition-era Newspaper Ad for Bevo Near Beer in The Alamance "
    "Gleaner. From the North Carolina Digital Heritage Center (1919, February 27).]"
    "\n\n"
    "[Illustration 11: Prohibition-era Broadside advertising Schlitz FAMO Near Beer. From "
    "the Smithsonian Institution (n.d.).]"
    "\n\n"
    "[Illustration 12: Prohibition-era Broadside on vehicle advertising \u2018Malt Syrup,\u2019 a "
    "necessary ingredient to illegally produce alcoholic malt beers. From Klein (2019).]"
    "\n\n"
    "Prohibition brought about several negative consequences, including an increase in crime "
    "and corruption, a rise in consumption of dangerous forms of alcohol, and a decrease in "
    "government revenue from alcohol taxes (Thornton, 2014; Drexler, 2020). The Twenty-First "
    "Amendment repealed Prohibition in December 1933 (National Archives, 2022), and the "
    "alcohol industry roared back to life. But Prohibition had changed the landscape "
    "permanently. The industry emerged leaner, more consolidated, and more sophisticated "
    "than ever. It had learned that survival depended not just on making a good product but "
    "on mastering the art of public persuasion."
)

CHAPTER_5 = (
    "The First World War sent millions of young men into a landscape of unprecedented "
    "horror \u2014 trenches filled with mud and corpses, artillery barrages that lasted for days. "
    "The psychological trauma was immense, resulting in what was then termed \u201cshell shock,\u201d "
    "now recognized as post-traumatic stress disorder (Shephard, 2001). Of the 4.7 million "
    "American soldiers who served, many returned home with profound trauma. In the teeth of "
    "that trauma, alcohol was likely a prevalent coping mechanism due to its easy availability "
    "(The National WWI Museum and Memorial, 2023). Some reports suggest military officers "
    "provided it to bolster morale or inspire a fighting spirit (Kami\u0119\u0144ski, 2019) \u2014 a "
    "practice reminiscent of Agamemnon\u2019s effort to inspire his army during the Trojan War. "
    "Throughout history, mental health issues and alcohol abuse among soldiers have been well "
    "documented (Birmes, 2003; Schumm, 2012; Andreas, 2019)."
    "\n\n"
    "[Image 13: U.S. Signal Corps photograph captioned: \u201cAmerican soldiers in a captured "
    "German trench drinking beer out of steins and smoking cigars.\u201d From the National "
    "WWI Museum and Memorial (2023).]"
    "\n\n"
    "After WWI, veterans returned to an America entering Prohibition. Advertisers were quick "
    "to capitalize on demand among veterans, often using themes related to nationalism or the "
    "war to sell their products (Pope, 1980). Anheuser-Busch launched legal marketing "
    "campaigns for near beer specifically targeting veterans, using patriotic imagery to "
    "appeal to their sense of duty and sacrifice."
    "\n\n"
    "[Illustration 14: Anheuser-Busch Advertisement for Bevo Near Beer using Patriotic "
    "Themes. From Anheuser-Busch (n.d.).]"
    "\n\n"
    "Following the repeal of Prohibition in 1933, the industry had to navigate a more "
    "regulated landscape with stricter rules on advertising (Pennock et al., 2005; Jurkiewicz "
    "et al., 2007). The Great Depression, which began in 1929, created a different kind of "
    "crisis \u2014 and a different kind of opportunity. Millions of Americans confronted "
    "unemployment, poverty, and a shattering loss of identity (Bernanke, 2009; Benmelech et "
    "al., 2019). Historians suggest that many individuals abused alcohol to cope with the "
    "hardships (Elder, 2018). The alcohol industry responded with advertising calibrated to "
    "exploit exactly this vulnerability. Beer and whiskey advertisements of the 1930s were "
    "saturated with images of rugged masculinity \u2014 cowboys, outdoorsmen, men of action "
    "(Armengol, 2014)."
    "\n\n"
    "[Illustration 15: Rodeo Lager Advertisement Depicting a Hypermasculine Cowboy. From "
    "Lehmann Printing and Lithographing Co. (1936).]"
    "\n\n"
    "[Illustration 16: Lucky Strike Bourbon Advertisement Depicting a Hypermasculine "
    "Frontier Explorer. From Lehmann Printing and Lithographing Co. (circa 1930s).]"
    "\n\n"
    "Women were targeted too, but differently. Wine advertisements presented drinking as "
    "sophisticated and refined, using references to beauty and aesthetics to appeal to women "
    "who commanded a growing share of household purchasing power (Parkin, 2007; Lavin, 1995; "
    "Golia, 2016). These gendered marketing strategies \u2014 beer and hard liquor appealing to "
    "men, wine to women \u2014 established templates that persist well into the twenty-first "
    "century (Carrotte, 2016; Auter, 2016)."
    "\n\n"
    "[Illustration 17: California Belle Port Wine Advertisement Depicting a Woman With "
    "Idealistic Beauty Standards of the Time. From Lehmann Printing and Lithographing "
    "Co. (1935).]"
    "\n\n"
    "Then came the Second World War, and the alcohol industry found its greatest opportunity "
    "since the repeal of Prohibition. The demand for alcohol increased and exceeded "
    "pre-Prohibition levels (Lender et al., 1987). More than sixty million souls were lost "
    "to direct warfare and genocide (Sturgeon, 2015). The military incorporated beer and "
    "spirits into soldiers\u2019 rations, and the brewing industry wrapped itself in the flag. "
    "Alcohol also became an important source of revenue through government-imposed taxes "
    "(Ripy, 1999). Marketing remained active throughout, relying on emotional appeals and "
    "patriotic themes to connect products with the war effort (Witkowski, 2003)."
    "\n\n"
    "[Illustration 18: Schenley Whiskey Advertisement circa 1943 promoting frugality and the "
    "priority of purchasing U.S. War Bonds. From American Century Shop (2024).]"
    "\n\n"
    "[Illustration 19: Schenley Whiskey Advertisement using patriotic themes. From American "
    "Foreign Service Association (1943).]"
    "\n\n"
    "Photographs of American soldiers drinking wine on the streets of liberated Paris after "
    "the Normandy invasion became some of the most reproduced images of the war \u2014 "
    "celebrations of freedom in which alcohol was central."
    "\n\n"
    "[Illustration 20: American Soldiers Drinking on the Paris Streets following The Battle "
    "of Normandy. From Popperfoto (1944, July 1).]"
    "\n\n"
    "[Illustration 21: American Soldiers receiving their beer ration on Sterling Island, "
    "1944. From National World War II Museum (2021).]"
    "\n\n"
    "[Illustration 22: British Navy Seaman receiving their Rum Rations circa World War II. "
    "From Central Press (1942, June 30).]"
    "\n\n"
    "It is well documented that WWII veterans suffered disproportionately high levels of "
    "alcoholism (Herrmann et al., 1996; Shephard, 2001). The postwar era delivered on the "
    "promise of celebration. Returning veterans drove a consumption boom, and per capita "
    "alcohol consumption rose steadily, a trend that extended into the 1960s and accelerated "
    "in the 1970s (Landberg, 2009). The stage was set for the medium that would change "
    "everything: television."
)

CHAPTER_6 = (
    "In the early 1950s, a new appliance took its place in American living rooms, kicking "
    "off what many historians refer to as the Golden Age of Advertising (Cracknell, 2012). "
    "Television was the most powerful advertising medium ever invented \u2014 it combined the "
    "visual impact of print with the emotional intimacy of radio and delivered both directly "
    "into the home. Companies created television commercials showcasing products in the best "
    "possible light, using catchy slogans like \u201cWhen you say Budweiser, you\u2019ve said it "
    "all\u201d to create lasting brand associations (Samuel, 2001; Richards, 2022)."
    "\n\n"
    "The spirits industry took a different approach. In 1948, the Distilled Spirits Council "
    "adopted a voluntary code keeping hard liquor advertisements off television and radio "
    "(Hacker, 1998). The code was framed as corporate responsibility, but it ceded the "
    "airwaves entirely to beer and wine brands. In a self-regulated system, the industry "
    "establishes its own guidelines with no repercussions for noncompliance. Research has "
    "shown that despite self-regulation, undesirable outcomes related to alcohol advertising "
    "\u2014 such as underage drinking \u2014 remain common (Anderson et al., 2009). The vacuum "
    "left by spirits was filled by prolific advertisements for beer (Miller, 2002)."
    "\n\n"
    "[Illustration 23: Budweiser television commercial advertisements through the late 20th "
    "century. Left: \u2018Where there\u2019s life, there\u2019s Bud\u2019 (1956). Right: \u2018Wassup\u2019 "
    "(1999). From BetterBrandsSC (2013) and Barnett (2022, June 14), respectively.]"
    "\n\n"
    "Product placement became one of the industry\u2019s most effective tools. This advertising "
    "technique has been increasingly popular since the 1970s, becoming ubiquitous after the "
    "1982 success of the film E.T. (Babin, 1996; Newell et al., 2006). The partnership "
    "between James Bond and Smirnoff vodka is perhaps the most famous example. Wilson et "
    "al. (2018) systematically analyzed six decades of James Bond films and found 109 "
    "alcohol product placement events \u2014 4.5 per film."
    "\n\n"
    "[Illustration 24: James Bond\u2019s long history of Smirnoff product placement. Left: Dr. "
    "No (1962). Right: No Time to Die (2021). From Young (1962) and Fukunaga (2021), "
    "respectively.]"
    "\n\n"
    "Sponsorship operated on the same principle. When Miller Lite signed a sponsorship deal "
    "with the Dallas Cowboys in 1991, it bought an association linking its brand to the "
    "emotional intensity of professional football (Fischer, 2021; Meenaghan, 2021; Crompton, "
    "1993). Research has demonstrated that alcohol sports sponsorship is associated with "
    "increased levels of drinking amongst youth and hazardous drinking among adults (Brown, "
    "2016)."
    "\n\n"
    "[Illustration 25: Advertisement depicting the Cowboys Lite House, sponsored by Miller "
    "Lite. From Dallas Cowboys (n.d.).]"
    "\n\n"
    "Celebrity endorsement pushed the strategy further still. When Sean \u201cDiddy\u201d Combs "
    "partnered with Ciroc vodka in the mid-2000s, it accelerated vodka consumption among "
    "young Black Americans, a demographic previously hard to reach by vodka brands (Siegel "
    "et al., 2012; Bergkvist et al., 2016; Atkin et al., 1983). When George Clooney "
    "co-founded Casamigos tequila, the brand\u2019s identity was essentially indistinguishable "
    "from Clooney\u2019s own (Kellershohn, 2022). The sale of Casamigos to Diageo for one "
    "billion dollars demonstrated just how valuable that fusion of celebrity and brand "
    "could be."
    "\n\n"
    "[Illustration 26: Advertisement for Casamigos Tequila featuring celebrity endorser "
    "George Clooney. From Domenic (n.d.).]"
    "\n\n"
    "Research has shown that product placement, sponsorship, and celebrity endorsement are "
    "effective in promoting brand awareness and increasing alcohol use, particularly among "
    "youth and young adults (Jernigan et al., 2008; Bragg et al., 2018; Sargnet et al., "
    "2020). By the end of the twentieth century, alcohol had achieved a kind of cultural "
    "saturation. It was not merely advertised. It was ambient. And then the internet arrived."
)

CHAPTER_7 = (
    "In the mid-1990s, the emergence of the internet started to garner widespread public "
    "attention (Dutton, 2013), and the alcohol industry was quick to identify its potential. "
    "Some of the earliest forms of digital advertising were static banner ads on websites, "
    "similar to a digital billboard (Manchanda et al., 2006). Brands like Budweiser were "
    "among the pioneers, purchasing banner space on popular platforms (Davik, 2000)."
    "\n\n"
    "Major alcohol brands started creating their own dedicated websites. Jack Daniel\u2019s "
    "launched its website in the mid-1990s, filled with information about its whiskey-making "
    "process, cocktail recipes, and historical tidbits (McCune, 1998; Gordon, 2010). "
    "Programmatic advertising emerged as a means to target potential consumers more "
    "specifically, with dynamic, interactive content linking directly to product homepages "
    "(Hammersley, 2003). Email campaigns further personalized brands\u2019 connections with "
    "consumers, allowing brands to leverage specific information to tailor messages "
    "(Hastings, 2009; Kingsnorth, 2022)."
    "\n\n"
    "[Illustration 27: Early (top, circa 1997) and modern (bottom, circa 2023) stills of "
    "Jack Daniel\u2019s website. From Jack Daniels (1997) and Jack Daniel\u2019s (2023), "
    "respectively.]"
    "\n\n"
    "Social media changed everything again. Platforms like Facebook, Instagram, and Twitter "
    "offered something no previous advertising medium could match: the ability to make "
    "commercial messages look like personal communication. Since the late 2000s, the alcohol "
    "industry has been effectively using social media marketing (Hastings, 2009; Lobstein et "
    "al., 2016; Noel et al., 2020; Dwivedi et al., 2015; Jamil et al., 2022). Smirnoff\u2019s "
    "Facebook strategy was designed with explicit intent to make branded content "
    "indistinguishable from posts by friends and family. Internal documents revealed that "
    "Smirnoff insiders were aware that nearly 75% of their Facebook followers were under "
    "the legal drinking age (Hastings, 2009)."
    "\n\n"
    "[Illustration 28: Facebook post from Smirnoff Vodka, circa 2023. The post shows the "
    "insidious nature of SMM, with content appearing like user-generated content \u2014 "
    "selfies, hashtags, emojis, likes, comments, and shares \u2014 virtually indistinguishable "
    "in form. From Smirnoff US (2023).]"
    "\n\n"
    "Research has shown that social media marketing of alcohol is associated with initiating, "
    "using, and abusing alcohol, especially among youth and young adults (Moreno et al., "
    "2014; Jernigan et al., 2017; Curtis et al., 2018; Hendriks et al., 2021; Alhabash et "
    "al., 2022). The blurring of commercial and user-generated content created a new kind "
    "of advertising environment. When a college student posted a photo holding a bottle of "
    "craft beer, was that advertising? When an influencer mentioned a tequila brand, was "
    "that a paid endorsement or a personal recommendation? The lines dissolved, and the "
    "dissolution was profitable."
    "\n\n"
    "By the time the COVID-19 pandemic arrived in early 2020, the infrastructure was already "
    "in place. Americans were confined to their homes, anxious, isolated, and spending more "
    "time on social media than ever before (Auxier et al., 2021; Bendau et al., 2021; Nabi "
    "et al., 2022; Price et al., 2022). The ancient industry had adapted once again, and the "
    "consequences were only beginning to be understood."
)

CHAPTER_8 = (
    "Nine thousand years of history leaves certain patterns visible if you know where to "
    "look. Three, in particular, stand out from the long story told in the preceding chapters."
    "\n\n"
    "The first is this: the alcohol industry\u2019s success has always been tied to advances in "
    "communication technology. This is not a coincidence. It is a strategy. From the "
    "hand-written documents like De Agri Cultura (Cato et al., 1934) to the pub signs of "
    "medieval England (Richards, 2022), from Brunschwig\u2019s printed manual (Bruschwig et al., "
    "1500; Gately, 2008) to the color newspaper advertisements of the nineteenth century, "
    "from television (Miller, 2002; Cracknell, 2012; Samuel, 2001) to the social media "
    "platforms of the twenty-first century (Dutton, 2013; Kingsnorth, 2022), the industry "
    "has consistently been among the earliest and most aggressive adopters of every new "
    "medium. The pattern is so consistent that it amounts to a defining characteristic of "
    "the industry itself."
    "\n\n"
    "[Illustration 29: Adapted Conceptual Model for the Differential Susceptibility to "
    "Media Effects Model (DSMM).]"
    "\n\n"
    "The second pattern is darker. The alcohol industry has a long and documented history of "
    "exploiting vulnerable populations. The triangular trade that built the colonial rum "
    "industry was powered by enslaved labor (McCusker, 1970; Higman, 2000). The Jim Crow "
    "era concentrated alcohol wealth in the hands of white capitalists while systematically "
    "excluding Black entrepreneurs (Godsil, 2006; Trounstine, 2018). Depression-era "
    "advertising targeted economically devastated men and isolated women with messaging "
    "designed to exploit their psychological vulnerabilities (Armengol, 2014; Parkin, 2007; "
    "Lefebvre et al., 2020). And the social media strategies of the twenty-first century "
    "have proven structurally incapable of preventing exposure of minors to alcohol marketing "
    "(Hastings, 2009; Auxier et al., 2021)."
    "\n\n"
    "The third pattern concerns the lasting power of media portrayals. When James Bond "
    "ordered a vodka martini in 1962, he created an association between sophistication and "
    "Smirnoff that endured for more than six decades (Wilson et al., 2018). When wartime "
    "photographs showed soldiers drinking in liberated Paris, they created an equation "
    "between alcohol and freedom that shaped American culture for generations. Gender norms "
    "around alcohol \u2014 men with beer and hard liquor, women with wine \u2014 have been "
    "reinforced through decades of targeted marketing (Parkin, 2007; Armengol, 2014; Golia, "
    "2016; Carrotte, 2016; Auter, 2016; Lefebvre et al., 2020). These portrayals do not "
    "merely sell a product. They construct a world (Kellershohn, 2022)."
    "\n\n"
    "[Illustration 30: Conceptual Model for Cross-lagged Panel Analyses in Study 2.]"
    "\n\n"
    "The COVID-19 pandemic brought all three patterns into convergence. A communications "
    "technology \u2014 social media \u2014 reached people in their most vulnerable moments, "
    "confined to their homes, frightened, and cut off from normal social support "
    "(Pfefferbaum et al., 2020; Panchal et al., 2023). The industry\u2019s digital marketing "
    "apparatus delivered alcohol advertising directly to those people with unprecedented "
    "precision. The pandemic led to documented increases in stress, isolation, alcohol "
    "consumption, and related mortality (Grossman et al., 2020; Koob et al., 2020; Pollard "
    "et al., 2020; Foster et al., 2021; White et al., 2022). And the accumulated weight of "
    "decades of media portrayal \u2014 alcohol as comfort, as reward, as escape \u2014 primed "
    "millions of Americans to respond in exactly the way the advertising intended. Media "
    "portrayals from the alcohol industry during this period included the new availability "
    "of delivery alcohol and the promotion of virtual happy hours (Atkinson et al., 2021; "
    "Martino et al., 2021; Gerritsen et al., 2021; Pakdaman et al., 2021)."
    "\n\n"
    "The drinking age is not a number on a card. It is the age we live in \u2014 an era in "
    "which the ancient industry of alcohol has achieved a level of commercial sophistication "
    "and cultural penetration that its founders could never have imagined. Understanding how "
    "we arrived here is the first step toward deciding where we go next. That decision "
    "belongs to all of us. But it must be made with open eyes."
)

AFTERWORD = (
    "I began this research as a doctoral student at the University of Texas at Austin, "
    "surrounded by the artifacts of a drinking culture so pervasive that it had become "
    "invisible. Austin is a city that loves its bars, its live music venues, its craft "
    "breweries, and its weekend brunches with bottomless mimosas. I participated in that "
    "culture, as most people do, without thinking very much about where it came from or who "
    "benefits from it."
    "\n\n"
    "Writing this history changed that. Not because the facts were surprising \u2014 most of "
    "them are hiding in plain sight \u2014 but because seeing them assembled in sequence reveals "
    "a pattern that is difficult to unsee. The alcohol industry is not simply a business "
    "that makes a product people enjoy. It is one of the most adaptive, strategically "
    "sophisticated, and historically consequential commercial enterprises in human "
    "civilization. It has survived prohibition, regulation, and social movements that would "
    "have destroyed lesser industries. It has shaped the media landscape, the political "
    "process, and the cultural imagination of entire nations."
    "\n\n"
    "I do not presume to tell anyone whether or how much to drink. That is a personal "
    "decision, and I respect it. But I do believe that decisions made in ignorance are not "
    "truly free. My hope is that this book has provided some of the context that makes "
    "genuine choice possible. The industry will keep adapting. The question is whether the "
    "rest of us will keep paying attention."
)

# ---------------------------------------------------------------------------
# BUILD DOCUMENT
# ---------------------------------------------------------------------------

def main():
    doc = Document()

    # Set default font for the document
    style = doc.styles["Normal"]
    font = style.font
    font.name = "Times New Roman"
    font.size = Pt(12)
    style.paragraph_format.line_spacing = 1.15

    # Also set the rFonts element for compatibility
    rPr = style.element.get_or_add_rPr()
    rFonts = rPr.find(qn("w:rFonts"))
    if rFonts is None:
        rFonts = rPr.makeelement(qn("w:rFonts"), {})
        rPr.insert(0, rFonts)
    rFonts.set(qn("w:ascii"), "Times New Roman")
    rFonts.set(qn("w:hAnsi"), "Times New Roman")

    # Set narrow margins
    for section in doc.sections:
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1.2)
        section.right_margin = Inches(1.2)

    # ---- TITLE PAGE ----
    build_title_page(doc)

    # ---- INTRODUCTION ----
    add_chapter_title(doc, "INTRODUCTION")
    add_body(doc, INTRODUCTION)

    # ---- CHAPTER 1 ----
    add_chapter_title(doc, "CHAPTER 1\nThe Ancient Glass")
    add_body(doc, CHAPTER_1)

    # ---- CHAPTER 2 ----
    add_chapter_title(doc, "CHAPTER 2\nSigns and Spirits")
    add_body(doc, CHAPTER_2)

    # ---- CHAPTER 3 ----
    add_chapter_title(doc, "CHAPTER 3\nBlood, Sugar, and Rum")
    add_body(doc, CHAPTER_3)

    # ---- CHAPTER 4 ----
    add_chapter_title(doc, "CHAPTER 4\nRace, Temperance, and the Noble Experiment")
    add_body(doc, CHAPTER_4)

    # ---- CHAPTER 5 ----
    add_chapter_title(doc, "CHAPTER 5\nA Soldier\u2019s Drink")
    add_body(doc, CHAPTER_5)

    # ---- CHAPTER 6 ----
    add_chapter_title(doc, "CHAPTER 6\nThe Golden Age and the Screen")
    add_body(doc, CHAPTER_6)

    # ---- CHAPTER 7 ----
    add_chapter_title(doc, "CHAPTER 7\nThe Feed")
    add_body(doc, CHAPTER_7)

    # ---- CHAPTER 8 ----
    add_chapter_title(doc, "CHAPTER 8\nThree Key Points")
    add_body(doc, CHAPTER_8)

    # ---- AFTERWORD ----
    add_chapter_title(doc, "AFTERWORD")
    add_body(doc, AFTERWORD)

    # ---- SAVE ----
    output_dir = os.path.join(os.path.dirname(__file__), "deliverables")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "the_drinking_age.docx")
    doc.save(output_path)
    print(f"Book saved to: {output_path}")

    # Word count
    total = 0
    for var in [INTRODUCTION, CHAPTER_1, CHAPTER_2, CHAPTER_3, CHAPTER_4,
                CHAPTER_5, CHAPTER_6, CHAPTER_7, CHAPTER_8, AFTERWORD]:
        total += len(var.split())
    print(f"Total word count: {total}")


if __name__ == "__main__":
    main()
