#!/usr/bin/env python3
"""Build the Dutch page (nl/index.html) from the English page (index.html).

English is the source. After every change to index.html, run:
    python3 tools/build_nl.py
Text nodes are matched by the start of their English text, so a changed
English sentence fails loudly here until its Dutch line is updated too.
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
src = (ROOT / "index.html").read_text(encoding="utf-8")
s = src

# Exact replacements (head, attributes, scripts). Each must occur at least once.
EXACT = [
    ('<html lang="en">', '<html lang="nl">'),
    ('<title>Cognitive &amp; Systemic Coaching | Annemieke – Nouvo Consultancy</title>',
     '<title>Cognitieve &amp; systemische coaching | Annemieke – Nouvo Consultancy</title>'),
    ('<meta name="description" content="Cognitive and systemic coaching with Annemieke. Single sessions, a 6 months program or a year program with family constellation. In person, online or outdoors.">',
     '<meta name="description" content="Cognitieve en systemische coaching met Annemieke. Losse sessies, een traject van 6 maanden of een jaartraject met familieopstelling. Live, online of buiten.">'),
    ('<link rel="canonical" href="https://nouvoconsultancy.com/">', '<link rel="canonical" href="https://nouvoconsultancy.com/nl/">'),
    ('<meta property="og:title" content="What if you got curious, about what you’re not seeing yet?">',
     '<meta property="og:title" content="Wat zie jij nog niet?">'),
    ('<meta property="og:description" content="Cognitive and systemic coaching with Annemieke. Single sessions, a 6 months program or a year program, in person, online or outdoors.">',
     '<meta property="og:description" content="Cognitieve en systemische coaching met Annemieke. Losse sessies, een traject van 6 maanden of een jaartraject, live, online of buiten.">'),
    ('<meta property="og:url" content="https://nouvoconsultancy.com/">', '<meta property="og:url" content="https://nouvoconsultancy.com/nl/">'),
    ('content="Annemieke, coach at Nouvo Consultancy"', 'content="Annemieke, coach bij Nouvo Consultancy"'),
    ('<meta property="og:locale" content="en_GB">', '<meta property="og:locale" content="nl_NL">'),
    ('"url": "https://nouvoconsultancy.com/",', '"url": "https://nouvoconsultancy.com/nl/",'),
    ('<a class="skip" href="#main">Skip to content</a>', '<a class="skip" href="#main">Naar de inhoud</a>'),
    ('<nav class="lang" aria-label="Language">', '<nav class="lang" aria-label="Taal">'),
    ('<a href="/nl/" hreflang="nl" lang="nl">', '<a href="/nl/" hreflang="nl" lang="nl" aria-current="page">'),
    ('<a href="/" hreflang="en" lang="en" aria-current="page">', '<a href="/" hreflang="en" lang="en">'),
    ('alt="Annemieke smiling in a white blouse, standing by a wooden fence in a meadow"', 'alt="Annemieke lacht in een witte blouse bij een houten hek in een weiland"'),
    ('alt="Portrait of Annemieke laughing in a field"', 'alt="Portret van Annemieke, lachend in een veld"'),
    ('alt="Woman sitting on a hill looking out over a city at sunrise"', 'alt="Vrouw op een heuvel kijkt bij zonsopgang uit over een stad"'),
    ('alt="Close-up of apples and leaves"', 'alt="Close-up van appels en bladeren"'),
    ('alt="Old family photographs spread on a table"', 'alt="Oude familiefoto’s verspreid over een tafel"'),
    ('alt="Misty pine forest"', 'alt="Mistig dennenbos"'),
    ('alt="Brick farmhouse with an olive tree in a pot and a wooden bench"', 'alt="Bakstenen boerderij met een olijfboom in een pot en een houten bank"'),
    ('value="New message via the Nouvo Consultancy website"', 'value="Nieuw bericht via de website van Nouvo Consultancy (NL)"'),
    ('<label for="name">Name</label>', '<label for="name">Naam</label>'),
    ('<label for="email">Email</label>', '<label for="email">E-mail</label>'),
    ('<label for="message">Message</label>', '<label for="message">Bericht</label>'),
    ('<button class="btn" type="submit">Send message</button>', '<button class="btn" type="submit">Verstuur bericht</button>'),
    ("status.textContent = 'Sending…';", "status.textContent = 'Bezig met versturen…';"),
    ("status.textContent = 'Thank you! Your message has been sent.';", "status.textContent = 'Dankjewel! Je bericht is verstuurd.';"),
    ("status.textContent = 'Something went wrong. Please try again or give me a call.';", "status.textContent = 'Er ging iets mis. Probeer het opnieuw of bel me even.';"),
    ('<strong>Phone</strong>', '<strong>Telefoon</strong>'),
    ("const MORE = 'Read more', LESS = 'Show less';", "const MORE = 'Lees meer', LESS = 'Lees minder';"),
]

# Text nodes: English start of the text -> full Dutch text.
TEXT = [
    ("What if you got curious", "Wat zie jij nog niet?"),
    ("Hi, I'm Annemieke.", "Hoi, ik ben Annemieke. Ik help je ontdekken wat je keuzes écht drijft, met cognitief en systemisch werk. We kijken naar de patronen die je misschien tegenhouden en vinden een weg vooruit die goed voelt voor jou."),
    ("How we can work together.", "Zo kunnen we samenwerken."),
    ("I'm interested", "Ik heb interesse"),
    ("Single sessions", "Losse sessies"),
    ("A 1.5-hour session", "Een sessie van 1,5 uur waarin cognitieve en systemische coaching samenkomen, met ruimte om te onderzoeken wat er nu voor jou speelt."),
    ("Ideal if you want to dive deeper", "Ideaal als je dieper op een specifiek vraagstuk wilt ingaan, een frisse blik wilt krijgen, of gewoon wilt ervaren hoe ik werk voordat je voor een langer traject kiest."),
    ("Sessions can take place", "Sessies kunnen live of online plaatsvinden."),
    ("6 months program", "Traject van 6 maanden"),
    ("Monthly sessions over six months", "Maandelijkse sessies gedurende zes maanden, waarin systemische coaching samengaat met optionele sessies buiten in de natuur."),
    ("Nature offers space", "De natuur geeft ruimte om te vertragen, afstand te nemen van de dagelijkse afleiding en beter te luisteren naar wat er vanbinnen gebeurt."),
    ("Year program", "Jaartraject"),
    ("A deeper year-long journey", "Een dieper traject van een jaar, met meer ruimte en tijd voor blijvende verandering. Dit krijg je:"),
    ("Your own personal family constellation", "Je eigen persoonlijke familieopstelling"),
    ("Monthly coaching sessions, with the option", "Maandelijkse coachingsessies, binnen of buiten in de natuur"),
    ("WhatsApp support between sessions", "Ondersteuning via WhatsApp tussen de sessies, voor momenten waarop je even richting of reflectie nodig hebt"),
    ("About me", "Over mij"),
    ("Hey! Good to see you here.", "Hoi! Fijn dat je er bent."),
    ("I believe we all have many layers", "Ik geloof dat we allemaal uit vele lagen bestaan, en ik ben daarop geen uitzondering. Ik ben altijd nieuwsgierig geweest naar mensen en naar wat er onder de oppervlakte ligt. Ik ben een mix van introvert en avonturier: net zo blij als ik verdwaal in mijn eigen gedachten als wanneer ik de wereld in stap om te ontdekken, te verbinden en iets nieuws te beleven."),
    ("My professional journey started", "Mijn loopbaan begon in de recruitment, maar mijn echte fascinatie is altijd de mens geweest: wat ons drijft, waarom we de keuzes maken die we maken, welke patronen we blijven herhalen en wat er daaronder allemaal speelt."),
    ("Over the years, that curiosity", "Door de jaren heen bracht die nieuwsgierigheid me bij cognitieve coaching en persoonlijke ontwikkeling. Meer recent voegde systemische coaching een belangrijke laag toe aan mijn werk: verder kijken dan het individu, en onderzoeken hoe onze relaties, familiegeschiedenis, omgeving en de systemen waar we deel van uitmaken bepalen wie we zijn en hoe we door het leven gaan."),
    ("Today, my coaching brings together", "In mijn coaching komen nu verschillende perspectieven samen: onze gedachten, emoties, ons lichaam en de systemen waar we bij horen. We zijn vaak zo gewend om ons leven te doordenken, dat we vergeten dat er meer is om naar te luisteren."),
    ("For me, coaching isn’t about fixing you", "Voor mij gaat coaching niet over jou repareren of vertellen wat je moet doen. Het gaat over ruimte maken om te vertragen, nieuwsgierig te worden naar je patronen, dingen vanuit een ander perspectief te zien en opnieuw contact te maken met wat er écht toe doet voor jou."),
    ("Coaching approaches", "Mijn manier van coachen"),
    ("Cognitive", "Cognitief"),
    ("The stories you tell yourself", "De verhalen die je jezelf vertelt, bepalen meer dan je misschien denkt. Samen onderzoeken we de gedachten en overtuigingen achter je keuzes, waar ze vandaan komen en waar er ruimte is om dingen anders te zien en nieuwe keuzes te maken."),
    ("Somatic", "Somatisch"),
    ("Not everything can be understood", "Niet alles is te begrijpen door erover na te denken. Met ademwerk, visualisatie en lichaamsbewustzijn vertragen we en luisteren we naar wat je lichaam je misschien vertelt, soms nog voordat je er woorden voor hebt."),
    ("Systemic", "Systemisch"),
    ("Some patterns make more sense", "Sommige patronen worden pas duidelijk als we verder kijken dan het individu. We onderzoeken hoe familiegeschiedenis, relaties en de systemen waar je deel van uitmaakt je denken, voelen en handelen kunnen vormen. Bewustwording van die patronen geeft ruimte om te kiezen wat nog bij jou hoort, en wat je klaar bent om los te laten."),
    ("Outdoor", "Buiten"),
    ("Sometimes, stepping outside", "Soms helpt een stap naar buiten om vanbinnen iets in beweging te brengen. Weg van schermen, routines en vier muren geeft de natuur ruimte om te vertragen, je hoofd leeg te maken en weer contact te maken met jezelf. Naast elkaar wandelen maakt het bovendien vaak makkelijker om je open te stellen en het gesprek vanzelf te laten ontstaan."),
    ("Reviews", "Reviews"),
    ("Annemiek is your sparring partner", "Annemiek is je sparringpartner en grootste cheerleader in één. Een strategisch denker met de empathie van een golden retriever (zonder het gekwijl). Ze luistert niet alleen, ze hoort écht wat je zegt. Ze leest tussen de regels door en vertaalt mijn zakelijke inzichten alsof het de normaalste zaak van de wereld is. En het mooiste? Voor je het weet doe je een salsadraai midden in een meeting. Miek, jij brengt de energie, krijgt iedereen in de juiste flow en maakt werk leuk! Zo blij dat ik je heb leren kennen 🎉."),
    ("I did a number of private coaching sessions", "Ik heb op eigen initiatief een aantal privé-coachingsessies bij Annemiek gedaan. Ik verwachtte dat ze me verder kon helpen met een coachvraag over focus. Die verwachting is waargemaakt. Annemiek kan ontzettend goed luisteren en komt precies met de vraag of observatie die je niet zag aankomen. Ze zet ook heel natuurlijk tools als visualisatie in. Het inzicht dat ik eraan overhield galmt nog elke week na in mijn hoofd en helpt me om focus te houden. Dankjewel Annemiek, ook voor de veilige setting die je tijdens de sessies wist te creëren!"),
    ("Annemiek has given me so much", "Annemiek heeft me zoveel gegeven, zowel zakelijk als persoonlijk. Ze luistert echt, stelt de juiste vragen en brengt op een zachte manier helderheid in situaties. Daarnaast geeft ze praktische tools die je ook echt kunt gebruiken. Wat ik vooral waardeer, is dat Annemiek je niet vertelt wat je moet doen, maar je helpt om tot je eigen inzichten en antwoorden te komen. Ze is warm, zorgzaam en oprecht geïnteresseerd. Bij haar voelt het veilig om over alles te praten, of het nu gaat over werk, keuzes die ik moet maken of dingen die me persoonlijk bezighouden. Mijn gesprekken met Annemiek geven me inzicht, richting en soms precies het duwtje dat ik nodig heb. Tot op de dag van vandaag haal ik zoveel uit haar begeleiding, en daar ben ik haar heel dankbaar voor!"),
    ("Let's connect", "Neem contact op"),
    ("Curious? Let’s have a conversation!", "Nieuwsgierig? Laten we kennismaken!"),
    ("Leave a message and I’ll get back to you", "Laat een bericht achter, dan neem ik zo snel mogelijk contact met je op."),
]

errors = []
for en, nl in EXACT:
    if en not in s:
        errors.append("exact: " + en[:80])
    s = s.replace(en, nl)

for start, nl in TEXT:
    pat = re.compile(r">(\s*)" + re.escape(start) + r"[^<]*<")
    s, n = pat.subn(lambda m: ">" + m.group(1) + nl + "<", s)
    if n == 0:
        errors.append("text: " + start)

if errors:
    sys.exit("Dutch build failed, update tools/build_nl.py:\n  " + "\n  ".join(errors))

out = ROOT / "nl" / "index.html"
out.parent.mkdir(exist_ok=True)
out.write_text(s, encoding="utf-8")
print("wrote", out.relative_to(ROOT))
