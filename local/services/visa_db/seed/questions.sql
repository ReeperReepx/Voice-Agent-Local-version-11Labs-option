-- Visa interview questions for all 20 destination countries
-- Categories: academics, finance, intent, ties, background, course_choice, country_specific

-- ============================================================
-- UNITED STATES (US)
-- ============================================================
INSERT INTO visa_questions (destination_country, category, question_text, question_text_hi, officer_objective, difficulty_level, common_failure_patterns, followup_rules) VALUES
('US', 'academics', 'What is your highest level of education?', 'Aapki sabse oonchi padhai kya hai?', 'Verify academic background and progression', 1, 'Vague about grades or institutions', 'Ask for specifics if answer is vague'),
('US', 'academics', 'What was your GPA or percentage in your last degree?', 'Aapke last degree mein kitne marks aaye the?', 'Assess academic performance', 1, 'Cannot recall exact scores', 'Follow up on poor performance explanation'),
('US', 'course_choice', 'Why did you choose this specific program and university?', 'Aapne yeh program aur university kyun chuni?', 'Test genuine interest vs. convenience choice', 2, 'Generic answers like "it is a good university"', 'Probe for specific program features'),
('US', 'course_choice', 'How does this course relate to your previous studies or work?', 'Yeh course aapki pichli padhai ya kaam se kaise juda hai?', 'Check logical progression in academic career', 2, 'No clear connection between past and future studies', 'Ask about career goals if connection is weak'),
('US', 'finance', 'How will you fund your education and living expenses in the US?', 'Aap apni padhai aur rehne ka kharcha kaise uthayenge?', 'Verify financial capacity', 2, 'Unclear funding sources, no documentation mention', 'Ask for specific amounts and sponsors'),
('US', 'finance', 'Who is your financial sponsor and what is their annual income?', 'Aapka financial sponsor kaun hai aur unki saalana income kitni hai?', 'Verify sponsor legitimacy', 2, 'Cannot state sponsor income clearly', 'Ask for relationship to sponsor and income proof'),
('US', 'intent', 'What are your plans after completing your studies?', 'Padhai khatam hone ke baad aapke kya plan hain?', 'Assess intent to return to home country', 3, 'Mentions staying in US, vague about return', 'Probe for specific return plans and job prospects'),
('US', 'intent', 'Why do you want to study in the US instead of your home country?', 'Aap apne desh ke bajaye US mein kyun padhna chahte hain?', 'Test if US education is genuinely needed', 2, 'Cannot articulate why US specifically', 'Ask about comparable programs at home'),
('US', 'ties', 'Do you have any family members currently living in the US?', 'Kya aapke parivaar mein koi US mein rehta hai?', 'Assess immigration risk through family ties', 1, 'Hiding family members in the US', 'Follow up on nature of relationship'),
('US', 'ties', 'What ties do you have to your home country that will bring you back?', 'Aapke apne desh se kya rishte hain jo aapko wapas laayenge?', 'Verify strong home ties', 3, 'Weak ties, no property or family obligations', 'Ask about property, family business, job offers'),
('US', 'country_specific', 'Have you been to the US before? If so, did you comply with your visa terms?', 'Kya aap pehle US gaye hain? Agar haan, toh kya aapne visa niyamon ka paalan kiya?', 'Check travel history and compliance', 1, 'Previous overstay or violation', 'Ask for dates and visa types of previous visits'),
('US', 'background', 'Tell me about yourself and your educational journey so far.', 'Apne baare mein bataiye aur apni padhai ke safar ke baare mein bataiye.', 'Assess overall narrative coherence', 1, 'Rehearsed or scripted-sounding response', 'Ask for specific moments or decisions');

-- ============================================================
-- UNITED KINGDOM (UK)
-- ============================================================
INSERT INTO visa_questions (destination_country, category, question_text, question_text_hi, officer_objective, difficulty_level, common_failure_patterns, followup_rules) VALUES
('UK', 'academics', 'What qualifications do you hold?', 'Aapke paas kya qualifications hain?', 'Verify academic credentials', 1, 'Vague about institution names or grades', 'Ask for transcripts reference'),
('UK', 'course_choice', 'Why have you chosen to study in the UK?', 'Aapne UK mein padhne ka faisla kyun kiya?', 'Genuine student test', 2, 'Only mentions rankings, no personal reason', 'Ask what UK offers that home country does not'),
('UK', 'course_choice', 'Why this particular university and course?', 'Yeh university aur course hi kyun?', 'Test research into the program', 2, 'Cannot name specific modules or faculty', 'Ask about course structure or unique features'),
('UK', 'finance', 'How will you pay for your tuition and living costs?', 'Aap apni fees aur rehne ka kharcha kaise denge?', 'Financial requirement check', 2, 'Funds not clearly available or documented', 'Ask for bank statement details'),
('UK', 'finance', 'Do you have the required funds in your bank account for at least 28 days?', 'Kya aapke bank account mein 28 din se required amount hai?', 'Check compliance with financial rules', 2, 'Funds recently deposited', 'Ask about source of recent deposits'),
('UK', 'intent', 'What will you do after your course finishes?', 'Course khatam hone ke baad aap kya karenge?', 'Assess return intent', 3, 'Plans to stay and work in UK permanently', 'Ask about Graduate Route visa vs return'),
('UK', 'ties', 'Do you have family or friends in the UK?', 'Kya aapke parivaar ya dost UK mein hain?', 'Immigration risk assessment', 1, 'Many family members already settled', 'Ask about nature and frequency of contact'),
('UK', 'background', 'Have you studied abroad before?', 'Kya aapne pehle videsh mein padhai ki hai?', 'Check travel and study history', 1, 'Previous visa refusals not disclosed', 'Ask about any previous visa applications'),
('UK', 'country_specific', 'What is your IELTS score?', 'Aapka IELTS score kya hai?', 'English proficiency verification', 1, 'Score below requirement', 'Ask about weakest section and improvement plans'),
('UK', 'intent', 'Have you applied to universities in your home country as well?', 'Kya aapne apne desh ki universities mein bhi apply kiya hai?', 'Test if UK is a genuine first choice', 2, 'No applications at home suggests immigration intent', 'Ask why home universities were not considered');

-- ============================================================
-- CANADA (CA)
-- ============================================================
INSERT INTO visa_questions (destination_country, category, question_text, question_text_hi, officer_objective, difficulty_level, common_failure_patterns, followup_rules) VALUES
('CA', 'academics', 'What is your educational background?', 'Aapki educational background kya hai?', 'Verify academic history', 1, 'Gaps in education unexplained', 'Ask about any gaps'),
('CA', 'course_choice', 'Why did you choose Canada for your studies?', 'Aapne Canada kyun chuna padhai ke liye?', 'Genuine study intent', 2, 'Only mentions immigration pathways', 'Redirect to academic reasons'),
('CA', 'course_choice', 'Why this specific Designated Learning Institution (DLI)?', 'Yeh specific DLI kyun chuni?', 'Check if student researched the institution', 2, 'Cannot name programs or campus details', 'Ask about DLI-specific features'),
('CA', 'finance', 'How will you support yourself financially in Canada?', 'Aap Canada mein apna kharcha kaise uthayenge?', 'Financial capacity check', 2, 'Relying solely on part-time work', 'Ask for GIC or bank proof details'),
('CA', 'finance', 'Have you arranged a Guaranteed Investment Certificate (GIC)?', 'Kya aapne GIC arrange kiya hai?', 'Check compliance with financial requirements', 2, 'Not aware of GIC requirement', 'Explain GIC and ask about financial planning'),
('CA', 'intent', 'What are your plans after graduation?', 'Graduation ke baad aapke kya plans hain?', 'Assess return intent', 3, 'Plans focused on PR pathway only', 'Ask about career opportunities at home'),
('CA', 'ties', 'What connections do you have in your home country?', 'Aapke apne desh mein kya connections hain?', 'Home ties assessment', 2, 'Weak ties or no family obligations', 'Ask about property, family, job commitments'),
('CA', 'background', 'Have you ever been refused a visa to any country?', 'Kya aapko kabhi kisi desh ka visa refuse hua hai?', 'Check for previous refusals', 1, 'Hiding previous refusals', 'Ask for details of any refusal'),
('CA', 'country_specific', 'Are you aware of the study permit conditions regarding work?', 'Kya aap study permit ke kaam ke niyamon se waakif hain?', 'Check knowledge of visa rules', 2, 'Plans to work more than allowed hours', 'Clarify work hour limits'),
('CA', 'intent', 'Why not study in the US or UK instead?', 'US ya UK ke bajaye Canada kyun?', 'Test specificity of choice', 2, 'Cannot differentiate Canada from alternatives', 'Ask for Canada-specific advantages');

-- ============================================================
-- AUSTRALIA (AU)
-- ============================================================
INSERT INTO visa_questions (destination_country, category, question_text, question_text_hi, officer_objective, difficulty_level, common_failure_patterns, followup_rules) VALUES
('AU', 'academics', 'What have you studied so far?', 'Aapne ab tak kya padhai ki hai?', 'Academic background check', 1, 'Inconsistent dates or institutions', 'Ask for timeline clarification'),
('AU', 'course_choice', 'Why have you chosen Australia for your studies?', 'Australia kyun chuna padhai ke liye?', 'GTE assessment', 2, 'Only mentions post-study work rights', 'Focus on academic reasons'),
('AU', 'course_choice', 'How does this course benefit your career back home?', 'Yeh course aapke ghar ke career ke liye kaise faydemand hai?', 'Test genuine temporary entrant status', 3, 'No clear career plan connected to course', 'Ask about job market at home'),
('AU', 'finance', 'Can you demonstrate sufficient funds for tuition and living?', 'Kya aap tuition aur rehne ke liye paisa dikha sakte hain?', 'Financial capacity verification', 2, 'Funds insufficient or unclear source', 'Ask for annual cost estimate'),
('AU', 'intent', 'Do you intend to return to your home country after studies?', 'Kya aap padhai ke baad wapas jaayenge?', 'Return intent check', 3, 'Evasive or mentions staying', 'Ask for specific return plan'),
('AU', 'ties', 'What family or economic ties do you have at home?', 'Ghar mein aapke kya family ya economic ties hain?', 'Home ties strength', 2, 'No strong ties mentioned', 'Ask about dependents or property'),
('AU', 'country_specific', 'Are you aware of the Genuine Temporary Entrant (GTE) requirement?', 'Kya aap GTE requirement se waakif hain?', 'Test knowledge of visa conditions', 2, 'Not aware of GTE', 'Explain and ask about compliance'),
('AU', 'background', 'Have you previously held any Australian visa?', 'Kya aapke paas pehle koi Australian visa raha hai?', 'Check compliance history', 1, 'Previous overstay', 'Ask about dates and compliance'),
('AU', 'finance', 'Who is funding your education and what is their relationship to you?', 'Aapki padhai kaun fund kar raha hai aur unka aapse kya rishta hai?', 'Sponsor verification', 2, 'Third-party or unclear sponsorship', 'Ask for documentation proof'),
('AU', 'intent', 'What career opportunities exist for you in your home country with this degree?', 'Is degree ke saath aapke desh mein kya career opportunities hain?', 'Test return motivation', 3, 'Cannot name specific opportunities', 'Ask for companies or sectors');

-- ============================================================
-- GERMANY (DE)
-- ============================================================
INSERT INTO visa_questions (destination_country, category, question_text, question_text_hi, officer_objective, difficulty_level, common_failure_patterns, followup_rules) VALUES
('DE', 'academics', 'What is your academic background?', 'Aapki academic background kya hai?', 'Verify educational qualifications', 1, 'Qualifications not recognized in Germany', 'Ask about credential evaluation'),
('DE', 'course_choice', 'Why did you choose to study in Germany?', 'Germany mein padhai kyun?', 'Test genuine academic interest', 2, 'Only mentions free tuition', 'Ask about course-specific reasons'),
('DE', 'course_choice', 'Is your course taught in German or English?', 'Aapka course German mein hai ya English mein?', 'Language readiness check', 1, 'German course but no German proficiency', 'Ask about language certificates'),
('DE', 'finance', 'Have you opened a blocked account with the required amount?', 'Kya aapne blocked account khola hai required amount ke saath?', 'Financial requirement check', 2, 'Not aware of blocked account requirement', 'Explain requirement and ask about plans'),
('DE', 'finance', 'How will you cover your living expenses beyond the blocked account?', 'Blocked account ke alaawa rehne ka kharcha kaise uthayenge?', 'Additional financial capacity', 2, 'Relies only on blocked account minimum', 'Ask about part-time work plans'),
('DE', 'intent', 'What do you plan to do after completing your degree?', 'Degree ke baad kya plan hai?', 'Return intent assessment', 3, 'Mentions staying in Germany for work', 'Ask about career prospects at home'),
('DE', 'ties', 'What motivates you to return to your home country?', 'Aapko apne desh wapas jaane ki kya motivation hai?', 'Home ties check', 2, 'No compelling return reason', 'Ask about family or career commitments'),
('DE', 'country_specific', 'Do you have health insurance coverage for Germany?', 'Kya aapke paas Germany ke liye health insurance hai?', 'Compliance check', 1, 'No insurance arranged', 'Explain requirement'),
('DE', 'background', 'Have you visited Germany or Europe before?', 'Kya aap pehle Germany ya Europe gaye hain?', 'Travel history check', 1, 'Previous Schengen violations', 'Ask about compliance on previous visits'),
('DE', 'academics', 'Do you have a TestAS or APS certificate if required?', 'Kya aapke paas TestAS ya APS certificate hai agar zaruri hai?', 'Check academic prerequisites', 2, 'Missing required certificates', 'Ask about application status');

-- ============================================================
-- FRANCE (FR)
-- ============================================================
INSERT INTO visa_questions (destination_country, category, question_text, question_text_hi, officer_objective, difficulty_level, common_failure_patterns, followup_rules) VALUES
('FR', 'academics', 'What are your academic qualifications?', 'Aapki academic qualifications kya hain?', 'Verify credentials', 1, 'Unrelated previous studies', 'Ask about connection to chosen course'),
('FR', 'course_choice', 'Why France for your studies?', 'France kyun chuna padhai ke liye?', 'Genuine student intent', 2, 'Generic cultural reasons only', 'Ask about specific program advantages'),
('FR', 'course_choice', 'Did you go through the Campus France process?', 'Kya aapne Campus France process follow kiya?', 'Check proper procedure followed', 1, 'Unfamiliar with Campus France', 'Explain and ask about status'),
('FR', 'finance', 'How will you finance your studies in France?', 'France mein padhai ka kharcha kaise uthayenge?', 'Financial capacity', 2, 'Insufficient funds', 'Ask for specific monthly budget'),
('FR', 'intent', 'What are your career plans after studying in France?', 'France mein padhai ke baad career plans kya hain?', 'Return intent', 3, 'Plans to stay permanently', 'Ask about home country career'),
('FR', 'ties', 'Do you have any family in France?', 'Kya aapke parivaar mein koi France mein hai?', 'Immigration risk', 1, 'Many settled family members', 'Ask about relationship nature'),
('FR', 'country_specific', 'Do you speak French? What is your proficiency level?', 'Kya aap French bolte hain? Kitni acchi?', 'Language readiness', 2, 'No French for French-taught course', 'Ask about language learning plans'),
('FR', 'background', 'Have you applied for a Schengen visa before?', 'Kya aapne pehle Schengen visa ke liye apply kiya hai?', 'Travel history', 1, 'Previous refusals', 'Ask for refusal details');

-- ============================================================
-- NETHERLANDS (NL)
-- ============================================================
INSERT INTO visa_questions (destination_country, category, question_text, question_text_hi, officer_objective, difficulty_level, common_failure_patterns, followup_rules) VALUES
('NL', 'academics', 'What have you studied previously?', 'Aapne pehle kya padhai ki hai?', 'Academic verification', 1, 'Gaps unexplained', 'Ask about gaps'),
('NL', 'course_choice', 'Why the Netherlands for your higher education?', 'Higher education ke liye Netherlands kyun?', 'Genuine intent', 2, 'Cannot name specific advantages', 'Ask about program uniqueness'),
('NL', 'finance', 'Can you show proof of sufficient funds?', 'Kya aap sufficient funds ka proof dikha sakte hain?', 'Financial check', 2, 'Funds not meeting threshold', 'Ask about funding sources'),
('NL', 'intent', 'What will you do after completing your program?', 'Program ke baad kya karenge?', 'Return intent', 3, 'Orientation year visa focused', 'Ask about home career'),
('NL', 'country_specific', 'Are you aware of the MVV requirements?', 'Kya aap MVV requirements se waakif hain?', 'Compliance check', 2, 'Not familiar with process', 'Explain and ask about status'),
('NL', 'ties', 'What will bring you back to your home country?', 'Kya cheez aapko wapas le aayegi?', 'Home ties', 2, 'Weak answer', 'Ask specifics');

-- ============================================================
-- IRELAND (IE)
-- ============================================================
INSERT INTO visa_questions (destination_country, category, question_text, question_text_hi, officer_objective, difficulty_level, common_failure_patterns, followup_rules) VALUES
('IE', 'academics', 'Tell me about your educational qualifications.', 'Apni educational qualifications ke baare mein bataiye.', 'Verify background', 1, 'Unclear timeline', 'Ask for dates'),
('IE', 'course_choice', 'Why Ireland for your studies?', 'Ireland kyun chuna padhai ke liye?', 'Genuine student test', 2, 'Only mentions English-speaking', 'Ask for Ireland-specific reasons'),
('IE', 'finance', 'Have you paid your course fees?', 'Kya aapne course fees pay ki hain?', 'Financial commitment check', 1, 'Fees not paid', 'Ask about payment plan'),
('IE', 'finance', 'Do you have evidence of funds to support yourself?', 'Kya aapke paas apne support ke liye funds ka proof hai?', 'Living cost verification', 2, 'Insufficient funds', 'Ask about sources'),
('IE', 'intent', 'What do you plan to do after your studies?', 'Padhai ke baad kya karenge?', 'Return intent', 3, 'Plans to stay', 'Ask about home career'),
('IE', 'country_specific', 'Are you aware of the immigration requirements for students in Ireland?', 'Kya aap Ireland ke student immigration requirements se waakif hain?', 'Compliance knowledge', 2, 'Not aware', 'Explain key requirements');

-- ============================================================
-- ITALY (IT)
-- ============================================================
INSERT INTO visa_questions (destination_country, category, question_text, question_text_hi, officer_objective, difficulty_level, common_failure_patterns, followup_rules) VALUES
('IT', 'academics', 'What is your educational background?', 'Aapki educational background kya hai?', 'Academic verification', 1, 'Vague details', 'Ask specifics'),
('IT', 'course_choice', 'Why did you choose Italy for your studies?', 'Italy kyun chuna?', 'Genuine intent', 2, 'Only tourism interest', 'Ask about program'),
('IT', 'finance', 'How will you support yourself financially in Italy?', 'Italy mein financially kaise support karenge?', 'Financial capacity', 2, 'Unclear funding', 'Ask for details'),
('IT', 'intent', 'What are your plans post-graduation?', 'Graduation ke baad kya plans hain?', 'Return intent', 3, 'Staying permanently', 'Ask about home plans'),
('IT', 'country_specific', 'Do you have accommodation arranged in Italy?', 'Kya Italy mein rehne ka intezaam hai?', 'Practical readiness', 1, 'No accommodation', 'Ask about plans'),
('IT', 'ties', 'What ties do you have to your home country?', 'Apne desh se kya ties hain?', 'Home ties', 2, 'Weak ties', 'Ask specifics');

-- ============================================================
-- SPAIN (ES)
-- ============================================================
INSERT INTO visa_questions (destination_country, category, question_text, question_text_hi, officer_objective, difficulty_level, common_failure_patterns, followup_rules) VALUES
('ES', 'academics', 'What are your academic credentials?', 'Aapki academic credentials kya hain?', 'Background check', 1, 'Incomplete info', 'Ask for details'),
('ES', 'course_choice', 'Why Spain for your education?', 'Spain kyun chuna padhai ke liye?', 'Genuine intent', 2, 'Cannot explain choice', 'Ask about program specifics'),
('ES', 'finance', 'How will you fund your stay in Spain?', 'Spain mein rehne ka kharcha kaise uthayenge?', 'Financial capacity', 2, 'No clear plan', 'Ask for financial proof'),
('ES', 'intent', 'What will you do after completing your course?', 'Course ke baad kya karenge?', 'Return intent', 3, 'Staying plans', 'Ask about home career'),
('ES', 'country_specific', 'Do you speak Spanish?', 'Kya aap Spanish bolte hain?', 'Language readiness', 2, 'No Spanish for Spanish-taught course', 'Ask about learning plans'),
('ES', 'ties', 'What motivates you to return home?', 'Ghar wapas jaane ki motivation kya hai?', 'Home ties', 2, 'Weak motivation', 'Ask about specifics');

-- ============================================================
-- SWITZERLAND (CH)
-- ============================================================
INSERT INTO visa_questions (destination_country, category, question_text, question_text_hi, officer_objective, difficulty_level, common_failure_patterns, followup_rules) VALUES
('CH', 'academics', 'What qualifications do you bring?', 'Aap kya qualifications laate hain?', 'Academic check', 1, 'Qualifications mismatch', 'Ask about relevance'),
('CH', 'course_choice', 'Why Switzerland for your studies?', 'Switzerland kyun chuna?', 'Genuine intent', 2, 'Only mentions reputation', 'Ask for specifics'),
('CH', 'finance', 'Can you prove financial self-sufficiency?', 'Kya aap financial self-sufficiency prove kar sakte hain?', 'Financial verification', 2, 'Insufficient proof', 'Ask about amounts'),
('CH', 'intent', 'What are your post-study plans?', 'Padhai ke baad kya plans hain?', 'Return intent', 3, 'Plans to remain', 'Ask about home career'),
('CH', 'country_specific', 'Which canton is your university in and are you aware of cantonal requirements?', 'Aapki university kis canton mein hai aur kya aap cantonal requirements se waakif hain?', 'Compliance knowledge', 2, 'Not aware', 'Explain cantonal process'),
('CH', 'ties', 'What connects you to your home country?', 'Aapko apne desh se kya jodta hai?', 'Home ties', 2, 'Weak connections', 'Ask specifics');

-- ============================================================
-- SWEDEN (SE)
-- ============================================================
INSERT INTO visa_questions (destination_country, category, question_text, question_text_hi, officer_objective, difficulty_level, common_failure_patterns, followup_rules) VALUES
('SE', 'academics', 'What is your academic background?', 'Aapki academic background kya hai?', 'Verification', 1, 'Gaps', 'Ask about gaps'),
('SE', 'course_choice', 'Why Sweden for your higher education?', 'Sweden kyun chuna higher education ke liye?', 'Genuine intent', 2, 'Generic reasons', 'Ask specifics'),
('SE', 'finance', 'Can you show proof of funds for tuition and living costs?', 'Kya aap tuition aur living costs ke funds dikha sakte hain?', 'Financial check', 2, 'Below threshold', 'Ask about sources'),
('SE', 'intent', 'What will you do after completing your studies?', 'Padhai ke baad kya karenge?', 'Return intent', 3, 'Stay plans', 'Ask home plans'),
('SE', 'country_specific', 'Have you paid your tuition fees to the Swedish university?', 'Kya aapne Swedish university ko tuition fees pay ki hain?', 'Commitment check', 1, 'Not paid', 'Ask about plan'),
('SE', 'ties', 'What will bring you back home?', 'Kya cheez aapko ghar wapas laayegi?', 'Home ties', 2, 'No strong ties', 'Ask specifics');

-- ============================================================
-- FINLAND (FI)
-- ============================================================
INSERT INTO visa_questions (destination_country, category, question_text, question_text_hi, officer_objective, difficulty_level, common_failure_patterns, followup_rules) VALUES
('FI', 'academics', 'What have you studied so far?', 'Ab tak kya padhai ki hai?', 'Academic check', 1, 'Vague', 'Ask details'),
('FI', 'course_choice', 'Why Finland for your studies?', 'Finland kyun chuna?', 'Genuine intent', 2, 'Cannot explain', 'Ask about program'),
('FI', 'finance', 'Do you have sufficient funds for your stay in Finland?', 'Kya aapke paas Finland mein rehne ke liye paisa hai?', 'Financial check', 2, 'Insufficient', 'Ask about sources'),
('FI', 'intent', 'What are your career plans after graduation?', 'Graduation ke baad career plans kya hain?', 'Return intent', 3, 'Staying plans', 'Home career question'),
('FI', 'country_specific', 'Are you aware of the residence permit requirements for students in Finland?', 'Kya aap Finland ke student residence permit requirements jaante hain?', 'Compliance', 2, 'Not aware', 'Explain'),
('FI', 'ties', 'What ties do you have to your home country?', 'Apne desh se kya ties hain?', 'Home ties', 2, 'Weak', 'Ask details');

-- ============================================================
-- NORWAY (NO)
-- ============================================================
INSERT INTO visa_questions (destination_country, category, question_text, question_text_hi, officer_objective, difficulty_level, common_failure_patterns, followup_rules) VALUES
('NO', 'academics', 'Tell me about your educational background.', 'Apni educational background ke baare mein bataiye.', 'Verification', 1, 'Gaps', 'Ask about gaps'),
('NO', 'course_choice', 'Why did you choose Norway?', 'Norway kyun chuna?', 'Genuine intent', 2, 'Free tuition only', 'Ask academic reasons'),
('NO', 'finance', 'Can you demonstrate NOK 137,000 or more for living costs per year?', 'Kya aap saal ka NOK 137,000 ya zyada dikha sakte hain?', 'Financial threshold', 2, 'Below threshold', 'Ask about plan'),
('NO', 'intent', 'What will you do after your program ends?', 'Program ke baad kya karenge?', 'Return intent', 3, 'Stay plans', 'Home plans'),
('NO', 'country_specific', 'Do you have accommodation arranged in Norway?', 'Kya Norway mein rehne ka intezaam hai?', 'Practical readiness', 1, 'No arrangement', 'Ask plans'),
('NO', 'ties', 'What connects you to your home country?', 'Apne desh se kya connection hai?', 'Home ties', 2, 'Weak', 'Ask details');

-- ============================================================
-- DENMARK (DK)
-- ============================================================
INSERT INTO visa_questions (destination_country, category, question_text, question_text_hi, officer_objective, difficulty_level, common_failure_patterns, followup_rules) VALUES
('DK', 'academics', 'What is your educational background?', 'Aapki educational background kya hai?', 'Verification', 1, 'Vague', 'Ask details'),
('DK', 'course_choice', 'Why Denmark for your studies?', 'Denmark kyun chuna?', 'Genuine intent', 2, 'Generic', 'Ask specifics'),
('DK', 'finance', 'Do you have sufficient funds for your stay?', 'Kya paisa hai rehne ke liye?', 'Financial check', 2, 'Insufficient', 'Ask sources'),
('DK', 'intent', 'What do you plan to do after graduation?', 'Graduation ke baad kya plan hai?', 'Return intent', 3, 'Stay plans', 'Home plans'),
('DK', 'country_specific', 'Are you aware of the Danish residence permit requirements?', 'Kya aap Danish residence permit requirements jaante hain?', 'Compliance', 2, 'Not aware', 'Explain'),
('DK', 'ties', 'What will bring you back to your home country?', 'Kya aapko wapas laayega?', 'Home ties', 2, 'Weak', 'Details');

-- ============================================================
-- JAPAN (JP)
-- ============================================================
INSERT INTO visa_questions (destination_country, category, question_text, question_text_hi, officer_objective, difficulty_level, common_failure_patterns, followup_rules) VALUES
('JP', 'academics', 'What is your educational background?', 'Aapki educational background kya hai?', 'Academic check', 1, 'Vague', 'Ask details'),
('JP', 'course_choice', 'Why Japan for your studies?', 'Japan kyun chuna?', 'Genuine intent', 2, 'Only anime/culture', 'Ask academic reasons'),
('JP', 'finance', 'Who is your financial sponsor?', 'Aapka financial sponsor kaun hai?', 'Sponsor verification', 2, 'Unclear sponsor', 'Ask details'),
('JP', 'finance', 'How will living expenses be covered?', 'Rehne ka kharcha kaise cover hoga?', 'Financial capacity', 2, 'Relies on part-time', 'Ask about sponsor support'),
('JP', 'intent', 'What will you do after your studies in Japan?', 'Japan mein padhai ke baad kya karenge?', 'Return intent', 3, 'Stay plans', 'Home plans'),
('JP', 'country_specific', 'Do you speak Japanese? What level?', 'Kya aap Japanese bolte hain? Kitni acchi?', 'Language readiness', 2, 'No Japanese', 'Ask about plans to learn'),
('JP', 'ties', 'What ties do you have at home?', 'Ghar mein kya ties hain?', 'Home ties', 2, 'Weak', 'Ask details');

-- ============================================================
-- SOUTH KOREA (KR)
-- ============================================================
INSERT INTO visa_questions (destination_country, category, question_text, question_text_hi, officer_objective, difficulty_level, common_failure_patterns, followup_rules) VALUES
('KR', 'academics', 'What have you studied previously?', 'Pehle kya padhai ki hai?', 'Academic check', 1, 'Vague', 'Ask details'),
('KR', 'course_choice', 'Why South Korea for higher education?', 'South Korea kyun chuna higher education ke liye?', 'Genuine intent', 2, 'Only K-culture', 'Ask academic reasons'),
('KR', 'finance', 'How will you fund your education in South Korea?', 'South Korea mein padhai ka kharcha kaise uthayenge?', 'Financial check', 2, 'Unclear', 'Ask sources'),
('KR', 'intent', 'What are your post-graduation plans?', 'Graduation ke baad plans kya hain?', 'Return intent', 3, 'Stay plans', 'Home plans'),
('KR', 'country_specific', 'Do you speak Korean?', 'Kya aap Korean bolte hain?', 'Language readiness', 2, 'No Korean for Korean-taught course', 'Ask about plans'),
('KR', 'ties', 'What will motivate you to return home?', 'Ghar wapas jaane ki motivation kya hai?', 'Home ties', 2, 'Weak', 'Details');

-- ============================================================
-- SINGAPORE (SG)
-- ============================================================
INSERT INTO visa_questions (destination_country, category, question_text, question_text_hi, officer_objective, difficulty_level, common_failure_patterns, followup_rules) VALUES
('SG', 'academics', 'What is your academic record?', 'Aapka academic record kya hai?', 'Verification', 1, 'Poor grades', 'Ask about improvement'),
('SG', 'course_choice', 'Why Singapore for your studies?', 'Singapore kyun chuna?', 'Genuine intent', 2, 'Generic reasons', 'Ask specifics'),
('SG', 'finance', 'How will you pay for your education and living in Singapore?', 'Singapore mein padhai aur rehne ka kharcha kaise denge?', 'Financial check', 2, 'Unclear sources', 'Ask details'),
('SG', 'intent', 'What do you plan to do after graduation?', 'Graduation ke baad kya plan hai?', 'Return intent', 3, 'Stay plans', 'Home career'),
('SG', 'country_specific', 'Is your institution approved by the Singapore government?', 'Kya aapki institution Singapore government se approved hai?', 'Legitimate institution', 1, 'Unapproved institution', 'Ask about institution status'),
('SG', 'ties', 'What are your ties to your home country?', 'Apne desh se kya ties hain?', 'Home ties', 2, 'Weak', 'Details');

-- ============================================================
-- NEW ZEALAND (NZ)
-- ============================================================
INSERT INTO visa_questions (destination_country, category, question_text, question_text_hi, officer_objective, difficulty_level, common_failure_patterns, followup_rules) VALUES
('NZ', 'academics', 'What is your educational background?', 'Aapki educational background kya hai?', 'Verification', 1, 'Gaps', 'Ask about gaps'),
('NZ', 'course_choice', 'Why New Zealand for your studies?', 'New Zealand kyun chuna?', 'Genuine intent', 2, 'Only mentions scenery', 'Ask academic reasons'),
('NZ', 'finance', 'Can you demonstrate sufficient funds?', 'Kya aap sufficient funds dikha sakte hain?', 'Financial check', 2, 'Below threshold', 'Ask sources'),
('NZ', 'intent', 'What are your plans after completing your studies?', 'Padhai ke baad kya plans hain?', 'Return intent', 3, 'Stay plans', 'Home plans'),
('NZ', 'country_specific', 'Do you meet the health and character requirements?', 'Kya aap health aur character requirements meet karte hain?', 'Compliance', 1, 'Unsure', 'Ask about medical exam'),
('NZ', 'ties', 'What connects you to your home country?', 'Apne desh se kya connection hai?', 'Home ties', 2, 'Weak', 'Details');

-- ============================================================
-- UNITED ARAB EMIRATES (AE)
-- ============================================================
INSERT INTO visa_questions (destination_country, category, question_text, question_text_hi, officer_objective, difficulty_level, common_failure_patterns, followup_rules) VALUES
('AE', 'academics', 'What have you studied so far?', 'Ab tak kya padhai ki hai?', 'Academic check', 1, 'Vague', 'Ask details'),
('AE', 'course_choice', 'Why the UAE for your studies?', 'UAE kyun chuna padhai ke liye?', 'Genuine intent', 2, 'Only mentions luxury', 'Ask academic reasons'),
('AE', 'finance', 'How will your studies be funded?', 'Padhai ka kharcha kaise hoga?', 'Financial check', 2, 'Unclear sources', 'Ask details'),
('AE', 'intent', 'What are your post-graduation plans?', 'Graduation ke baad plans kya hain?', 'Return intent', 3, 'Stay plans', 'Home plans'),
('AE', 'country_specific', 'Is your university licensed by the UAE Ministry of Education?', 'Kya aapki university UAE Ministry of Education se licensed hai?', 'Legitimate institution', 1, 'Not sure', 'Ask to verify'),
('AE', 'ties', 'What ties do you have at home?', 'Ghar mein kya ties hain?', 'Home ties', 2, 'Weak', 'Details');
