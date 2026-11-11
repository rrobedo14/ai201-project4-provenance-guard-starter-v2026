"""
What your test runs. ← UNIT 8, MILESTONE 3

Each of your five criteria needs something run against it. A criterion about
false positives needs your own writing. One about label coverage needs inputs
across the score range. One about the appeal path needs a real content_id.

Working that out is Milestone 3's first step, and this file is where you write
it down. `run_eval.py` runs everything here three times.

A scenario carries **either** of these:

    "texts"   a list of strings. Each is sent as {"text": ..., "creator_id": ...}
              with a creator_id made up for you. Use this for most criteria.

    "bodies"  a list of whole request bodies, sent exactly as written. Use this
              when the malformed request IS the point — empty text, no `text`
              field at all, something enormous. A bad-input criterion needs it,
              because you cannot express "the field is missing" as a string.

Rate limits: every text and every body gets its own creator_id, so each one is
sent once per trial — three times per run, under the 5-per-minute limit. A body
with no creator_id would fall back to the IP address and share one bucket, and
the run would start getting 429s instead of testing anything.

What each criterion needs (criteria.md):

    1. False positives  10 pieces of my own writing, at most 1 scoring 0.70+.
    2. Score spread     10 clearly-AI + 10 clearly-human; AI average >= 0.70,
                        human average <= 0.35, gap >= 0.35.
    3. Label coverage   15 inputs; each of the three labels at least twice.
    4. Appeal path      a real content_id, then /appeal — not sendable from here.
    5. Bad input        missing / empty / oversized text -> 100% get a 400.
"""

# ── Criterion 1 (and the human half of criterion 2) ─────────────────────────
# ⚠️ YOUR OWN WRITING. Not AI text, not a sample from the web — things you
# actually wrote: old essays, emails, posts, assignments. A paragraph or two
# each (about 80–200 words) so the model signal has enough to read.
# The run refuses to start while any of these still say REPLACE ME.
MY_WRITING = [
    # 1. old use-case assignment: how the use cases were selected
    "Theses use cases were chosen for our project as they are the most important for the functionality of the application. These cases reflect the critical features of our application which include, geolocation, matchmaking, and access to rooms, that our application offers the users and what makes our application differ from what is out there. Our matchmaking case makes extensive use of the geolocation feature to find matches. Being able to access rooms for chatting is also one of things we considered when selecting the use cases, as communication is a big part of interacting with the application.",
    # 2. same assignment: login / register
    "Registering a user for access to the application using the proper format. A user registering an account will have a valid email address that can be used to verify authenticity. A registered account will have a unique and valid username and user information which includes alphanumeric and standard special characters. We don’t want to have one user with the same account information as another for obvious reasons. Another thing is that when registering an account, the email will have to be unique as well to avoid multiple account by the same user. Logging into an account for access to the application. A user will have a valid registered and active account in good standing. Successful login will occur if the account information matches the information on the application, such as username and password. Users will have three attempts to input the correct credentials after that the account will be locked. This is standard in most if the industry.",
    # 3. same assignment: map + home page
    "Viewing the map on the application. The map view will have information on the location such city, state, and zip code. In the view of the map the user will have the option to select matchmaking based on location. The user can specify a certain range from a selected city or zip code and have the results filtered out. Viewing the home page for information about the application. The home page will have information about user and the different sports available as will include navigation towards parts of the application. From here the user navigate towards all the other pages on the application. This is also the main information hub for the user, which will update them on any relevant information that is of interest, i.e., a new post or a comment on a post they created.",
    # 4. same assignment: matchmaking, chat, teams, profile
    "Starting the matchmaking will show other user’s profile and their rating. Profiles with a higher rating will show up first on the application which the user can select. Communication is an important aspect to all interactions that we have every day. In this chat feature we can talk to a selected user and send them information. Accessing other user’s profile and seeing their public information. A user should be able to see the username and profile picture. A user should be able to view different teams’ profile and see information regarding a team. There will be things such as contact information and picture; this can help a user get a better idea of the team in general. Accessing a user’s profile, which includes information of the user such as username, picture, and various other setting that the user can change.  This will enable the user to add information about themselves which helps in finding partners.",
    # 5. written fresh: weekend car repair
    "Last weekend I worked on my car, the brake cylinder from the back brakes started leaking so I had to change it.\nI saw that the master cylinder was low and has very little brake fluid and since I had to take the brake apart anyways i just went ahead and changed both the back brakes.",
    # 6. written fresh: extension email
    "Hello this is Rogelio, I was emailing you regarding on an extension for Project 4 that is due on Friday, you mentioned in class to email you if we needed an extension.",
    # 7. written fresh: why computer science
    "I picked computer science because in high school I took a computer class and we wrote some basic programs and I had a lot of fun writing code.\nthe program we wrote was a simple one, one that changed the color of a web page, we wrote it in notepad and then use the command prompt to run it. I thought that was pretty cool to see how what I build changed something, to see the effect of my work in the real world.",
    # 8. written fresh: cataloging merchandise at work
    "When cataloging merchandise, you have to make sure that the label is received and that that receive location is set to receiving. When the merchandise is not in the proper zone then there errors can occur and it will not let you move the merchandise until it is in the proper zone.",
    # 9. written fresh: astronomy, how the sun shines
    "Many people believe that the sun is a glowing ball of fire in the sky but this is not the case. On earth fire is a chemical reaction that requires oxygen and since there is no oxygen in space then the fire as people know cannot exits in space. Then how does the sun burn so brightly, well the answer is a secret force called fusion.",
    # 10. my five "Why this target" sentences from criteria.md, joined
    "I allow at most 1 false positive in 10 because on a publishing platform, a wrong accusation costs a writer their trust and reputation, whereas a missed detection only lets a piece of AI text slip through. I require a 0.35 gap because a clear separation ensures the system has a distinct boundary between machine and human writing, preventing borderline inputs from collapsing into random guesses. I require each label to appear at least twice because every label must be reachable so the system can properly signal ambiguity and nuance instead of forcing every edge case into an artificial binary. I set a 100% target because creators disputing a false flag need an ironclad guarantee that their dispute is reliably tracked and recorded for human review without dropping data. I set a 100% interception target because strict input validation protects the core detection models and database backends from failing on malformed or malicious data.",
]

# ── Criterion 2: the AI half ─────────────────────────────────────────────────
# Ten paragraphs generated by an AI model (Claude) in the generic, even,
# "several key strategies" register. Comments show what the pipeline scored
# them when this file was written — two land at 0.69, held under the AI line
# by the disagreement cap. They stay in: dropping the ones that miss would be
# picking the test to fit the result.
CLEARLY_AI = [
    "Effective leadership is essential for the success of any organization. Leaders who communicate a clear vision are better able to motivate their teams and achieve long-term goals. There are several key qualities that distinguish successful leaders. First, strong leaders demonstrate integrity, which builds trust among employees. Second, they are adaptable and able to respond to changing circumstances. Finally, effective leaders invest in the development of their team members, ensuring that the organization remains competitive over time.",  # ai 0.78
    "Climate change represents one of the most significant challenges facing the world today. Rising global temperatures are contributing to more frequent extreme weather events, rising sea levels, and disruptions to ecosystems. Addressing this issue requires coordinated action at multiple levels. Governments can implement policies that reduce greenhouse gas emissions. Businesses can adopt sustainable practices throughout their operations. Individuals can also make a meaningful difference by reducing energy consumption and making environmentally conscious choices.",  # ai 0.83
    "Reading offers numerous benefits for individuals of all ages. Regular reading improves vocabulary, enhances comprehension skills, and strengthens critical thinking. In addition, reading can reduce stress and provide a valuable opportunity for relaxation. There are several ways to develop a consistent reading habit. First, setting aside a specific time each day for reading can help establish a routine. Second, choosing books that align with personal interests makes the experience more enjoyable. Ultimately, reading is a lifelong investment in personal growth.",  # ai 0.74
    "Technology has transformed the way people communicate in the modern world. Social media platforms, messaging applications, and video conferencing tools have made it easier than ever to stay connected with others. However, these advancements also present certain challenges. Excessive screen time can negatively affect mental health and reduce face-to-face interaction. It is therefore important for individuals to maintain a healthy balance between online and offline activities. By using technology mindfully, people can enjoy its benefits while minimizing its drawbacks.",  # ai 0.76
    "A healthy diet is a fundamental component of overall well-being. Consuming a variety of fruits, vegetables, whole grains, and lean proteins provides the body with essential nutrients. Proper nutrition supports immune function, maintains energy levels, and reduces the risk of chronic diseases. There are several practical strategies for improving dietary habits. Planning meals in advance can help individuals make healthier choices. Additionally, limiting processed foods and added sugars is widely recommended. Small, consistent changes can lead to significant long-term benefits.",  # unsure 0.69
    "Teamwork plays a crucial role in achieving organizational objectives. When team members collaborate effectively, they can combine their skills and perspectives to solve complex problems. Successful teams share several important characteristics. First, they establish clear roles and responsibilities. Second, they maintain open lines of communication. Third, they foster an environment of mutual respect and trust. By prioritizing these elements, organizations can create high-performing teams that consistently deliver positive results.",  # unsure 0.69
    "Education is widely regarded as one of the most important investments a society can make. A strong education system equips individuals with the knowledge and skills needed to participate fully in the economy. Furthermore, education promotes social mobility and contributes to informed civic engagement. To improve educational outcomes, it is important to ensure that all students have access to qualified teachers, adequate resources, and supportive learning environments. Investing in education ultimately benefits both individuals and society as a whole.",  # ai 0.88
    "Financial planning is an essential skill that can help individuals achieve stability and security. Creating a budget allows people to track their income and expenses and identify areas where they can save. In addition, building an emergency fund provides a safety net in the event of unexpected costs. Another important aspect of financial planning is saving for retirement. By starting early and contributing consistently, individuals can take advantage of compound growth. Overall, careful financial planning leads to greater peace of mind.",  # ai 0.82
    "Sleep is a vital aspect of maintaining good health. Adequate sleep supports cognitive function, emotional regulation, and physical recovery. Unfortunately, many people do not get the recommended amount of sleep each night. There are several strategies that can improve sleep quality. Maintaining a consistent sleep schedule helps regulate the body's internal clock. Creating a comfortable sleep environment and limiting screen time before bed are also beneficial. By prioritizing sleep, individuals can enhance their overall well-being and daily performance.",  # ai 0.81
    "Customer service is a key factor in the success of any business. Companies that provide excellent service are more likely to retain customers and build a positive reputation. There are several best practices for delivering high-quality customer service. First, employees should listen carefully to customer concerns. Second, they should respond promptly and professionally. Third, they should take ownership of problems and work to resolve them efficiently. By consistently meeting customer expectations, businesses can foster loyalty and drive long-term growth.",  # ai 0.81
]

SCENARIOS = [
    {
        "name": "my own writing",
        "criterion": 1,
        "texts": MY_WRITING,
    },
    {
        "name": "AI side of spread",
        "criterion": 2,
        "texts": CLEARLY_AI,
    },
    {
        # The same ten pieces as criterion 1. My own writing is the clearest
        # human baseline I have — I know for certain who wrote it.
        "name": "human side of spread",
        "criterion": 2,
        "texts": MY_WRITING,
    },
    {
        "name": "label coverage",
        "criterion": 3,
        # 15 inputs, five aimed at each band. Sources and the score each got
        # when this file was written are in the comments. What matters here is
        # whether each label is reachable, not who wrote the text.
        "texts": [
            # aimed at human
            "I didn't sleep. Not properly, anyway — I lay there listening to the boiler tick and thinking about the thing I'd said to Marcus at the pub, which was stupid, and which he will absolutely bring up again. Twice now. So: coffee, and the long way round to work, and a plan. The plan lasted until about ten past nine, when Priya asked how the weekend was and I said \"fine\" in the voice that means it wasn't, and she put her mug down and looked at me. That's the trouble with Priya. She notices.",  # samples/clearly_human.json: human 0.31
            "Went to the shops. Forgot the milk again. Classic.",  # written by Claude, short and casual: human 0.32
            "Testing the rate limit with a repeated submission body.",  # flood text from the attack set: human 0.25
            "Communication at work matters more than people say it does — and I mean the boring kind, not the away-day kind. Teams that actually tell each other things get more done. Obviously. A few things help. Regular check-ins, which everyone hates and everyone needs. Writing decisions down, so nobody has to remember what was agreed in a corridor in March. And making it genuinely safe to ask a stupid question, which is the hardest one and the one that matters most.",  # attack set EV05, heavy human edit: human 0.35
            # aimed at unsure
            "Time management matters more than people admit, especially now that work moves as fast as it does. If you're organised you hit deadlines, and you're less frazzled doing it. A few things actually help. Prioritise — work out what genuinely matters and do that first. Cut the interruptions; notifications wreck focus and the damage is worse than it feels at the time. And take breaks, short ones, often.",  # samples/borderline.json: unsure 0.41
            "The parish registers of Ashworth survive, with lamentable gaps, from 1563 onward. Their omissions are themselves instructive: no baptisms were recorded during the winter of 1647, when the incumbent, a Mr. Thomas Greaves, appears to have absconded rather than subscribe to the Covenant. His successor, whose hand is cramped and idiosyncratic, entered marriages and burials indiscriminately on the same leaves. Historians have tended to treat such irregularities as clerical negligence; I am inclined to read them otherwise — as the residue of a community whose ecclesiastical loyalties were, for a decade at least, genuinely unsettled.",  # samples/formal_human.json: unsure 0.40
            "Went for a run. Legs hurt. Worth it.",  # attack set FP08: unsure 0.47
            "The importance of effective communication in the workplace cannot be overstated. Really. Teams that communicate clearly are better positioned to achieve their objectives and avoid costly misunderstandings. Really. There are several strategies organisations can adopt to improve this. Really. First — establishing regular check-ins ensures that information flows consistently between team members. Really. Second — documenting decisions provides a reference point that reduces ambiguity. Really. Finally — encouraging an environment where questions are welcomed helps surface issues early. Really. Implementing these approaches can lead to meaningful improvements in team performance and overall satisfaction.",  # attack set EV02: unsure 0.51
            "The importance of effective communication in the workplace cannot be overstated; and, moreover, Teams that communicate clearly are better positioned to achieve their objectives and avoid costly misunderstandings; and, moreover, There are several strategies organisations can adopt to improve this; and, moreover, First —  establishing regular check-ins ensures that information flows consistently between team members; and, moreover, Second, documenting decisions provides a reference point that reduces ambiguity; and, moreover, Finally, encouraging an environment where questions are welcomed helps surface issues early; and, moreover, Implementing these approaches can lead to meaningful improvements in team performance and overall satisfaction.",  # attack set EV07: unsure 0.47
            "We got to the campsite about four. The pitch was fine, a bit sloped, but there was a tap nearby and the toilets were clean enough. Putting the tent up took longer than it should have because I had forgotten how the poles went. The weather held until Saturday night. Then it rained hard and kept raining. We stayed in the tent and played cards and ate most of the food we had brought for Sunday. On Sunday we packed up wet and drove home early. It was not the weekend we planned but the kids enjoyed it and we would go back.",  # attack set FP01: unsure 0.69
            # aimed at ai
            "The importance of effective time management cannot be overstated in today's fast-paced work environment. Professionals who develop strong organizational habits are better positioned to meet deadlines and reduce stress. There are several key strategies that can help individuals improve their productivity. First, prioritization is essential. By identifying the most important tasks and addressing them first, workers can ensure that critical objectives are met. Second, minimizing distractions plays a significant role. Setting aside dedicated blocks of time for concentrated work is widely considered beneficial. Finally, regular breaks are important for maintaining performance.",  # samples/clearly_ai.json: ai 0.71
            "Regular exercise offers numerous benefits for both physical and mental health. Studies have consistently shown that people who stay active tend to sleep better and report lower levels of stress. There are several simple ways to build exercise into a busy schedule. First, walking or cycling to work is an easy place to start. Second, short workouts at home can be surprisingly effective, even if it's only twenty minutes. Honestly, the hardest part is just getting started. Finally, finding an activity you actually enjoy makes it far more likely that you'll stick with it over time.",  # samples/edited_ai.json: ai 0.80
            "The importance of effective communication in the workplace cannot be overstated. Teams that communicate clearly are better positioned to achieve their objectives and avoid costly m\n\nThe importance of effective communication in the workplace cannot be overstated. Teams that communicate clearly are better positioned to achieve their objectives and avoid costly m\n\nThe importance of effective communication in the workplace cannot be overstated. Teams that communicate clearly are better positioned to achieve their objectives and avoid costly m",  # attack set EV10: ai 0.96
            "Climate change represents one of the most significant challenges facing the world today. Rising global temperatures are contributing to more frequent extreme weather events, rising sea levels, and disruptions to ecosystems. Addressing this issue requires coordinated action at multiple levels. Governments can implement policies that reduce greenhouse gas emissions. Businesses can adopt sustainable practices throughout their operations. Individuals can also make a meaningful difference by reducing energy consumption and making environmentally conscious choices.",  # AI paragraph 2 above: ai 0.83
            "Education is widely regarded as one of the most important investments a society can make. A strong education system equips individuals with the knowledge and skills needed to participate fully in the economy. Furthermore, education promotes social mobility and contributes to informed civic engagement. To improve educational outcomes, it is important to ensure that all students have access to qualified teachers, adequate resources, and supportive learning environments. Investing in education ultimately benefits both individuals and society as a whole.",  # AI paragraph 7 above: ai 0.88
        ],
    },
    {
        "name": "bad input",
        "criterion": 5,
        # Exactly the three cases the criterion names: missing, empty, and
        # oversized text. Each has its own creator_id (see rate limits above).
        "bodies": [
            {"creator_id": "eval_bad_missing"},                 # no text field at all
            {"text": None, "creator_id": "eval_bad_null"},      # text present but null
            {"text": "", "creator_id": "eval_bad_empty"},       # empty string
            {"text": "   \n\t  ", "creator_id": "eval_bad_blank"},  # whitespace only
            # Oversized: ~60,000 characters, far past the 400-token detector window.
            {"text": "We got to the campsite about four and the pitch was fine. " * 1000,
             "creator_id": "eval_bad_huge"},
        ],
    },

    # ── Criterion 4: the appeal path ─────────────────────────────────────────
    # Not here. run_eval.py only POSTs to /submit and doesn't keep the
    # content_id that comes back, so an appeal can't be chained from this file.
    # Tested by hand instead, three times:
    #
    #   1. curl -X POST http://127.0.0.1:5000/submit -H "Content-Type: application/json" \
    #        -d '{"text": "<a paragraph>", "creator_id": "eval_appeal"}'
    #   2. curl -X POST http://127.0.0.1:5000/appeal -H "Content-Type: application/json" \
    #        -d '{"content_id": "<id from step 1>", "reasoning": "I wrote this myself."}'
    #   3. curl http://127.0.0.1:5000/log?limit=3   -> the appeal entry is there
    #
    # Pass = step 2 returns 200 with the new status, and step 3 shows the entry.
]


def validate() -> list[str]:
    """
    Complain about anything malformed, before a long run rather than during.

    A "bodies" scenario is deliberately exempt from the empty check — an empty
    string is the whole point of a bad-input case, and refusing to run one
    would make that criterion untestable.
    """
    problems = []
    for i, scenario in enumerate(SCENARIOS, 1):
        if not scenario.get("name"):
            problems.append(f"scenario {i} has no name")

        texts = scenario.get("texts")
        bodies = scenario.get("bodies")

        if texts and bodies:
            problems.append(
                f"scenario {i} ('{scenario.get('name')}') has both texts and "
                f"bodies — pick one"
            )
            continue

        if bodies:
            for j, body in enumerate(bodies, 1):
                if not isinstance(body, dict):
                    problems.append(
                        f"scenario {i}, body {j} is not a dict — bodies are whole "
                        f"request bodies, like {{'text': '', 'creator_id': 'x'}}"
                    )
            continue

        if not texts:
            problems.append(f"scenario {i} has no texts and no bodies")
            continue

        for j, text in enumerate(texts, 1):
            if not str(text).strip():
                problems.append(
                    f"scenario {i}, text {j} is empty — if an empty submission is what "
                    f"you're testing, use 'bodies' instead of 'texts'"
                )
            elif str(text).startswith("REPLACE ME"):
                problems.append(
                    f"scenario {i} ('{scenario.get('name')}'), text {j} is still "
                    f"the placeholder"
                )
    return problems
