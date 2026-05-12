-- Phase 0: Données de test génératives (ref.*)
-- Génère 20 enseignants, 250 étudiants, 15 cours et inscriptions cohérentes

-- ============================================
-- 1. Générer 20 enseignants
-- ============================================
INSERT INTO ref.enseignant (id, nom, prenom)
SELECT
    i,
    'NOM_' || i,
    'Prenom_' || i
FROM generate_series(1, 20) AS s(i)
ON CONFLICT (id) DO NOTHING;

-- ============================================
-- 2. Générer 250 étudiants
-- ============================================
INSERT INTO ref.etudiant (numero_et, nom, prenom, filiere, niveau)
SELECT
    'E' || LPAD(i::text, 4, '0'),
    'Nom_' || i,
    'Prenom_' || i,
    (ARRAY['Informatique', 'Réseaux', 'Data'])[floor(random()*3)+1],
    (ARRAY['Bac +1','Bac +2','Bac +3','Bac +4','Bac +5'])[floor(random()*5)+1]
FROM generate_series(1, 250) AS s(i)
ON CONFLICT (numero_et) DO NOTHING;

-- ============================================
-- 3. Générer 15 cours (3 existants + 12 nouveaux)
-- ============================================
-- Cours existants (IDs 1-3)
INSERT INTO ref.cours (id, intitule, section, horaire, session, enseignant_id) VALUES
  (1, 'Bases de Données', 'Bachelor', '08h00–10h00', 'matin', 1),
  (2, 'Réseaux 1', 'Bachelor', '08h00–10h00', 'matin', 2),
  (3, 'Spark & Big Data', 'Mastere', '13h00–16h00', 'apres-midi', 3)
ON CONFLICT (id) DO NOTHING;

-- Cours supplémentaires (IDs 4-15)
INSERT INTO ref.cours (id, intitule, section, horaire, session, enseignant_id)
SELECT
    i,
    CASE i
        WHEN 4 THEN 'Programmation Python'
        WHEN 5 THEN 'Développement Web'
        WHEN 6 THEN 'Algorithmique'
        WHEN 7 THEN 'Sécurité Informatique'
        WHEN 8 THEN 'Intelligence Artificielle'
        WHEN 9 THEN 'Machine Learning'
        WHEN 10 THEN 'Cloud Computing'
        WHEN 11 THEN 'DevOps & CI/CD'
        WHEN 12 THEN 'Data Visualization'
        WHEN 13 THEN 'Deep Learning'
        WHEN 14 THEN 'Blockchain'
        WHEN 15 THEN 'IoT & Embarqué'
    END,
    CASE
        WHEN i % 2 = 0 THEN 'Bachelor'
        ELSE 'Mastere'
    END,
    CASE
        WHEN i % 3 = 0 THEN '08h00–10h00'
        WHEN i % 3 = 1 THEN '10h00–12h00'
        ELSE '13h00–16h00'
    END,
    CASE
        WHEN i % 2 = 0 THEN 'matin'
        ELSE 'apres-midi'
    END,
    (SELECT id FROM ref.enseignant ORDER BY random() LIMIT 1)
FROM generate_series(4, 15) s(i)
ON CONFLICT (id) DO NOTHING;

-- ============================================
-- 4. Planning des cours (Lundi-Vendredi)
-- ============================================
INSERT INTO ref.planning (id, cours_id, jour_semaine, heure_debut, heure_fin)
SELECT
    i,
    c.id,
    (ARRAY['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi'])[(i % 5) + 1],
    CASE
        WHEN c.session = 'matin' THEN '08:00'::time
        ELSE '13:00'::time
    END,
    CASE
        WHEN c.session = 'matin' THEN '12:00'::time
        ELSE '17:00'::time
    END
FROM generate_series(1, 15) AS s(i)
JOIN ref.cours c ON c.id = ((i - 1) % 15) + 1
ON CONFLICT (id) DO NOTHING;

-- ============================================
-- 5. Inscriptions cohérentes (max 6 cours par étudiant)
-- Bachelor (Bac+1 à Bac+3) → Cours Bachelor
-- Mastere (Bac+4 à Bac+5) → Cours Mastere
-- ============================================
INSERT INTO ref.inscription (id_etudiant, cours_id, date_inscription)
SELECT *
FROM (
    SELECT
        e.numero_et,
        c.id as cours_id,
        CURRENT_DATE as date_inscription,
        ROW_NUMBER() OVER (PARTITION BY e.numero_et ORDER BY random()) as rn
    FROM ref.etudiant e
    JOIN ref.cours c
    ON (
        (e.niveau IN ('Bac +1','Bac +2','Bac +3') AND c.section = 'Bachelor')
        OR
        (e.niveau IN ('Bac +4','Bac +5') AND c.section = 'Mastere')
    )
) t
WHERE rn <= 6
ON CONFLICT (id_etudiant, cours_id) DO NOTHING;
