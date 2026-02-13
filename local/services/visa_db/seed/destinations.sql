-- Top 20 destination countries for student visas
INSERT INTO destinations (country_code, country_name, risk_profile_notes) VALUES
('US',  'United States',       'F-1 visa. Heavy scrutiny on intent to return, financial proof, ties to home country.'),
('UK',  'United Kingdom',      'Tier 4/Student visa. Focus on genuine student test, financial requirements, English proficiency.'),
('CA',  'Canada',              'Study permit. Emphasis on financial capacity, genuine intent, and ties to home country.'),
('AU',  'Australia',           'Student visa subclass 500. Genuine Temporary Entrant (GTE) requirement is key.'),
('DE',  'Germany',             'Student visa. Blocked account required. Focus on course relevance and language proficiency.'),
('FR',  'France',              'Student visa via Campus France. Focus on academic project coherence and financial means.'),
('NL',  'Netherlands',         'MVV + residence permit. Focus on admission, finances, and study plan.'),
('IE',  'Ireland',             'Study visa. Emphasis on course fees paid, financial proof, English ability.'),
('IT',  'Italy',               'Student visa. Focus on university admission, financial means, accommodation proof.'),
('ES',  'Spain',               'Student visa. Focus on admission letter, financial proof, health insurance.'),
('CH',  'Switzerland',         'Student visa. Cantonal approval needed. Strong emphasis on academic credentials.'),
('SE',  'Sweden',              'Residence permit for studies. Tuition + living costs must be proven upfront.'),
('FI',  'Finland',             'Residence permit. Focus on financial self-sufficiency and genuine study intent.'),
('NO',  'Norway',              'Student residence permit. Must prove NOK 137,000+ per year for living costs.'),
('DK',  'Denmark',             'Residence permit for studies. Focus on admission, finances, English proficiency.'),
('JP',  'Japan',               'Student visa (College Student status). Focus on financial sponsor, study plan, Japanese ability.'),
('KR',  'South Korea',         'D-2 visa. Focus on admission, financial proof, study plan.'),
('SG',  'Singapore',           'Student Pass. Focus on institution approval, financial means, academic record.'),
('NZ',  'New Zealand',         'Student visa. Genuine intent, financial proof, health and character requirements.'),
('AE',  'United Arab Emirates','Student visa. University sponsorship required. Focus on admission and financial proof.')
ON CONFLICT (country_code) DO NOTHING;
