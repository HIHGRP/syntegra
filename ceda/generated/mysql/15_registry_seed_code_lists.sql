-- Jurisdiction code lists — generated from ceda/model/reference/*.yaml. DO NOT EDIT.
-- Load after 10_registry.sql. tenant_id is the state tenant; replace @tenant before loading.
SET NAMES utf8mb4;
SET @tenant = UUID_TO_BIN('00000000-0000-7000-8000-000000000001');

-- education_level: Education levels and grades (Nigeria)
INSERT INTO `code_list` (`id`, `tenant_id`, `code`, `title`, `pack`, `is_extensible`) VALUES (UUID_TO_BIN(UUID()), @tenant, 'education_level', 'Education levels and grades (Nigeria)', 'ng-core', FALSE);
INSERT INTO `code_value` (`id`, `tenant_id`, `code_list_id`, `code`, `label`, `sort_order`, `valid_from`) VALUES
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'education_level'), 'ECCDE', 'Early childhood care (ECCDE', 1, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'education_level'), 'KG', 'Kindergarten / Nursery', 2, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'education_level'), 'PRY1', 'Primary 1', 3, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'education_level'), 'PRY2', 'Primary 2', 4, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'education_level'), 'PRY3', 'Primary 3', 5, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'education_level'), 'PRY4', 'Primary 4', 6, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'education_level'), 'PRY5', 'Primary 5', 7, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'education_level'), 'PRY6', 'Primary 6', 8, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'education_level'), 'JSS1', 'Junior Secondary 1', 9, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'education_level'), 'JSS2', 'Junior Secondary 2', 10, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'education_level'), 'JSS3', 'Junior Secondary 3', 11, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'education_level'), 'SSS1', 'Senior Secondary 1', 12, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'education_level'), 'SSS2', 'Senior Secondary 2', 13, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'education_level'), 'SSS3', 'Senior Secondary 3', 14, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'education_level'), 'NTC', 'Technical college (NTC/NBC)', 15, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'education_level'), 'NCE', 'College of education (NCE)', 16, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'education_level'), 'ND', 'Polytechnic National Diploma', 17, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'education_level'), 'HND', 'Polytechnic Higher National Diploma', 18, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'education_level'), 'UG100', 'University 100 level', 19, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'education_level'), 'UG200', 'University 200 level', 20, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'education_level'), 'UG300', 'University 300 level', 21, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'education_level'), 'UG400', 'University 400 level', 22, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'education_level'), 'UG500', 'University 500 level', 23, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'education_level'), 'UG600', 'University 600 level', 24, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'education_level'), 'UG700', 'University 700 level', 25, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'education_level'), 'PG', 'Postgraduate', 26, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'education_level'), 'NURSING', 'Nursing and midwifery', 27, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'education_level'), 'HEALTH_TECH', 'Health technology', 28, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'education_level'), 'ADULT', 'Adult and non-formal education', 29, '2026-01-01');

-- institution_category: Institution categories
INSERT INTO `code_list` (`id`, `tenant_id`, `code`, `title`, `pack`, `is_extensible`) VALUES (UUID_TO_BIN(UUID()), @tenant, 'institution_category', 'Institution categories', 'ng-core', FALSE);
INSERT INTO `code_value` (`id`, `tenant_id`, `code_list_id`, `code`, `label`, `sort_order`, `valid_from`) VALUES
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'institution_category'), 'eccde_centre', 'Eccde centre', 1, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'institution_category'), 'nursery_primary', 'Nursery primary', 2, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'institution_category'), 'primary', 'Primary', 3, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'institution_category'), 'junior_secondary', 'Junior secondary', 4, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'institution_category'), 'senior_secondary', 'Senior secondary', 5, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'institution_category'), 'combined_secondary', 'Combined secondary', 6, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'institution_category'), 'technical_college', 'Technical college', 7, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'institution_category'), 'college_of_education', 'College of education', 8, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'institution_category'), 'polytechnic', 'Polytechnic', 9, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'institution_category'), 'monotechnic', 'Monotechnic', 10, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'institution_category'), 'university', 'University', 11, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'institution_category'), 'school_of_nursing', 'School of nursing', 12, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'institution_category'), 'school_of_health_technology', 'School of health technology', 13, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'institution_category'), 'special_school', 'Special school', 14, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'institution_category'), 'non_formal_centre', 'Non formal centre', 15, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'institution_category'), 'tutorial_centre', 'Tutorial centre', 16, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'institution_category'), 'international_school', 'International school', 17, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'institution_category'), 'military_academy', 'Military academy', 18, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'institution_category'), 'police_academy', 'Police academy', 19, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'institution_category'), 'paramilitary_academy', 'Paramilitary academy', 20, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'institution_category'), 'defence_university', 'Defence university', 21, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'institution_category'), 'staff_college', 'Staff college', 22, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'institution_category'), 'defence_college', 'Defence college', 23, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'institution_category'), 'security_training_school', 'Security training school', 24, '2026-01-01');

-- ownership: Ownership
INSERT INTO `code_list` (`id`, `tenant_id`, `code`, `title`, `pack`, `is_extensible`) VALUES (UUID_TO_BIN(UUID()), @tenant, 'ownership', 'Ownership', 'ng-core', FALSE);
INSERT INTO `code_value` (`id`, `tenant_id`, `code_list_id`, `code`, `label`, `sort_order`, `valid_from`) VALUES
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'ownership'), 'federal', 'Federal', 1, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'ownership'), 'state', 'State', 2, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'ownership'), 'lga', 'Lga', 3, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'ownership'), 'private', 'Private', 4, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'ownership'), 'faith', 'Faith', 5, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'ownership'), 'community', 'Community', 6, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'ownership'), 'ngo', 'Ngo', 7, '2026-01-01');

-- sex: Sex (as recorded on identity documents)
INSERT INTO `code_list` (`id`, `tenant_id`, `code`, `title`, `pack`, `is_extensible`) VALUES (UUID_TO_BIN(UUID()), @tenant, 'sex', 'Sex (as recorded on identity documents)', 'ng-core', FALSE);
INSERT INTO `code_value` (`id`, `tenant_id`, `code_list_id`, `code`, `label`, `sort_order`, `valid_from`) VALUES
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'sex'), 'female', 'Female', 1, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'sex'), 'male', 'Male', 2, '2026-01-01');

-- language: Languages
INSERT INTO `code_list` (`id`, `tenant_id`, `code`, `title`, `pack`, `is_extensible`) VALUES (UUID_TO_BIN(UUID()), @tenant, 'language', 'Languages', 'ng-core', TRUE);
INSERT INTO `code_value` (`id`, `tenant_id`, `code_list_id`, `code`, `label`, `sort_order`, `valid_from`) VALUES
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'language'), 'en', 'En', 1, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'language'), 'ha', 'Ha', 2, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'language'), 'ig', 'Ig', 3, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'language'), 'yo', 'Yo', 4, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'language'), 'ibb', 'Ibb', 5, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'language'), 'ff', 'Ff', 6, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'language'), 'kr', 'Kr', 7, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'language'), 'tiv', 'Tiv', 8, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'language'), 'efi', 'Efi', 9, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'language'), 'pcm', 'Pcm', 10, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'language'), 'ar', 'Ar', 11, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'language'), 'fr', 'Fr', 12, '2026-01-01');

-- identifier_scheme: External identifier schemes
INSERT INTO `code_list` (`id`, `tenant_id`, `code`, `title`, `pack`, `is_extensible`) VALUES (UUID_TO_BIN(UUID()), @tenant, 'identifier_scheme', 'External identifier schemes', 'ng-core', TRUE);
INSERT INTO `code_value` (`id`, `tenant_id`, `code_list_id`, `code`, `label`, `sort_order`, `valid_from`) VALUES
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'identifier_scheme'), 'NG-NIN', 'Ng-nin', 1, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'identifier_scheme'), 'WAEC-CAND', 'Waec-cand', 2, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'identifier_scheme'), 'NECO-CAND', 'Neco-cand', 3, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'identifier_scheme'), 'NABTEB-CAND', 'Nabteb-cand', 4, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'identifier_scheme'), 'JAMB-REG', 'Jamb-reg', 5, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'identifier_scheme'), 'BECE-CAND', 'Bece-cand', 6, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'identifier_scheme'), 'TRCN', 'Trcn', 7, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'identifier_scheme'), 'MDCN', 'Mdcn', 8, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'identifier_scheme'), 'NMCN', 'Nmcn', 9, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'identifier_scheme'), 'CAC-RC', 'Cac-rc', 10, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'identifier_scheme'), 'TIN', 'Tin', 11, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'identifier_scheme'), 'UPN', 'Upn', 12, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'identifier_scheme'), 'INST-ID', 'Inst-id', 13, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'identifier_scheme'), 'PREV-LRN-ID', 'Prev-lrn-id', 14, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'identifier_scheme'), 'NG-BVN', 'Ng-bvn', 15, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'identifier_scheme'), 'PENCOM-RSA', 'Pencom-rsa', 16, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'identifier_scheme'), 'NHF', 'Nhf', 17, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'identifier_scheme'), 'IPPIS', 'Ippis', 18, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'identifier_scheme'), 'SVC-NO', 'Service number', 19, '2026-01-01');

-- regulator: Regulators, examination and awarding bodies
INSERT INTO `code_list` (`id`, `tenant_id`, `code`, `title`, `pack`, `is_extensible`) VALUES (UUID_TO_BIN(UUID()), @tenant, 'regulator', 'Regulators, examination and awarding bodies', 'ng-core', TRUE);
INSERT INTO `code_value` (`id`, `tenant_id`, `code_list_id`, `code`, `label`, `sort_order`, `valid_from`) VALUES
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'regulator'), 'FME', 'Fme', 1, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'regulator'), 'STATE_MOE', 'State moe', 2, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'regulator'), 'SUBEB', 'Subeb', 3, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'regulator'), 'UBEC', 'Ubec', 4, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'regulator'), 'NERDC', 'Nerdc', 5, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'regulator'), 'NBTE', 'Nbte', 6, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'regulator'), 'NCCE', 'Ncce', 7, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'regulator'), 'NUC', 'Nuc', 8, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'regulator'), 'TRCN', 'Trcn', 9, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'regulator'), 'MDCN', 'Mdcn', 10, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'regulator'), 'NMCN', 'Nmcn', 11, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'regulator'), 'PCN', 'Pcn', 12, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'regulator'), 'MRTB', 'Mrtb', 13, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'regulator'), 'RRBN', 'Rrbn', 14, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'regulator'), 'MLSCN', 'Mlscn', 15, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'regulator'), 'CHPRBN', 'Chprbn', 16, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'regulator'), 'WAEC', 'Waec', 17, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'regulator'), 'NECO', 'Neco', 18, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'regulator'), 'NABTEB', 'Nabteb', 19, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'regulator'), 'NBAIS', 'Nbais', 20, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'regulator'), 'JAMB', 'Jamb', 21, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'regulator'), 'STATE_EXAM_BOARD', 'State exam board', 22, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'regulator'), 'INSTITUTION_SENATE', 'Institution senate', 23, '2026-01-01');

-- exam_body: Examination bodies
INSERT INTO `code_list` (`id`, `tenant_id`, `code`, `title`, `pack`, `is_extensible`) VALUES (UUID_TO_BIN(UUID()), @tenant, 'exam_body', 'Examination bodies', 'ng-core', FALSE);
INSERT INTO `code_value` (`id`, `tenant_id`, `code_list_id`, `code`, `label`, `sort_order`, `valid_from`) VALUES
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'exam_body'), 'WAEC', 'Waec', 1, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'exam_body'), 'NECO', 'Neco', 2, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'exam_body'), 'NABTEB', 'Nabteb', 3, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'exam_body'), 'NBAIS', 'Nbais', 4, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'exam_body'), 'JAMB', 'Jamb', 5, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'exam_body'), 'STATE_BECE', 'State bece', 6, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'exam_body'), 'INSTITUTION', 'Institution', 7, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'exam_body'), 'CAMBRIDGE', 'Cambridge', 8, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'exam_body'), 'IB', 'Ib', 9, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'exam_body'), 'PEARSON', 'Pearson', 10, '2026-01-01');

-- attendance_code: Attendance codes (Book 3 §7.2)
INSERT INTO `code_list` (`id`, `tenant_id`, `code`, `title`, `pack`, `is_extensible`) VALUES (UUID_TO_BIN(UUID()), @tenant, 'attendance_code', 'Attendance codes (Book 3 §7.2)', 'ng-core', FALSE);
INSERT INTO `code_value` (`id`, `tenant_id`, `code_list_id`, `code`, `label`, `sort_order`, `valid_from`) VALUES
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'attendance_code'), 'P', 'Present', 1, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'attendance_code'), 'L', 'Late', 2, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'attendance_code'), 'A', 'Absent (unauthorised)', 3, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'attendance_code'), 'M', 'Medical', 4, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'attendance_code'), 'E', 'Excused', 5, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'attendance_code'), 'AA', 'Approved activity', 6, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'attendance_code'), 'NR', 'Not required', 7, '2026-01-01');

-- absence_reason: Absence reasons reported by parents
INSERT INTO `code_list` (`id`, `tenant_id`, `code`, `title`, `pack`, `is_extensible`) VALUES (UUID_TO_BIN(UUID()), @tenant, 'absence_reason', 'Absence reasons reported by parents', 'ng-core', TRUE);
INSERT INTO `code_value` (`id`, `tenant_id`, `code_list_id`, `code`, `label`, `sort_order`, `valid_from`) VALUES
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'absence_reason'), 'illness', 'Illness', 1, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'absence_reason'), 'medical_appointment', 'Medical appointment', 2, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'absence_reason'), 'family_emergency', 'Family emergency', 3, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'absence_reason'), 'religious_observance', 'Religious observance', 4, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'absence_reason'), 'transport', 'Transport', 5, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'absence_reason'), 'insecurity', 'Insecurity', 6, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'absence_reason'), 'weather_flooding', 'Weather flooding', 7, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'absence_reason'), 'other', 'Other', 8, '2026-01-01');

-- absence_type: Staff absence types
INSERT INTO `code_list` (`id`, `tenant_id`, `code`, `title`, `pack`, `is_extensible`) VALUES (UUID_TO_BIN(UUID()), @tenant, 'absence_type', 'Staff absence types', 'ng-core', FALSE);
INSERT INTO `code_value` (`id`, `tenant_id`, `code_list_id`, `code`, `label`, `sort_order`, `valid_from`) VALUES
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'absence_type'), 'sick', 'Sick', 1, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'absence_type'), 'annual_leave', 'Annual leave', 2, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'absence_type'), 'maternity', 'Maternity', 3, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'absence_type'), 'paternity', 'Paternity', 4, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'absence_type'), 'study', 'Study', 5, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'absence_type'), 'training', 'Training', 6, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'absence_type'), 'official_duty', 'Official duty', 7, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'absence_type'), 'compassionate', 'Compassionate', 8, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'absence_type'), 'unauthorised', 'Unauthorised', 9, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'absence_type'), 'casual', 'Casual', 10, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'absence_type'), 'examination', 'Examination', 11, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'absence_type'), 'sabbatical', 'Sabbatical', 12, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'absence_type'), 'leave_of_absence', 'Leave of absence', 13, '2026-01-01');

-- leaving_reason: Leaving reasons
INSERT INTO `code_list` (`id`, `tenant_id`, `code`, `title`, `pack`, `is_extensible`) VALUES (UUID_TO_BIN(UUID()), @tenant, 'leaving_reason', 'Leaving reasons', 'ng-core', FALSE);
INSERT INTO `code_value` (`id`, `tenant_id`, `code_list_id`, `code`, `label`, `sort_order`, `valid_from`) VALUES
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'leaving_reason'), 'completed_level', 'Completed level', 1, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'leaving_reason'), 'transferred', 'Transferred', 2, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'leaving_reason'), 'relocated', 'Relocated', 3, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'leaving_reason'), 'financial', 'Financial', 4, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'leaving_reason'), 'dropped_out', 'Dropped out', 5, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'leaving_reason'), 'deceased', 'Deceased', 6, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'leaving_reason'), 'excluded', 'Excluded', 7, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'leaving_reason'), 'unknown', 'Unknown', 8, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'leaving_reason'), 'employment', 'Employment', 9, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'leaving_reason'), 'marriage', 'Marriage', 10, '2026-01-01');

-- relationship: Learner–guardian relationship
INSERT INTO `code_list` (`id`, `tenant_id`, `code`, `title`, `pack`, `is_extensible`) VALUES (UUID_TO_BIN(UUID()), @tenant, 'relationship', 'Learner–guardian relationship', 'ng-core', FALSE);
INSERT INTO `code_value` (`id`, `tenant_id`, `code_list_id`, `code`, `label`, `sort_order`, `valid_from`) VALUES
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'relationship'), 'mother', 'Mother', 1, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'relationship'), 'father', 'Father', 2, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'relationship'), 'step_parent', 'Step parent', 3, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'relationship'), 'grandparent', 'Grandparent', 4, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'relationship'), 'aunt_uncle', 'Aunt uncle', 5, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'relationship'), 'sibling', 'Sibling', 6, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'relationship'), 'legal_guardian', 'Legal guardian', 7, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'relationship'), 'foster_carer', 'Foster carer', 8, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'relationship'), 'social_worker', 'Social worker', 9, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'relationship'), 'sponsor', 'Sponsor', 10, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'relationship'), 'other', 'Other', 11, '2026-01-01');

-- consent_type: Consent types (FR-FAM-05)
INSERT INTO `code_list` (`id`, `tenant_id`, `code`, `title`, `pack`, `is_extensible`) VALUES (UUID_TO_BIN(UUID()), @tenant, 'consent_type', 'Consent types (FR-FAM-05)', 'ng-core', FALSE);
INSERT INTO `code_value` (`id`, `tenant_id`, `code_list_id`, `code`, `label`, `sort_order`, `valid_from`) VALUES
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'consent_type'), 'photography', 'Photography', 1, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'consent_type'), 'trips', 'Trips', 2, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'consent_type'), 'data_sharing', 'Data sharing', 3, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'consent_type'), 'medical', 'Medical', 4, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'consent_type'), 'biometrics', 'Biometrics', 5, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'consent_type'), 'digital_services', 'Digital services', 6, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'consent_type'), 'video_recording', 'Video recording', 7, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'consent_type'), 'marketing', 'Marketing', 8, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'consent_type'), 'facial_match', 'Facial match', 9, '2026-01-01');

-- stream: Senior secondary streams
INSERT INTO `code_list` (`id`, `tenant_id`, `code`, `title`, `pack`, `is_extensible`) VALUES (UUID_TO_BIN(UUID()), @tenant, 'stream', 'Senior secondary streams', 'ng-core', FALSE);
INSERT INTO `code_value` (`id`, `tenant_id`, `code_list_id`, `code`, `label`, `sort_order`, `valid_from`) VALUES
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'stream'), 'science', 'Science', 1, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'stream'), 'arts', 'Arts', 2, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'stream'), 'commercial', 'Commercial', 3, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'stream'), 'technical', 'Technical', 4, '2026-01-01');

-- subject_group: Subject groups
INSERT INTO `code_list` (`id`, `tenant_id`, `code`, `title`, `pack`, `is_extensible`) VALUES (UUID_TO_BIN(UUID()), @tenant, 'subject_group', 'Subject groups', 'ng-core', FALSE);
INSERT INTO `code_value` (`id`, `tenant_id`, `code_list_id`, `code`, `label`, `sort_order`, `valid_from`) VALUES
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'subject_group'), 'core', 'Core', 1, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'subject_group'), 'science', 'Science', 2, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'subject_group'), 'arts', 'Arts', 3, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'subject_group'), 'commercial', 'Commercial', 4, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'subject_group'), 'technical', 'Technical', 5, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'subject_group'), 'vocational', 'Vocational', 6, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'subject_group'), 'language', 'Language', 7, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'subject_group'), 'religious', 'Religious', 8, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'subject_group'), 'creative', 'Creative', 9, '2026-01-01');

-- room_type: Room types
INSERT INTO `code_list` (`id`, `tenant_id`, `code`, `title`, `pack`, `is_extensible`) VALUES (UUID_TO_BIN(UUID()), @tenant, 'room_type', 'Room types', 'ng-core', FALSE);
INSERT INTO `code_value` (`id`, `tenant_id`, `code_list_id`, `code`, `label`, `sort_order`, `valid_from`) VALUES
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'room_type'), 'classroom', 'Classroom', 1, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'room_type'), 'laboratory', 'Laboratory', 2, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'room_type'), 'workshop', 'Workshop', 3, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'room_type'), 'ict_suite', 'Ict suite', 4, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'room_type'), 'library', 'Library', 5, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'room_type'), 'hall', 'Hall', 6, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'room_type'), 'sports', 'Sports', 7, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'room_type'), 'office', 'Office', 8, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'room_type'), 'hostel_room', 'Hostel room', 9, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'room_type'), 'skills_lab', 'Skills lab', 10, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'room_type'), 'clinic', 'Clinic', 11, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'room_type'), 'store', 'Store', 12, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'room_type'), 'toilet', 'Toilet', 13, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'room_type'), 'kitchen_dining', 'Kitchen dining', 14, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'room_type'), 'staff_room', 'Staff room', 15, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'room_type'), 'staff_quarters', 'Staff quarters', 16, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'room_type'), 'nursery_play', 'Nursery play', 17, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'room_type'), 'chapel_mosque', 'Chapel mosque', 18, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'room_type'), 'guard_house', 'Guard house', 19, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'room_type'), 'generator_house', 'Generator house', 20, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'room_type'), 'water_point', 'Water point', 21, '2026-01-01');

-- condition_grade: Condition grades
INSERT INTO `code_list` (`id`, `tenant_id`, `code`, `title`, `pack`, `is_extensible`) VALUES (UUID_TO_BIN(UUID()), @tenant, 'condition_grade', 'Condition grades', 'ng-core', FALSE);
INSERT INTO `code_value` (`id`, `tenant_id`, `code_list_id`, `code`, `label`, `sort_order`, `valid_from`) VALUES
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'condition_grade'), 'good', 'Good', 1, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'condition_grade'), 'fair', 'Fair', 2, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'condition_grade'), 'poor', 'Poor', 3, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'condition_grade'), 'unsafe', 'Unsafe', 4, '2026-01-01');

-- asset_category: Asset categories
INSERT INTO `code_list` (`id`, `tenant_id`, `code`, `title`, `pack`, `is_extensible`) VALUES (UUID_TO_BIN(UUID()), @tenant, 'asset_category', 'Asset categories', 'ng-core', FALSE);
INSERT INTO `code_value` (`id`, `tenant_id`, `code_list_id`, `code`, `label`, `sort_order`, `valid_from`) VALUES
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'asset_category'), 'ict_device', 'Ict device', 1, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'asset_category'), 'furniture', 'Furniture', 2, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'asset_category'), 'lab_equipment', 'Lab equipment', 3, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'asset_category'), 'workshop_equipment', 'Workshop equipment', 4, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'asset_category'), 'vehicle', 'Vehicle', 5, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'asset_category'), 'generator', 'Generator', 6, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'asset_category'), 'water_system', 'Water system', 7, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'asset_category'), 'sports_equipment', 'Sports equipment', 8, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'asset_category'), 'other', 'Other', 9, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'asset_category'), 'solar_system', 'Solar system', 10, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'asset_category'), 'transformer', 'Transformer', 11, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'asset_category'), 'borehole', 'Borehole', 12, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'asset_category'), 'fire_safety_equipment', 'Fire safety equipment', 13, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'asset_category'), 'security_system', 'Security system', 14, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'asset_category'), 'kitchen_equipment', 'Kitchen equipment', 15, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'asset_category'), 'medical_equipment', 'Medical equipment', 16, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'asset_category'), 'playground_equipment', 'Playground equipment', 17, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'asset_category'), 'musical_instrument', 'Musical instrument', 18, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'asset_category'), 'office_equipment', 'Office equipment', 19, '2026-01-01');

-- staff_category: Staff categories
INSERT INTO `code_list` (`id`, `tenant_id`, `code`, `title`, `pack`, `is_extensible`) VALUES (UUID_TO_BIN(UUID()), @tenant, 'staff_category', 'Staff categories', 'ng-core', FALSE);
INSERT INTO `code_value` (`id`, `tenant_id`, `code_list_id`, `code`, `label`, `sort_order`, `valid_from`) VALUES
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'staff_category'), 'teaching', 'Teaching', 1, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'staff_category'), 'non_teaching', 'Non teaching', 2, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'staff_category'), 'lecturer', 'Lecturer', 3, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'staff_category'), 'graduate_assistant', 'Graduate assistant', 4, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'staff_category'), 'technician', 'Technician', 5, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'staff_category'), 'administrative', 'Administrative', 6, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'staff_category'), 'support', 'Support', 7, '2026-01-01');

-- academic_rank: Academic ranks (load policy)
INSERT INTO `code_list` (`id`, `tenant_id`, `code`, `title`, `pack`, `is_extensible`) VALUES (UUID_TO_BIN(UUID()), @tenant, 'academic_rank', 'Academic ranks (load policy)', 'ng-core', FALSE);
INSERT INTO `code_value` (`id`, `tenant_id`, `code_list_id`, `code`, `label`, `sort_order`, `valid_from`) VALUES
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'academic_rank'), 'professor', 'Professor', 1, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'academic_rank'), 'reader', 'Reader', 2, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'academic_rank'), 'senior_lecturer', 'Senior lecturer', 3, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'academic_rank'), 'lecturer_i', 'Lecturer i', 4, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'academic_rank'), 'lecturer_ii', 'Lecturer ii', 5, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'academic_rank'), 'assistant_lecturer', 'Assistant lecturer', 6, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'academic_rank'), 'graduate_assistant', 'Graduate assistant', 7, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'academic_rank'), 'chief_lecturer', 'Chief lecturer', 8, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'academic_rank'), 'principal_lecturer', 'Principal lecturer', 9, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'academic_rank'), 'lecturer_iii', 'Lecturer iii', 10, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'academic_rank'), 'instructor', 'Instructor', 11, '2026-01-01');

-- appraisal_rating: Appraisal ratings
INSERT INTO `code_list` (`id`, `tenant_id`, `code`, `title`, `pack`, `is_extensible`) VALUES (UUID_TO_BIN(UUID()), @tenant, 'appraisal_rating', 'Appraisal ratings', 'ng-core', FALSE);
INSERT INTO `code_value` (`id`, `tenant_id`, `code_list_id`, `code`, `label`, `sort_order`, `valid_from`) VALUES
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'appraisal_rating'), 'outstanding', 'Outstanding', 1, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'appraisal_rating'), 'very_good', 'Very good', 2, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'appraisal_rating'), 'good', 'Good', 3, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'appraisal_rating'), 'fair', 'Fair', 4, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'appraisal_rating'), 'poor', 'Poor', 5, '2026-01-01');

-- cpd_kind: CPD kinds
INSERT INTO `code_list` (`id`, `tenant_id`, `code`, `title`, `pack`, `is_extensible`) VALUES (UUID_TO_BIN(UUID()), @tenant, 'cpd_kind', 'CPD kinds', 'ng-core', FALSE);
INSERT INTO `code_value` (`id`, `tenant_id`, `code_list_id`, `code`, `label`, `sort_order`, `valid_from`) VALUES
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'cpd_kind'), 'course', 'Course', 1, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'cpd_kind'), 'workshop', 'Workshop', 2, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'cpd_kind'), 'conference', 'Conference', 3, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'cpd_kind'), 'lms_training', 'Lms training', 4, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'cpd_kind'), 'digital_practice', 'Digital practice', 5, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'cpd_kind'), 'mentoring', 'Mentoring', 6, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'cpd_kind'), 'qualification', 'Qualification', 7, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'cpd_kind'), 'statutory_training', 'Statutory training', 8, '2026-01-01');

-- training_topic: Statutory training topics (MFS §18.10)
INSERT INTO `code_list` (`id`, `tenant_id`, `code`, `title`, `pack`, `is_extensible`) VALUES (UUID_TO_BIN(UUID()), @tenant, 'training_topic', 'Statutory training topics (MFS §18.10)', 'ng-core', FALSE);
INSERT INTO `code_value` (`id`, `tenant_id`, `code_list_id`, `code`, `label`, `sort_order`, `valid_from`) VALUES
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'training_topic'), 'child_protection', 'Child protection', 1, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'training_topic'), 'safe_schools', 'Safe schools', 2, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'training_topic'), 'first_aid', 'First aid', 3, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'training_topic'), 'fire_safety', 'Fire safety', 4, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'training_topic'), 'data_protection', 'Data protection', 5, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'training_topic'), 'online_safety', 'Online safety', 6, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'training_topic'), 'send_awareness', 'Send awareness', 7, '2026-01-01');

-- behaviour_category: Behaviour categories (state minimum framework includes bullying, violence, lateness, positive conduct)
INSERT INTO `code_list` (`id`, `tenant_id`, `code`, `title`, `pack`, `is_extensible`) VALUES (UUID_TO_BIN(UUID()), @tenant, 'behaviour_category', 'Behaviour categories (state minimum framework includes bullying, violence, lateness, positive conduct)', 'ng-core', TRUE);
INSERT INTO `code_value` (`id`, `tenant_id`, `code_list_id`, `code`, `label`, `sort_order`, `valid_from`) VALUES
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'behaviour_category'), 'positive_conduct', 'Positive conduct', 1, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'behaviour_category'), 'academic_effort', 'Academic effort', 2, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'behaviour_category'), 'helpfulness', 'Helpfulness', 3, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'behaviour_category'), 'leadership', 'Leadership', 4, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'behaviour_category'), 'bullying', 'Bullying', 5, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'behaviour_category'), 'cyber_bullying', 'Cyber bullying', 6, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'behaviour_category'), 'violence', 'Violence', 7, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'behaviour_category'), 'lateness', 'Lateness', 8, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'behaviour_category'), 'disruption', 'Disruption', 9, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'behaviour_category'), 'defiance', 'Defiance', 10, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'behaviour_category'), 'uniform', 'Uniform', 11, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'behaviour_category'), 'damage', 'Damage', 12, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'behaviour_category'), 'substance', 'Substance', 13, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'behaviour_category'), 'other', 'Other', 14, '2026-01-01');

-- concern_category: Safeguarding concern categories — Nigerian pack (FR-SAF-105)
INSERT INTO `code_list` (`id`, `tenant_id`, `code`, `title`, `pack`, `is_extensible`) VALUES (UUID_TO_BIN(UUID()), @tenant, 'concern_category', 'Safeguarding concern categories — Nigerian pack (FR-SAF-105)', 'ng-core', FALSE);
INSERT INTO `code_value` (`id`, `tenant_id`, `code_list_id`, `code`, `label`, `sort_order`, `valid_from`) VALUES
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'concern_category'), 'physical_abuse', 'Physical abuse', 1, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'concern_category'), 'emotional_abuse', 'Emotional abuse', 2, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'concern_category'), 'sexual_abuse', 'Sexual abuse', 3, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'concern_category'), 'neglect', 'Neglect', 4, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'concern_category'), 'bullying', 'Bullying', 5, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'concern_category'), 'cyber_bullying', 'Cyber bullying', 6, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'concern_category'), 'child_labour', 'Child labour', 7, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'concern_category'), 'early_forced_marriage', 'Early forced marriage', 8, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'concern_category'), 'trafficking', 'Trafficking', 9, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'concern_category'), 'fgm', 'Fgm', 10, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'concern_category'), 'insecurity_abduction_risk', 'Insecurity abduction risk', 11, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'concern_category'), 'substance_misuse', 'Substance misuse', 12, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'concern_category'), 'online_safety', 'Online safety', 13, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'concern_category'), 'risk_of_dropping_out', 'Risk of dropping out', 14, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'concern_category'), 'other', 'Other', 15, '2026-01-01');

-- risk_level: Safeguarding risk levels (set by the DSL)
INSERT INTO `code_list` (`id`, `tenant_id`, `code`, `title`, `pack`, `is_extensible`) VALUES (UUID_TO_BIN(UUID()), @tenant, 'risk_level', 'Safeguarding risk levels (set by the DSL)', 'ng-core', FALSE);
INSERT INTO `code_value` (`id`, `tenant_id`, `code_list_id`, `code`, `label`, `sort_order`, `valid_from`) VALUES
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'risk_level'), 'low', 'Low', 1, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'risk_level'), 'medium', 'Medium', 2, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'risk_level'), 'high', 'High', 3, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'risk_level'), 'immediate', 'Immediate', 4, '2026-01-01');

-- send_need_area: SEND need areas
INSERT INTO `code_list` (`id`, `tenant_id`, `code`, `title`, `pack`, `is_extensible`) VALUES (UUID_TO_BIN(UUID()), @tenant, 'send_need_area', 'SEND need areas', 'ng-core', FALSE);
INSERT INTO `code_value` (`id`, `tenant_id`, `code_list_id`, `code`, `label`, `sort_order`, `valid_from`) VALUES
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'send_need_area'), 'cognition_learning', 'Cognition learning', 1, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'send_need_area'), 'communication_interaction', 'Communication interaction', 2, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'send_need_area'), 'social_emotional_mental_health', 'Social emotional mental health', 3, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'send_need_area'), 'sensory_visual', 'Sensory visual', 4, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'send_need_area'), 'sensory_hearing', 'Sensory hearing', 5, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'send_need_area'), 'physical', 'Physical', 6, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'send_need_area'), 'multiple', 'Multiple', 7, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'send_need_area'), 'medical', 'Medical', 8, '2026-01-01');

-- send_support_level: SEND support levels
INSERT INTO `code_list` (`id`, `tenant_id`, `code`, `title`, `pack`, `is_extensible`) VALUES (UUID_TO_BIN(UUID()), @tenant, 'send_support_level', 'SEND support levels', 'ng-core', FALSE);
INSERT INTO `code_value` (`id`, `tenant_id`, `code_list_id`, `code`, `label`, `sort_order`, `valid_from`) VALUES
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'send_support_level'), 'monitoring', 'Monitoring', 1, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'send_support_level'), 'school_support', 'School support', 2, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'send_support_level'), 'specialist_support', 'Specialist support', 3, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'send_support_level'), 'statutory_plan', 'Statutory plan', 4, '2026-01-01');

-- send_plan_type: SEND plan types
INSERT INTO `code_list` (`id`, `tenant_id`, `code`, `title`, `pack`, `is_extensible`) VALUES (UUID_TO_BIN(UUID()), @tenant, 'send_plan_type', 'SEND plan types', 'ng-core', FALSE);
INSERT INTO `code_value` (`id`, `tenant_id`, `code_list_id`, `code`, `label`, `sort_order`, `valid_from`) VALUES
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'send_plan_type'), 'iep', 'Iep', 1, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'send_plan_type'), 'isp', 'Isp', 2, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'send_plan_type'), 'statutory_plan', 'Statutory plan', 3, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'send_plan_type'), 'health_plan', 'Health plan', 4, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'send_plan_type'), 'behaviour_support_plan', 'Behaviour support plan', 5, '2026-01-01');

-- provision_kind: SEND provision kinds
INSERT INTO `code_list` (`id`, `tenant_id`, `code`, `title`, `pack`, `is_extensible`) VALUES (UUID_TO_BIN(UUID()), @tenant, 'provision_kind', 'SEND provision kinds', 'ng-core', FALSE);
INSERT INTO `code_value` (`id`, `tenant_id`, `code_list_id`, `code`, `label`, `sort_order`, `valid_from`) VALUES
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'provision_kind'), 'in_class_support', 'In class support', 1, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'provision_kind'), 'small_group', 'Small group', 2, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'provision_kind'), 'one_to_one', 'One to one', 3, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'provision_kind'), 'therapy', 'Therapy', 4, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'provision_kind'), 'assistive_technology', 'Assistive technology', 5, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'provision_kind'), 'mentoring', 'Mentoring', 6, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'provision_kind'), 'gifted_extension', 'Gifted extension', 7, '2026-01-01');

-- adjustment_kind: Reasonable adjustments
INSERT INTO `code_list` (`id`, `tenant_id`, `code`, `title`, `pack`, `is_extensible`) VALUES (UUID_TO_BIN(UUID()), @tenant, 'adjustment_kind', 'Reasonable adjustments', 'ng-core', FALSE);
INSERT INTO `code_value` (`id`, `tenant_id`, `code_list_id`, `code`, `label`, `sort_order`, `valid_from`) VALUES
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'adjustment_kind'), 'extra_time', 'Extra time', 1, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'adjustment_kind'), 'large_print', 'Large print', 2, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'adjustment_kind'), 'read_aloud', 'Read aloud', 3, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'adjustment_kind'), 'scribe', 'Scribe', 4, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'adjustment_kind'), 'rest_breaks', 'Rest breaks', 5, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'adjustment_kind'), 'seating', 'Seating', 6, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'adjustment_kind'), 'alternative_format', 'Alternative format', 7, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'adjustment_kind'), 'assistive_technology', 'Assistive technology', 8, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'adjustment_kind'), 'separate_room', 'Separate room', 9, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'adjustment_kind'), 'step_free_room', 'Step free room', 10, '2026-01-01');

-- referral_agency: External referral agencies
INSERT INTO `code_list` (`id`, `tenant_id`, `code`, `title`, `pack`, `is_extensible`) VALUES (UUID_TO_BIN(UUID()), @tenant, 'referral_agency', 'External referral agencies', 'ng-core', FALSE);
INSERT INTO `code_value` (`id`, `tenant_id`, `code_list_id`, `code`, `label`, `sort_order`, `valid_from`) VALUES
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'referral_agency'), 'speech_language', 'Speech language', 1, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'referral_agency'), 'occupational_therapy', 'Occupational therapy', 2, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'referral_agency'), 'educational_psychology', 'Educational psychology', 3, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'referral_agency'), 'health', 'Health', 4, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'referral_agency'), 'social_welfare', 'Social welfare', 5, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'referral_agency'), 'police', 'Police', 6, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'referral_agency'), 'ngo', 'Ngo', 7, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'referral_agency'), 'other', 'Other', 8, '2026-01-01');

-- gifted_domain: Gifted and talented domains
INSERT INTO `code_list` (`id`, `tenant_id`, `code`, `title`, `pack`, `is_extensible`) VALUES (UUID_TO_BIN(UUID()), @tenant, 'gifted_domain', 'Gifted and talented domains', 'ng-core', FALSE);
INSERT INTO `code_value` (`id`, `tenant_id`, `code_list_id`, `code`, `label`, `sort_order`, `valid_from`) VALUES
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'gifted_domain'), 'academic', 'Academic', 1, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'gifted_domain'), 'mathematics', 'Mathematics', 2, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'gifted_domain'), 'science', 'Science', 3, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'gifted_domain'), 'languages', 'Languages', 4, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'gifted_domain'), 'arts', 'Arts', 5, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'gifted_domain'), 'music', 'Music', 6, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'gifted_domain'), 'sport', 'Sport', 7, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'gifted_domain'), 'leadership', 'Leadership', 8, '2026-01-01');

-- wellbeing_concern_type: Wellbeing concern types (MFS §18.8)
INSERT INTO `code_list` (`id`, `tenant_id`, `code`, `title`, `pack`, `is_extensible`) VALUES (UUID_TO_BIN(UUID()), @tenant, 'wellbeing_concern_type', 'Wellbeing concern types (MFS §18.8)', 'ng-core', FALSE);
INSERT INTO `code_value` (`id`, `tenant_id`, `code_list_id`, `code`, `label`, `sort_order`, `valid_from`) VALUES
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'wellbeing_concern_type'), 'exam_pressure', 'Exam pressure', 1, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'wellbeing_concern_type'), 'anxiety', 'Anxiety', 2, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'wellbeing_concern_type'), 'bullying', 'Bullying', 3, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'wellbeing_concern_type'), 'friendships', 'Friendships', 4, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'wellbeing_concern_type'), 'family', 'Family', 5, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'wellbeing_concern_type'), 'sleep', 'Sleep', 6, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'wellbeing_concern_type'), 'online_safety', 'Online safety', 7, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'wellbeing_concern_type'), 'food', 'Food', 8, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'wellbeing_concern_type'), 'transport', 'Transport', 9, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'wellbeing_concern_type'), 'other', 'Other', 10, '2026-01-01');

-- intervention_kind: Intervention kinds
INSERT INTO `code_list` (`id`, `tenant_id`, `code`, `title`, `pack`, `is_extensible`) VALUES (UUID_TO_BIN(UUID()), @tenant, 'intervention_kind', 'Intervention kinds', 'ng-core', FALSE);
INSERT INTO `code_value` (`id`, `tenant_id`, `code_list_id`, `code`, `label`, `sort_order`, `valid_from`) VALUES
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'intervention_kind'), 'attendance', 'Attendance', 1, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'intervention_kind'), 'academic_catch_up', 'Academic catch up', 2, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'intervention_kind'), 'behaviour', 'Behaviour', 3, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'intervention_kind'), 'wellbeing', 'Wellbeing', 4, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'intervention_kind'), 'literacy', 'Literacy', 5, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'intervention_kind'), 'numeracy', 'Numeracy', 6, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'intervention_kind'), 're_entry', 'Re entry', 7, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'intervention_kind'), 'mentoring', 'Mentoring', 8, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'intervention_kind'), 'family_support', 'Family support', 9, '2026-01-01');

-- inspection_area: Inspection areas
INSERT INTO `code_list` (`id`, `tenant_id`, `code`, `title`, `pack`, `is_extensible`) VALUES (UUID_TO_BIN(UUID()), @tenant, 'inspection_area', 'Inspection areas', 'ng-core', FALSE);
INSERT INTO `code_value` (`id`, `tenant_id`, `code_list_id`, `code`, `label`, `sort_order`, `valid_from`) VALUES
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'inspection_area'), 'leadership', 'Leadership', 1, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'inspection_area'), 'teaching_learning', 'Teaching learning', 2, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'inspection_area'), 'curriculum', 'Curriculum', 3, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'inspection_area'), 'safeguarding', 'Safeguarding', 4, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'inspection_area'), 'welfare', 'Welfare', 5, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'inspection_area'), 'premises', 'Premises', 6, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'inspection_area'), 'staffing', 'Staffing', 7, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'inspection_area'), 'records', 'Records', 8, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'inspection_area'), 'finance', 'Finance', 9, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'inspection_area'), 'community', 'Community', 10, '2026-01-01');

-- inspection_judgement: Inspection judgements
INSERT INTO `code_list` (`id`, `tenant_id`, `code`, `title`, `pack`, `is_extensible`) VALUES (UUID_TO_BIN(UUID()), @tenant, 'inspection_judgement', 'Inspection judgements', 'ng-core', FALSE);
INSERT INTO `code_value` (`id`, `tenant_id`, `code_list_id`, `code`, `label`, `sort_order`, `valid_from`) VALUES
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'inspection_judgement'), 'outstanding', 'Outstanding', 1, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'inspection_judgement'), 'good', 'Good', 2, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'inspection_judgement'), 'requires_improvement', 'Requires improvement', 3, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'inspection_judgement'), 'inadequate', 'Inadequate', 4, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'inspection_judgement'), 'not_judged', 'Not judged', 5, '2026-01-01');

-- facility_check_kind: Facility checks and certifications (FR-INSP-101)
INSERT INTO `code_list` (`id`, `tenant_id`, `code`, `title`, `pack`, `is_extensible`) VALUES (UUID_TO_BIN(UUID()), @tenant, 'facility_check_kind', 'Facility checks and certifications (FR-INSP-101)', 'ng-core', FALSE);
INSERT INTO `code_value` (`id`, `tenant_id`, `code_list_id`, `code`, `label`, `sort_order`, `valid_from`) VALUES
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'facility_check_kind'), 'fire_inspection', 'Fire inspection', 1, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'facility_check_kind'), 'fire_certificate', 'Fire certificate', 2, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'facility_check_kind'), 'health_safety_check', 'Health safety check', 3, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'facility_check_kind'), 'structural_safety', 'Structural safety', 4, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'facility_check_kind'), 'food_hygiene', 'Food hygiene', 5, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'facility_check_kind'), 'water_quality', 'Water quality', 6, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'facility_check_kind'), 'electrical_safety', 'Electrical safety', 7, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'facility_check_kind'), 'generator_safety', 'Generator safety', 8, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'facility_check_kind'), 'vehicle_roadworthiness', 'Vehicle roadworthiness', 9, '2026-01-01');

-- curriculum_framework: Curriculum frameworks (FR-CUR-115)
INSERT INTO `code_list` (`id`, `tenant_id`, `code`, `title`, `pack`, `is_extensible`) VALUES (UUID_TO_BIN(UUID()), @tenant, 'curriculum_framework', 'Curriculum frameworks (FR-CUR-115)', 'ng-core', FALSE);
INSERT INTO `code_value` (`id`, `tenant_id`, `code_list_id`, `code`, `label`, `sort_order`, `valid_from`) VALUES
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'curriculum_framework'), 'national', 'National', 1, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'curriculum_framework'), 'state', 'State', 2, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'curriculum_framework'), 'cambridge', 'Cambridge', 3, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'curriculum_framework'), 'ib', 'Ib', 4, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'curriculum_framework'), 'pearson', 'Pearson', 5, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'curriculum_framework'), 'american', 'American', 6, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'curriculum_framework'), 'british', 'British', 7, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'curriculum_framework'), 'competency', 'Competency', 8, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'curriculum_framework'), 'institutional', 'Institutional', 9, '2026-01-01');

-- benchmark_framework: Tertiary benchmark frameworks
INSERT INTO `code_list` (`id`, `tenant_id`, `code`, `title`, `pack`, `is_extensible`) VALUES (UUID_TO_BIN(UUID()), @tenant, 'benchmark_framework', 'Tertiary benchmark frameworks', 'ng-core', FALSE);
INSERT INTO `code_value` (`id`, `tenant_id`, `code_list_id`, `code`, `label`, `sort_order`, `valid_from`) VALUES
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'benchmark_framework'), 'NUC_CCMAS', 'Nuc ccmas', 1, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'benchmark_framework'), 'NBTE', 'Nbte', 2, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'benchmark_framework'), 'NCCE', 'Ncce', 3, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'benchmark_framework'), 'MDCN', 'Mdcn', 4, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'benchmark_framework'), 'NMCN', 'Nmcn', 5, '2026-01-01');

-- degree_class: Degree and diploma classifications
INSERT INTO `code_list` (`id`, `tenant_id`, `code`, `title`, `pack`, `is_extensible`) VALUES (UUID_TO_BIN(UUID()), @tenant, 'degree_class', 'Degree and diploma classifications', 'ng-core', FALSE);
INSERT INTO `code_value` (`id`, `tenant_id`, `code_list_id`, `code`, `label`, `sort_order`, `valid_from`) VALUES
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'degree_class'), 'first_class', 'First class', 1, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'degree_class'), 'second_upper', 'Second upper', 2, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'degree_class'), 'second_lower', 'Second lower', 3, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'degree_class'), 'third_class', 'Third class', 4, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'degree_class'), 'pass', 'Pass', 5, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'degree_class'), 'distinction', 'Distinction', 6, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'degree_class'), 'upper_credit', 'Upper credit', 7, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'degree_class'), 'lower_credit', 'Lower credit', 8, '2026-01-01');

-- programme_family: Health-profession programme families (FR-MED-103)
INSERT INTO `code_list` (`id`, `tenant_id`, `code`, `title`, `pack`, `is_extensible`) VALUES (UUID_TO_BIN(UUID()), @tenant, 'programme_family', 'Health-profession programme families (FR-MED-103)', 'ng-core', FALSE);
INSERT INTO `code_value` (`id`, `tenant_id`, `code_list_id`, `code`, `label`, `sort_order`, `valid_from`) VALUES
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'programme_family'), 'medicine', 'Medicine', 1, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'programme_family'), 'dentistry', 'Dentistry', 2, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'programme_family'), 'nursing', 'Nursing', 3, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'programme_family'), 'midwifery', 'Midwifery', 4, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'programme_family'), 'pharmacy', 'Pharmacy', 5, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'programme_family'), 'physiotherapy', 'Physiotherapy', 6, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'programme_family'), 'radiography', 'Radiography', 7, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'programme_family'), 'medical_laboratory_science', 'Medical laboratory science', 8, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'programme_family'), 'community_health', 'Community health', 9, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'programme_family'), 'public_health', 'Public health', 10, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'programme_family'), 'other_allied', 'Other allied', 11, '2026-01-01');

-- destination_kind: Destinations
INSERT INTO `code_list` (`id`, `tenant_id`, `code`, `title`, `pack`, `is_extensible`) VALUES (UUID_TO_BIN(UUID()), @tenant, 'destination_kind', 'Destinations', 'ng-core', FALSE);
INSERT INTO `code_value` (`id`, `tenant_id`, `code_list_id`, `code`, `label`, `sort_order`, `valid_from`) VALUES
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'destination_kind'), 'further_education', 'Further education', 1, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'destination_kind'), 'higher_education', 'Higher education', 2, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'destination_kind'), 'employment', 'Employment', 3, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'destination_kind'), 'apprenticeship', 'Apprenticeship', 4, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'destination_kind'), 'entrepreneurship', 'Entrepreneurship', 5, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'destination_kind'), 'professional_qualification', 'Professional qualification', 6, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'destination_kind'), 'nysc', 'Nysc', 7, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'destination_kind'), 'not_in_education_or_employment', 'Not in education or employment', 8, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'destination_kind'), 'unknown', 'Unknown', 9, '2026-01-01');

-- admission_scheme: Higher-education admission schemes
INSERT INTO `code_list` (`id`, `tenant_id`, `code`, `title`, `pack`, `is_extensible`) VALUES (UUID_TO_BIN(UUID()), @tenant, 'admission_scheme', 'Higher-education admission schemes', 'ng-core', FALSE);
INSERT INTO `code_value` (`id`, `tenant_id`, `code_list_id`, `code`, `label`, `sort_order`, `valid_from`) VALUES
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'admission_scheme'), 'jamb_utme', 'Jamb utme', 1, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'admission_scheme'), 'jamb_de', 'Jamb de', 2, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'admission_scheme'), 'caps', 'Caps', 3, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'admission_scheme'), 'ucas_equivalent', 'Ucas equivalent', 4, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'admission_scheme'), 'direct', 'Direct', 5, '2026-01-01');

-- finance_scheme: Student finance schemes
INSERT INTO `code_list` (`id`, `tenant_id`, `code`, `title`, `pack`, `is_extensible`) VALUES (UUID_TO_BIN(UUID()), @tenant, 'finance_scheme', 'Student finance schemes', 'ng-core', FALSE);
INSERT INTO `code_value` (`id`, `tenant_id`, `code_list_id`, `code`, `label`, `sort_order`, `valid_from`) VALUES
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'finance_scheme'), 'nelfund', 'Nelfund', 1, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'finance_scheme'), 'state_bursary', 'State bursary', 2, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'finance_scheme'), 'scholarship', 'Scholarship', 3, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'finance_scheme'), 'bank_loan', 'Bank loan', 4, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'finance_scheme'), 'other', 'Other', 5, '2026-01-01');

-- guidance_topic: Career guidance topics
INSERT INTO `code_list` (`id`, `tenant_id`, `code`, `title`, `pack`, `is_extensible`) VALUES (UUID_TO_BIN(UUID()), @tenant, 'guidance_topic', 'Career guidance topics', 'ng-core', FALSE);
INSERT INTO `code_value` (`id`, `tenant_id`, `code_list_id`, `code`, `label`, `sort_order`, `valid_from`) VALUES
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'guidance_topic'), 'stream_selection', 'Stream selection', 1, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'guidance_topic'), 'subject_choice', 'Subject choice', 2, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'guidance_topic'), 'careers', 'Careers', 3, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'guidance_topic'), 'higher_education', 'Higher education', 4, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'guidance_topic'), 'tvet_pathway', 'Tvet pathway', 5, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'guidance_topic'), 'personal', 'Personal', 6, '2026-01-01');

-- industry_sector: Industry sectors
INSERT INTO `code_list` (`id`, `tenant_id`, `code`, `title`, `pack`, `is_extensible`) VALUES (UUID_TO_BIN(UUID()), @tenant, 'industry_sector', 'Industry sectors', 'ng-core', FALSE);
INSERT INTO `code_value` (`id`, `tenant_id`, `code_list_id`, `code`, `label`, `sort_order`, `valid_from`) VALUES
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'industry_sector'), 'agriculture', 'Agriculture', 1, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'industry_sector'), 'construction', 'Construction', 2, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'industry_sector'), 'manufacturing', 'Manufacturing', 3, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'industry_sector'), 'ict', 'Ict', 4, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'industry_sector'), 'health', 'Health', 5, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'industry_sector'), 'hospitality', 'Hospitality', 6, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'industry_sector'), 'energy', 'Energy', 7, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'industry_sector'), 'finance', 'Finance', 8, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'industry_sector'), 'public_sector', 'Public sector', 9, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'industry_sector'), 'education', 'Education', 10, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'industry_sector'), 'other', 'Other', 11, '2026-01-01');

-- digital_strand: Digital skills framework strands (MFS §8.6)
INSERT INTO `code_list` (`id`, `tenant_id`, `code`, `title`, `pack`, `is_extensible`) VALUES (UUID_TO_BIN(UUID()), @tenant, 'digital_strand', 'Digital skills framework strands (MFS §8.6)', 'ng-core', FALSE);
INSERT INTO `code_value` (`id`, `tenant_id`, `code_list_id`, `code`, `label`, `sort_order`, `valid_from`) VALUES
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'digital_strand'), 'device_use', 'Device use', 1, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'digital_strand'), 'information_literacy', 'Information literacy', 2, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'digital_strand'), 'communication', 'Communication', 3, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'digital_strand'), 'content_creation', 'Content creation', 4, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'digital_strand'), 'safety_wellbeing', 'Safety wellbeing', 5, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'digital_strand'), 'computational_thinking', 'Computational thinking', 6, '2026-01-01');

-- feeding_programme: School feeding programmes
INSERT INTO `code_list` (`id`, `tenant_id`, `code`, `title`, `pack`, `is_extensible`) VALUES (UUID_TO_BIN(UUID()), @tenant, 'feeding_programme', 'School feeding programmes', 'ng-core', FALSE);
INSERT INTO `code_value` (`id`, `tenant_id`, `code_list_id`, `code`, `label`, `sort_order`, `valid_from`) VALUES
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'feeding_programme'), 'ng_hgsfp', 'Ng hgsfp', 1, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'feeding_programme'), 'state_programme', 'State programme', 2, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'feeding_programme'), 'institution', 'Institution', 3, '2026-01-01');

-- dietary_code: Dietary requirements
INSERT INTO `code_list` (`id`, `tenant_id`, `code`, `title`, `pack`, `is_extensible`) VALUES (UUID_TO_BIN(UUID()), @tenant, 'dietary_code', 'Dietary requirements', 'ng-core', FALSE);
INSERT INTO `code_value` (`id`, `tenant_id`, `code_list_id`, `code`, `label`, `sort_order`, `valid_from`) VALUES
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'dietary_code'), 'vegetarian', 'Vegetarian', 1, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'dietary_code'), 'halal', 'Halal', 2, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'dietary_code'), 'no_pork', 'No pork', 3, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'dietary_code'), 'nut_allergy', 'Nut allergy', 4, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'dietary_code'), 'lactose_intolerant', 'Lactose intolerant', 5, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'dietary_code'), 'gluten_free', 'Gluten free', 6, '2026-01-01'),
  (UUID_TO_BIN(UUID()), @tenant, (SELECT `id` FROM `code_list` WHERE `tenant_id` = @tenant AND `code` = 'dietary_code'), 'other', 'Other', 7, '2026-01-01');

