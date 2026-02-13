-- Follow-up questions linked to parent questions
-- These trigger based on weak, vague, or incomplete answers

-- US followups (parent IDs will be 1-12 based on insertion order)
INSERT INTO followups (parent_question_id, trigger_condition, followup_question, followup_question_hi) VALUES
(1, 'vague_answer', 'Can you name the exact institution and degree you completed?', 'Kya aap apni exact institution aur degree ka naam bata sakte hain?'),
(2, 'low_score', 'How do you explain your academic performance?', 'Aap apni academic performance ko kaise explain karenge?'),
(3, 'generic_answer', 'What specific features of this program attracted you?', 'Is program ki kaunsi khaas baat aapko attract karti hai?'),
(4, 'weak_connection', 'If your background is different, why switch fields now?', 'Agar aapka background alag hai, toh ab field kyun badal rahe hain?'),
(5, 'unclear_funding', 'Can you provide specific amounts and sources of funding?', 'Kya aap funding ki specific amount aur source bata sakte hain?'),
(6, 'vague_sponsor', 'What documentation do you have for your sponsor''s income?', 'Aapke sponsor ki income ke liye kya documentation hai?'),
(7, 'mentions_staying', 'What specific career opportunities await you back home?', 'Ghar wapas jaane par kaunse career opportunities hain?'),
(8, 'cannot_explain', 'Are there comparable programs in your home country?', 'Kya aapke desh mein comparable programs hain?'),
(9, 'has_family_in_us', 'What is the nature of your relationship with them?', 'Unse aapka rishta kaisa hai?'),
(10, 'weak_ties', 'Do you own property or have a job offer back home?', 'Kya aapki property hai ya ghar mein job offer hai?'),
(11, 'previous_travel', 'What visa type did you hold and for how long?', 'Aapke paas kaunsa visa tha aur kitne samay ke liye?'),
(12, 'scripted_response', 'Can you tell me a specific moment that influenced your career choice?', 'Koi specific moment bataiye jisne aapki career choice ko influence kiya?'),

-- UK followups (parent IDs 13-22)
(13, 'vague_answer', 'Which institution granted your qualification?', 'Kaunsi institution ne aapko qualification di?'),
(14, 'generic_reason', 'What does the UK offer that your home country cannot?', 'UK aapko kya de sakta hai jo aapka desh nahi de sakta?'),
(15, 'no_research', 'Can you name any modules or professors in your chosen program?', 'Kya aap apne program ke modules ya professors ka naam bata sakte hain?'),
(16, 'unclear_funding', 'Where exactly are the funds currently held?', 'Funds exactly kahan hain abhi?'),
(17, 'recent_deposit', 'Why were the funds deposited recently?', 'Funds recently kyun deposit kiye gaye?'),
(18, 'staying_plans', 'Are you aware of the Graduate Route visa terms?', 'Kya aap Graduate Route visa ke terms jaante hain?'),
(19, 'many_contacts', 'How often do you visit them?', 'Aap unse kitni baar milte hain?'),

-- CA followups (parent IDs 23-32)
(23, 'gaps_in_education', 'Can you explain the gaps in your educational timeline?', 'Apni padhai ki timeline mein gaps explain kar sakte hain?'),
(24, 'immigration_focus', 'Setting aside immigration, what academic benefit does Canada offer?', 'Immigration chhodke, Canada academically kya benefit deta hai?'),
(25, 'no_research', 'What makes this DLI different from other institutions?', 'Yeh DLI doosri institutions se kaise alag hai?'),
(26, 'relies_on_work', 'What if you cannot find part-time work?', 'Agar part-time kaam nahi mila toh?'),
(28, 'pr_focused', 'What specific career opportunities exist for you at home?', 'Ghar mein aapke liye kaunse specific career opportunities hain?'),

-- AU followups (parent IDs 33-42)
(33, 'inconsistent_dates', 'Can you clarify the timeline of your education?', 'Apni padhai ki timeline clear kar sakte hain?'),
(34, 'work_rights_focus', 'What academic advantages does Australia offer specifically?', 'Australia specifically kya academic advantages deta hai?'),
(35, 'no_career_plan', 'What is the job market like for this field in your home country?', 'Aapke desh mein is field ka job market kaisa hai?'),
(37, 'evasive', 'Let me ask directly — do you plan to return or stay?', 'Seedha poochta hoon — kya aap wapas jaayenge ya rahenge?'),

-- DE followups (parent IDs 43-52)
(43, 'unrecognized', 'Have you had your credentials evaluated by anabin or uni-assist?', 'Kya aapne credentials anabin ya uni-assist se evaluate karaaye hain?'),
(44, 'free_tuition_only', 'Beyond cost, what does Germany offer academically?', 'Cost ke alaawa, Germany academically kya offer karta hai?'),
(46, 'no_blocked_account', 'How do you plan to meet the financial requirement then?', 'Phir financial requirement kaise meet karenge?');
