-- Risk factors by destination-origin country pairs
-- Scrutiny levels: 1 = standard, 2 = elevated, 3 = high

INSERT INTO risk_factors (destination_country, origin_country, risk_reason, scrutiny_level) VALUES
-- US risk factors
('US', 'India', 'High volume of applications, significant overstay rates in student category', 2),
('US', 'Pakistan', 'Elevated security screening, detailed financial verification required', 3),
('US', 'Bangladesh', 'Immigration intent concerns, strong financial scrutiny', 2),
('US', 'Nepal', 'High refusal rates, weak ties documentation common', 2),
('US', 'Nigeria', 'Elevated scrutiny, immigration intent assessment critical', 3),
('US', 'China', 'Large applicant pool, research field restrictions may apply', 2),
('US', 'Iran', 'Administrative processing likely, field of study restrictions', 3),
('US', 'Vietnam', 'Financial documentation scrutiny, return intent focus', 2),
('US', 'Philippines', 'Immigration intent concerns, family ties in US common', 2),
('US', 'Egypt', 'Elevated screening, academic credential verification', 2),

-- UK risk factors
('UK', 'India', 'High volume, genuine student test focus, financial scrutiny', 2),
('UK', 'Pakistan', 'Elevated scrutiny, strong ties verification needed', 3),
('UK', 'Bangladesh', 'Financial capacity concerns, credibility interviews common', 2),
('UK', 'Nigeria', 'High refusal rate, genuine student test critical', 3),
('UK', 'China', 'Large volume, generally lower risk but financial verification needed', 1),
('UK', 'Sri Lanka', 'Immigration intent concerns, work intent assessment', 2),

-- CA risk factors
('CA', 'India', 'Very high application volume, quality of DLI choice scrutinized', 2),
('CA', 'Pakistan', 'Financial verification, return intent focus', 3),
('CA', 'Bangladesh', 'High refusal rates, financial scrutiny', 3),
('CA', 'Nigeria', 'Strong scrutiny on finances and return intent', 3),
('CA', 'Nepal', 'Immigration intent concerns, GIC compliance check', 2),
('CA', 'Philippines', 'Family reunification risk, intent focus', 2),
('CA', 'Iran', 'Administrative delays, financial documentation', 2),

-- AU risk factors
('AU', 'India', 'GTE requirement focus, course-career relevance checked', 2),
('AU', 'Pakistan', 'Elevated GTE scrutiny, financial verification', 3),
('AU', 'Bangladesh', 'High refusal rates, GTE critical', 3),
('AU', 'Nepal', 'Immigration intent, GTE assessment focus', 2),
('AU', 'China', 'Large volume, generally favorable but GTE still checked', 1),
('AU', 'Nigeria', 'High scrutiny, GTE and financial proof critical', 3),
('AU', 'Vietnam', 'Moderate scrutiny, financial proof focus', 2),

-- DE risk factors
('DE', 'India', 'Blocked account compliance, credential recognition check', 2),
('DE', 'Pakistan', 'Elevated scrutiny, financial proof and intent', 2),
('DE', 'Bangladesh', 'Financial scrutiny, academic credential verification', 2),
('DE', 'Nigeria', 'High scrutiny, Anabin credential check critical', 3),
('DE', 'Iran', 'Administrative processing, field restrictions possible', 2),

-- FR risk factors
('FR', 'India', 'Campus France process compliance, academic project coherence', 2),
('FR', 'Morocco', 'High volume, genuine student intent focus', 2),
('FR', 'Algeria', 'Immigration intent scrutiny, financial verification', 2),
('FR', 'Senegal', 'Academic credential verification, financial proof', 2),
('FR', 'Tunisia', 'Return intent focus, campus France compliance', 2),

-- NL risk factors
('NL', 'India', 'Financial threshold verification, study plan coherence', 1),
('NL', 'Nigeria', 'Elevated scrutiny, financial proof', 3),

-- IE risk factors
('IE', 'India', 'Fee payment verification, financial self-sufficiency', 2),
('IE', 'Nigeria', 'High scrutiny, immigration intent', 3),
('IE', 'Pakistan', 'Financial verification, return intent', 2),

-- JP risk factors
('JP', 'India', 'Financial sponsor verification, study plan assessment', 1),
('JP', 'Nepal', 'High application volume, financial scrutiny', 2),
('JP', 'Bangladesh', 'Financial verification, sponsor legitimacy', 2),
('JP', 'Vietnam', 'Large student population, compliance history check', 2),

-- KR risk factors
('KR', 'India', 'Study plan assessment, financial check', 1),
('KR', 'Nepal', 'Immigration intent, financial verification', 2),
('KR', 'Vietnam', 'Large volume, compliance check', 1),

-- SG risk factors
('SG', 'India', 'Institution legitimacy check, financial verification', 1),
('SG', 'Bangladesh', 'Elevated scrutiny, financial proof', 2),

-- NZ risk factors
('NZ', 'India', 'Genuine intent, financial capacity, health requirements', 2),
('NZ', 'China', 'Financial verification, return intent', 1),
('NZ', 'Philippines', 'Immigration intent, family ties assessment', 2),

-- AE risk factors
('AE', 'India', 'Institution legitimacy, financial sponsor check', 1),
('AE', 'Pakistan', 'Financial verification, institution approval', 2),
('AE', 'Bangladesh', 'Financial scrutiny, institution legitimacy', 2);
