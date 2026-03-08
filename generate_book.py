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


def add_body(doc, text):
    paragraphs = text.strip().split("\n\n")
    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
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

INTRODUCTION = """
Every civilization that has left a record has also left evidence of drinking. The Sumerians brewed beer before they invented the wheel. The Egyptians paid their pyramid workers in ale. The Romans planted vineyards at the farthest edges of their empire, and when those legions finally marched home, the vines stayed behind and kept growing. Alcohol is not merely old. It is one of the most resilient industries in the history of commerce — older than banking, older than organized religion, older than writing itself.

This book is about how that industry came to define so much of American life. It is a story that begins in the Neolithic period, winds through ancient temples and medieval taverns, crosses the Atlantic on slave ships loaded with rum, and arrives in the twenty-first century on a smartphone screen at two in the morning. Along the way, it touches war and politics, race and gender, science and advertising, prohibition and excess. It is a story of astonishing adaptability. Every time human beings invented a new way to communicate — from clay tablets to color printing to cable television to social media — the alcohol industry figured out how to use it, often before anyone else did.

America occupies a special place in this narrative. No other country has swung so violently between drunkenness and temperance, between celebration and criminalization. The United States tried to outlaw alcohol entirely, failed spectacularly, and then spent the next century building the most sophisticated alcohol marketing apparatus the world has ever seen. Americans consume roughly fifty billion dollars' worth of alcohol each year, and the advertising that sustains that consumption has become so embedded in the culture that most people no longer notice it. Beer sponsors the Super Bowl. Wine anchors the lifestyle brand. Spirits fuel the celebrity endorsement machine. And beneath all of it runs a history that is far darker and more complex than the glossy advertisements suggest.

This is not a temperance tract, and it is not a celebration of drinking culture. It is an attempt to tell the story plainly — to trace how an ancient commodity became a modern juggernaut and to understand the human costs along the way. The chapters that follow move roughly chronologically, from the first fermented beverages to the digital feeds of the COVID-19 era. They draw on archaeological evidence, historical records, advertising archives, and the lived experiences of the people who made, sold, regulated, and consumed alcohol across thousands of years.

If there is a single thread that connects all of it, it is this: the alcohol industry has always understood, better than almost any other commercial enterprise, that selling a drink is really about selling a story. The stories change. The selling never stops.
"""

CHAPTER_1 = """
Somewhere in the Yellow River valley, around seven thousand years before the common era, someone stored a mixture of rice, honey, and hawthorn fruit in a clay vessel and forgot about it. When they came back, the liquid had changed. It fizzed. It tasted strange and sweet and warm. It made them feel different. That anonymous moment — reconstructed from chemical residue found on pottery fragments in Jiahu, China — is the oldest physical evidence of intentional fermentation that archaeologists have yet discovered. It is also the beginning of a nine-thousand-year commercial enterprise.

Alcohol emerged independently on nearly every inhabited continent. The Sumerians had a goddess of beer, Ninkasi, and the oldest surviving recipe in human history is a hymn to her that doubles as a brewing manual. The Egyptians refined the process and distributed beer as wages to the laborers who built the great monuments at Giza. In sub-Saharan Africa, communities brewed sorghum beer for communal ceremonies. In Mesoamerica, pulque — the fermented sap of the agave plant — held sacred significance for the Aztecs, who regulated its consumption with laws that punished public drunkenness with death.

But it was in the Mediterranean world that alcohol first became something recognizable as an industry. The ancient Greeks did not merely drink wine. They organized their social and intellectual lives around it. The symposium — literally "drinking together" — was the central institution of Athenian civic culture, the place where politics, philosophy, and poetry happened. Homer's Iliad is drenched in wine. Achilles drinks it. Agamemnon pours it as a libation to the gods. The Greek soldiers at Troy received daily rations, and the poem treats this as entirely unremarkable, which tells us that by the eighth century BCE, wine was already a logistical staple of warfare. The Greeks also planted vineyards across their colonial territories, from Sicily to the Black Sea coast, creating the first international wine trade.

Rome took everything the Greeks had built and scaled it up. The Roman legions received a daily wine ration of roughly a liter per soldier — an allocation that shaped agricultural policy across the empire. Vineyards followed the legions into Gaul, Iberia, and the Rhine Valley, establishing wine-growing regions that still produce today. Cato the Elder, writing in the second century BCE, produced what is arguably the first technical manual for commercial alcohol production. His De Agri Cultura contains detailed instructions on vine cultivation, pressing, fermentation, and storage — practical advice written for landowners who understood that wine was not just a beverage but a commodity.

Rome also gave us the first recorded warnings about alcohol's dangers. Seneca, writing in the first century CE, described the shame of habitual drunkenness in terms that would not sound out of place in a modern public health pamphlet. He wrote of men who could not remember the night before, who humiliated themselves in public, who destroyed their bodies in pursuit of a pleasure that consumed them. The irony was that Seneca himself lived in a society where wine was as common as water — more common, actually, since Roman water supplies were often unreliable.

What the ancient world established was a pattern that would repeat for millennia. Alcohol was simultaneously sacred and profane, celebrated and feared, regulated and indulged. It was nutrition for the poor and luxury for the rich. It was medicine, currency, social lubricant, and poison. And it was, from the very beginning, a business. The merchants of Pompeii advertised their wines on painted signs. The tavern keepers of Rome competed for customers. The vineyard owners of Gaul optimized their yields. Nine thousand years before the first television commercial, the alcohol industry was already doing what it does best: adapting to the world as it found it and selling whatever version of the drink that world would buy.
"""

CHAPTER_2 = """
In the centuries after Rome's fall, Europe did not stop drinking. If anything, it drank more. The medieval period was an age of ale — thick, dark, nutritious, and ubiquitous. Clean water was scarce in most European cities, and fermented beverages were genuinely safer to consume. Ale was breakfast. Ale was lunch. Ale was the caloric foundation of the peasant diet, and monasteries brewed it in enormous quantities, both for their own consumption and for sale. The Benedictine and Trappist monks became, without intending to, some of the most accomplished brewers in history. Their innovations — including the systematic use of hops for preservation and flavor — shaped the beer industry for centuries.

Drunkenness was endemic. The medieval period left behind a rich literature of complaint about public intoxication, from church sermons to court records to satirical poems. But it also left behind something else: the earliest recognizable forms of alcohol marketing. In 1389, King Richard II of England issued a decree requiring every tavern and alehouse to display a sign identifying itself. The law was practical — the king's inspectors needed to find the establishments they were supposed to regulate — but it created something unprecedented. For the first time, drinking establishments had to brand themselves, to create a visual identity that would attract customers from the street. The painted tavern sign, swinging on its iron bracket above the cobblestones, was one of the first advertising media in European commercial history.

Across the English Channel, the Flemish were pushing further. In the early 1300s, a brewery called Den Hoorn began operating in the city of Leuven, in what is now Belgium. Over the following centuries, the brewery changed hands, expanded, and eventually became the brand known today as Stella Artois. Its horn logo, derived from that original fourteenth-century name, is one of the oldest continuously used commercial symbols in the world — an unbroken thread of marketing that stretches back more than seven hundred years. Meanwhile, in France, the criers of the wine merchants walked the streets of Paris announcing their wares, an early form of audio advertising that preceded radio by half a millennium.

Then came the transformation that would reshape the industry forever. Distillation — the process of heating a fermented liquid to separate and concentrate its alcohol — had been practiced by Islamic alchemists for centuries, primarily for producing perfumes and medicines. When this knowledge migrated into Christian Europe, probably through the medical schools of Salerno and Montpellier, it landed in the hands of German apothecaries who saw different possibilities entirely. They began producing aqua vitae — "water of life" — and selling it as a medicinal tonic.

The breakthrough came in 1500, when a Strasbourg physician named Hieronymus Brunschwig published his Liber de arte distillandi, the first printed book devoted entirely to distillation. Gutenberg's press had been operating for only half a century, and Brunschwig was among the first to use the new technology to spread technical knowledge on an industrial scale. His book traveled across Europe and eventually across oceans. It was translated, copied, adapted, and improved upon. Within a generation, distillation was no longer the province of monks and apothecaries. It was an industry.

The implications were enormous. Distilled spirits were stronger, more portable, and more durable than beer or wine. They could survive long sea voyages. They could be produced from almost any fermentable material — grain, fruit, sugarcane, potatoes. They were, in a word, scalable. And they arrived just in time for the age of exploration, when European ships began crossing the Atlantic and opening trade routes that would connect — and devastate — entire continents. The spirits industry and the colonial enterprise grew up together, and neither was innocent.

The Renaissance gave the alcohol industry two things it had never had before: the technology to make stronger drinks and the communications infrastructure to sell them at scale. Brunschwig's book was, in a sense, the first viral marketing campaign for spirits. It turned a monastic secret into public knowledge and launched a commercial revolution that would shape the next five centuries of drinking culture. The marriage of alcohol and mass communication had begun.
"""

CHAPTER_3 = """
The story of rum is the story of empire, and it is written in blood. In the seventeenth and eighteenth centuries, a triangular trade route connected three continents in a cycle of extraordinary cruelty and extraordinary profit. Ships carried manufactured goods from Europe to the west coast of Africa, where they were exchanged for enslaved human beings. Those men, women, and children were transported in chains across the Atlantic to Caribbean sugar plantations, where they were forced to cultivate the sugarcane that produced molasses. The molasses was shipped to New England, where it was distilled into rum. The rum was sold back to Europe and Africa, and the cycle began again.

Rum was not incidental to this system. It was the engine. The profits from rum sales financed the purchase of more enslaved people. The rum itself was used as currency on the African coast, traded directly for human lives. And the sugar plantations that produced the raw materials were among the most lethal workplaces in human history — an enslaved person working a Caribbean sugar field had a life expectancy that made the mines of Potosi look merciful. Every bottle of colonial rum carried within it an invisible ledger of suffering.

America was built, in part, on this trade. The colonies' first significant manufacturing industry was rum distillation. By the mid-eighteenth century, New England had more than a hundred and fifty distilleries, and rum was the most widely consumed spirit in the colonies. It was also deeply entangled with the political life of the new nation. George Washington — the father of the country, the man on the dollar bill — operated one of the largest whiskey distilleries in America at his Mount Vernon estate. The distillery was run, day to day, by enslaved workers, including a man whose skill as a distiller was renowned but whose name was recorded only as property on a ledger. Washington also understood alcohol's political utility. During his 1758 campaign for the Virginia House of Burgesses, he distributed roughly a half-gallon of alcohol for every vote he received, a practice so common it had its own name: "swilling the planters with bumbo."

Thomas Jefferson, meanwhile, dreamed of a more refined American drinking culture. He planted vineyards at Monticello and imported French wines, hoping to wean the young republic off its appetite for hard spirits. He failed. Americans wanted whiskey, and the new nation's westward expansion created the conditions for a bourbon industry that would become one of the country's most enduring cultural exports. Buffalo Trace, established in 1775 on the banks of the Kentucky River, claims to be the oldest continuously operating distillery in America. Maker's Mark and Jim Beam followed in subsequent decades, building family dynasties that marketed tradition and craftsmanship even as they industrialized their production.

The nineteenth century brought the industrial revolution to alcohol and the advertising revolution alongside it. The timeline is striking. Commercial broadsides — single-sheet printed advertisements — became widespread in the 1830s, and alcohol brands were among the first to use them. Direct mail advertising emerged in the 1840s, and breweries and distilleries were early adopters. Color printing transformed newspaper advertising in the 1860s, and alcohol advertisements were among the most visually sophisticated of the era. The magazine advertising boom of the 1890s was fueled in significant part by spirits and beer brands willing to pay premium rates for full-page illustrations.

At every stage, the alcohol industry was not just participating in the communications revolution — it was driving it. The money that flowed from alcohol sales into advertising helped finance the growth of the American media industry itself. Newspapers, magazines, and eventually radio stations depended on alcohol advertising revenue. This created a dependency that would complicate every subsequent attempt to regulate the industry. When you fund the messenger, the messenger is reluctant to deliver bad news about your product.

By the turn of the twentieth century, alcohol was woven into the economic, political, and social fabric of America so thoroughly that it seemed impossible to extract. Millions of jobs depended on it. Entire regional economies revolved around it. The federal government relied on excise taxes from alcohol for a significant portion of its revenue. And the industry's advertising apparatus had made drinking synonymous with celebration, masculinity, patriotism, and freedom. But a counter-movement was gathering force — one that would attempt the most radical social experiment in American history.
"""

CHAPTER_4 = """
The story of alcohol in America cannot be told honestly without talking about race. From the colonial period onward, the industry was shaped by racial hierarchies that determined who profited, who labored, and who was excluded. After the Civil War and the collapse of Reconstruction, the Jim Crow era imposed a regime of racial segregation that extended into every corner of American commercial life, including the production and sale of alcohol.

Black Americans had been making alcohol since the colonial period — the enslaved distillers at Mount Vernon were only the most famous examples. After emancipation, some Black entrepreneurs managed to establish their own distilleries and breweries despite extraordinary obstacles. The A. Smith Bowman Distillery, founded by a Black family, produced respected whiskey for decades. But the economics of the Jim Crow era were designed to funnel wealth upward to white-owned enterprises, and over time, the pressures of segregation, discriminatory lending, and hostile regulation made it nearly impossible for Black-owned alcohol businesses to survive. The Bowman distillery eventually passed into the hands of Sazerac, controlled by the Goldring family, in a pattern of consolidation that repeated across the industry. The vast wealth generated by American alcohol — built originally on the labor of enslaved people — concentrated overwhelmingly in the hands of white capitalists whose fortunes could be traced back through colonialism, slavery, and dispossession.

While this economic consolidation was happening, a different kind of movement was gathering strength. The temperance movement had been building since the early nineteenth century, driven by a coalition of religious conservatives, women's rights activists, progressive reformers, and — it must be said — outright racists and nativists who associated alcohol with immigrant communities they despised. The movement was contradictory and complicated, but it was effective. State by state, county by county, temperance advocates pushed for restrictions on alcohol sales. And in 1920, they achieved something that would have seemed unthinkable a generation earlier: the Eighteenth Amendment to the Constitution, which prohibited the manufacture, sale, and transportation of intoxicating beverages across the entire United States.

Prohibition was called "the noble experiment," and it was a catastrophe. It did not stop Americans from drinking. It simply drove the industry underground, handing control to organized crime syndicates that made fortunes smuggling, distilling, and distributing illegal alcohol. Speakeasies proliferated — estimates suggest there were more than thirty thousand in New York City alone, roughly double the number of legal bars that had existed before the ban.

What is less often discussed is how the major alcohol companies survived Prohibition — and in some cases, quietly thrived. Anheuser-Busch, the St. Louis brewing giant, officially pivoted to producing "near beer," a low-alcohol beverage that complied with the law. But the company also sold malt syrup, marketed with a wink to home brewers who understood exactly what it was for. The syrup came with instructions that carefully explained what one must never do with it — instructions that, read in reverse, constituted a perfectly serviceable recipe for bootleg beer. Schlitz employed the same strategy. These companies maintained their brand recognition, their distribution networks, and their customer relationships throughout the thirteen years of Prohibition, positioning themselves for immediate dominance when the ban was lifted.

The Twenty-First Amendment repealed Prohibition in December 1933, and the alcohol industry roared back to life. But Prohibition had changed the landscape permanently. The patchwork of state and local regulations it left behind created the three-tier distribution system — manufacturer, distributor, retailer — that still governs American alcohol sales today. It had also demonstrated something important: the alcohol industry was not just resilient. It was, in a certain sense, unkillable. Even a constitutional amendment backed by decades of organized activism could not break it. The industry emerged from Prohibition leaner, more consolidated, and more sophisticated than ever. It had learned that survival depended not just on making a good product but on mastering the art of public persuasion. The advertising age was about to begin in earnest.
"""

CHAPTER_5 = """
The First World War sent millions of young men into a landscape of unprecedented horror — trenches filled with mud and corpses, artillery barrages that lasted for days, gas attacks that left survivors blinded and choking. The psychological toll was immense, and alcohol was one of the few comforts available. British officers routinely issued rum rations before sending men over the top. French soldiers received their pinard, a rough red wine that was as much a part of the daily kit as ammunition. The practice echoed something very old — Agamemnon, in Homer's telling, had done much the same for his warriors on the plains of Troy three thousand years earlier. War and alcohol had always been companions, and the industrial carnage of the Western Front only deepened the bond.

The American soldiers who came home from the war returned to a country that was, improbably, about to ban the very substance that had helped them survive. Prohibition took effect in 1920, and the veterans who had drunk their way through Belleau Wood and the Meuse-Argonne found themselves forbidden from buying a legal beer. The irony was not lost on them, and the brewing industry exploited it ruthlessly. Anheuser-Busch marketed its near-beer products with patriotic imagery that deliberately targeted veterans, wrapping a legal product in the emotional language of wartime sacrifice and masculine duty.

The Great Depression, which began in 1929, created a different kind of crisis — and a different kind of opportunity for the alcohol industry. Prohibition was repealed in 1933, just as millions of Americans were confronting unemployment, poverty, and a shattering loss of identity. For men who had been raised to define themselves by their ability to provide for their families, the Depression was an existential catastrophe. The alcohol industry responded with advertising that was calibrated to exploit exactly this vulnerability. Beer and whiskey advertisements of the 1930s were saturated with images of rugged masculinity — cowboys, outdoorsmen, men of action and strength. The message was not subtle: whatever the economy had taken from you, a drink could give it back. You could not control the stock market or the dust storms, but you could still be the kind of man who ordered a straight whiskey.

Women were targeted too, but differently. Wine advertisements of the era presented drinking as sophisticated, domestic, and refined — a complement to the homemaker's role rather than a challenge to it. These gendered marketing strategies, born in the Depression era, established templates that the industry would use for the rest of the century and beyond.

Then came the Second World War, and the alcohol industry found its greatest opportunity since the repeal of Prohibition. Demand for alcohol during the war exceeded pre-Prohibition levels for the first time. The military incorporated beer and spirits into soldiers' rations and recreation, and the brewing industry wrapped itself in the flag with an enthusiasm that bordered on parody. Advertisements showed soldiers and sailors hoisting beers in celebration, equating the consumption of alcohol with patriotic duty. Beer companies shipped millions of cans overseas, and the distinctive olive-drab beer can became one of the iconic images of the American war effort.

The images that came back from the front reinforced the message. Photographs of American soldiers drinking wine on the streets of liberated Paris after the Normandy invasion became some of the most reproduced images of the war — celebrations of freedom in which alcohol was not incidental but central. The message was clear: America had saved the world, and America deserved a drink.

The postwar era delivered on that promise. Returning veterans, flush with GI Bill benefits and eager to build the suburban lives they had fought for, drove a consumption boom that transformed the alcohol industry. Per capita alcohol consumption rose steadily through the late 1940s and 1950s, and the industry's advertising budgets grew to match. The stage was set for the medium that would change everything: television.
"""

CHAPTER_6 = """
In the early 1950s, a new appliance took its place in American living rooms, and the alcohol industry immediately understood what it meant. Television was the most powerful advertising medium ever invented — it combined the visual impact of print with the emotional intimacy of radio and delivered both directly into the home. Beer companies were among the first major advertisers on the new medium. Budweiser's slogan — "When you say Budweiser, you've said it all" — became one of the most recognized phrases in American culture, repeated so often that it functioned less as advertising than as folklore.

The spirits industry took a different approach, at least on the surface. In 1948, the Distilled Spirits Council of the United States adopted a voluntary code that kept hard liquor advertisements off television and radio. The code was framed as an act of corporate responsibility, but its practical effect was to cede the airwaves entirely to beer and wine brands, which filled the vacuum with a deluge of advertising that made drinking seem as natural and American as baseball. The spirits industry compensated through print advertising, billboards, and — increasingly — through less visible channels that would prove far more influential in the long run.

Product placement became one of the industry's most effective tools. The partnership between James Bond and Smirnoff vodka is perhaps the most famous example. Beginning with the earliest Bond films in the 1960s, the fictional spy's preference for a vodka martini — "shaken, not stirred" — functioned as an advertisement that audiences paid to watch. Over six decades and twenty-five films, the Bond franchise featured more than a hundred alcohol product placements, a staggering integration of commercial messaging into popular entertainment. The genius of product placement was that it did not feel like advertising. It felt like storytelling. When Bond ordered a drink, audiences did not experience it as a sales pitch. They experienced it as a character detail — and they filed it away accordingly.

Sponsorship operated on the same principle. When Miller Lite signed a sponsorship deal with the Dallas Cowboys in 1991, it was not just buying advertising space. It was buying an association — linking its brand to the emotional intensity of professional football, to loyalty, tribalism, and regional identity. Sports sponsorship allowed alcohol brands to embed themselves in the rituals and rhythms of American life in ways that conventional advertising never could. The beer brand became inseparable from the game-day experience.

Celebrity endorsement pushed the strategy further still. When Sean "Diddy" Combs partnered with Ciroc vodka in the 2000s, the arrangement went beyond traditional celebrity advertising. Combs became a brand ambassador whose personal lifestyle — the parties, the music, the image of success — served as a continuous, living advertisement. When George Clooney co-founded Casamigos tequila, the brand's identity was essentially indistinguishable from Clooney's own — sophisticated, effortless, aspirational. The sale of Casamigos to Diageo for one billion dollars demonstrated just how valuable that fusion of celebrity and brand could be.

By the end of the twentieth century, alcohol had achieved a kind of cultural saturation that would have been unimaginable to the temperance advocates of a hundred years earlier. It was in the movies, on the sidelines, in the music, on the billboards, and in the glossy pages of every magazine. It was not merely advertised. It was ambient — a background hum in the culture so constant that most people stopped hearing it entirely. And then the internet arrived, and everything accelerated.
"""

CHAPTER_7 = """
The internet did not immediately transform alcohol advertising. The first banner ads appeared in the mid-1990s, and while alcohol companies experimented with the new medium, the early web was a clumsy advertising vehicle — slow, text-heavy, and limited in reach. But the industry recognized the potential early. Jack Daniel's launched its website in 1997, and for more than two decades, it served as both a direct marketing channel and a destination for brand enthusiasts. It was among the first consumer brands to understand that a website could be more than a digital brochure — it could be a community.

The real transformation began with programmatic advertising and email marketing in the 2000s. For the first time, alcohol brands could target individual consumers with personalized messages based on their browsing history, purchase patterns, and demographic profiles. The old broadcast model — one message to millions — gave way to a precision approach that could reach exactly the right person at exactly the right moment. A consumer who searched for cocktail recipes might see bourbon ads for the next month. Someone who bought wine online would receive email campaigns calibrated to their preferences. The technology was not unique to alcohol, but the industry adopted it with characteristic speed.

Social media changed everything again. Platforms like Facebook, Instagram, and Twitter offered something no previous advertising medium could match: the ability to make commercial messages look like personal communication. Smirnoff's Facebook strategy, developed in the early 2010s, was designed with explicit intent to make branded content indistinguishable from posts by friends and family. The brand's social media team crafted posts that mimicked the casual tone, visual style, and emotional register of organic user content. A Smirnoff post in your feed looked and felt like something your college roommate might have shared.

The strategy worked — and its reach extended far beyond the legal drinking age. Analyses of Smirnoff's Facebook following revealed that roughly seventy-five percent of the brand's followers were under the legal drinking age. This was not an unintended consequence. Social media platforms' own architecture — designed to maximize engagement and sharing, with minimal barriers to access — made it structurally impossible to restrict alcohol advertising to adults. A teenager scrolling through Instagram encountered the same alcohol content as a thirty-year-old, often without any age-verification mechanism beyond a checkbox that no one enforced.

The blurring of commercial and user-generated content created a new kind of advertising environment. When a college student posted a photo holding a bottle of craft beer, was that advertising? When an influencer with a hundred thousand followers mentioned a tequila brand in a story, was that a paid endorsement or a personal recommendation? The lines dissolved, and the dissolution was profitable. Alcohol companies could now benefit from word-of-mouth marketing at a scale that no previous generation of advertisers could have imagined, and they could do it at a fraction of the cost of traditional media buys.

By the time the COVID-19 pandemic arrived in early 2020, the infrastructure was already in place. Americans were confined to their homes, anxious, isolated, and spending more time on social media than ever before. Alcohol delivery services reported demand increases of three hundred percent or more. And the industry's digital marketing apparatus — honed over two decades of experimentation — was perfectly positioned to reach every one of those homebound consumers, on every device, in every room of the house, at every hour of the day. The ancient industry had adapted once again, and the consequences were only beginning to be understood.
"""

CHAPTER_8 = """
Nine thousand years of history leaves certain patterns visible if you know where to look. Three, in particular, stand out from the long story told in the preceding chapters.

The first is this: the alcohol industry's success has always been tied to advances in communication technology. This is not a coincidence. It is a strategy. From the painted tavern signs mandated by Richard II to the printed books that spread distillation knowledge across Europe, from the color newspaper advertisements of the nineteenth century to the programmatic digital campaigns of the twenty-first, the industry has consistently been among the earliest and most aggressive adopters of every new medium. When radio emerged, breweries were there. When television arrived, beer companies were among the first sponsors. When social media platforms created new ways to reach consumers, alcohol brands were already designing content strategies. The pattern is so consistent that it amounts to a defining characteristic of the industry itself.

The second pattern is darker. The alcohol industry has a long and documented history of exploiting vulnerable populations. The triangular trade that built the colonial rum industry was powered by enslaved labor. The Jim Crow era concentrated alcohol wealth in the hands of white capitalists while systematically excluding Black entrepreneurs. Depression-era advertising targeted economically devastated men and isolated women with messaging designed to exploit their psychological vulnerabilities. And the social media strategies of the twenty-first century have proven structurally incapable of preventing exposure of minors to alcohol marketing — a failure that available evidence suggests the industry has been slow to remedy.

The third pattern concerns the lasting power of media portrayals. When James Bond ordered a vodka martini in 1962, he created an association between sophistication and Smirnoff that endured for more than six decades. When wartime photographs showed soldiers drinking in liberated Paris, they created an equation between alcohol and freedom that shaped American culture for generations. Media portrayals of alcohol are not ephemeral. They accumulate, layer upon layer, until they form a cultural bedrock that individuals absorb without conscious awareness. This is what makes alcohol advertising so effective and so difficult to counter — it does not merely sell a product. It constructs a world.

The COVID-19 pandemic brought all three patterns into convergence. A communications technology — social media — reached people in their most vulnerable moments, confined to their homes, frightened, and cut off from normal social support. The industry's digital marketing apparatus delivered alcohol advertising directly to those people with unprecedented precision. And the accumulated weight of decades of media portrayal — alcohol as comfort, as reward, as escape, as the thing you reach for when the world becomes too much — primed millions of Americans to respond in exactly the way the advertising intended.

The drinking age is not a number on a card. It is the age we live in — an era in which the ancient industry of alcohol has achieved a level of commercial sophistication and cultural penetration that its founders could never have imagined. Understanding how we arrived here is the first step toward deciding where we go next. That decision belongs to all of us. But it must be made with open eyes.
"""

AFTERWORD = """
I began this research as a doctoral student at the University of Texas at Austin, surrounded by the artifacts of a drinking culture so pervasive that it had become invisible. Austin is a city that loves its bars, its live music venues, its craft breweries, and its weekend brunches with bottomless mimosas. I participated in that culture, as most people do, without thinking very much about where it came from or who benefits from it.

Writing this history changed that. Not because the facts were surprising — most of them are hiding in plain sight — but because seeing them assembled in sequence reveals a pattern that is difficult to unsee. The alcohol industry is not simply a business that makes a product people enjoy. It is one of the most adaptive, strategically sophisticated, and historically consequential commercial enterprises in human civilization. It has survived prohibition, regulation, and social movements that would have destroyed lesser industries. It has shaped the media landscape, the political process, and the cultural imagination of entire nations.

I do not presume to tell anyone whether or how much to drink. That is a personal decision, and I respect it. But I do believe that decisions made in ignorance are not truly free. My hope is that this book has provided some of the context that makes genuine choice possible. The industry will keep adapting. The question is whether the rest of us will keep paying attention.
"""

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
    add_chapter_title(doc, "CHAPTER 5\nA Soldier's Drink")
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
