-- Phase 0: Données de test minimales (ref.*)

INSERT INTO ref.enseignant (id, nom, prenom) VALUES
  (1, 'BENALI', 'Karim'),
  (2, 'ZAHRAOUI', 'Nadia'),
  (3, 'EL AMRANI', 'Youssef')
ON CONFLICT (id) DO NOTHING;

INSERT INTO ref.etudiant (numero_et, nom, prenom, filiere, niveau) VALUES
  ('E0001', 'AHMED', 'Sara', 'Informatique', 'L1'),
  ('E0002', 'BOUKHALI', 'Omar', 'Informatique', 'L1'),
  ('E0003', 'CHERKAOUI', 'Imane', 'Réseaux', 'L2'),
  ('E0004', 'DAOUD', 'Yassine', 'Réseaux', 'L2'),
  ('E0005', 'EL IDRISSI', 'Aya', 'Data', 'L3'),
  ('E0006', 'FARHANI', 'Hamza', 'Data', 'L3')
ON CONFLICT (numero_et) DO NOTHING;

INSERT INTO ref.cours (id, intitule, section, horaire, session, enseignant_id) VALUES
  (1, 'Bases de Données', 'A', '08h00–10h00', 'matin', 1),
  (2, 'Réseaux 1', 'B', '08h00–10h00', 'matin', 2),
  (3, 'Spark & Big Data', 'A', '13h00–16h00', 'apres-midi', 3)
ON CONFLICT (id) DO NOTHING;

-- Planning du lundi au vendredi (exemple)
INSERT INTO ref.planning (id, cours_id, jour_semaine, heure_debut, heure_fin) VALUES
  (1, 1, 'Lundi', '08:00', '10:00'),
  (2, 2, 'Lundi', '08:00', '10:00'),
  (3, 3, 'Lundi', '13:00', '16:00'),
  (4, 1, 'Mardi', '08:00', '10:00'),
  (5, 3, 'Mercredi', '13:00', '16:00'),
  (6, 2, 'Jeudi', '08:00', '10:00'),
  (7, 3, 'Vendredi', '13:00', '16:00')
ON CONFLICT (id) DO NOTHING;

-- Inscriptions
INSERT INTO ref.inscription (id_etudiant, cours_id, date_inscription) VALUES
  ('E0001', 1, CURRENT_DATE),
  ('E0002', 1, CURRENT_DATE),
  ('E0003', 2, CURRENT_DATE),
  ('E0004', 2, CURRENT_DATE),
  ('E0005', 3, CURRENT_DATE),
  ('E0006', 3, CURRENT_DATE),
  ('E0001', 3, CURRENT_DATE),
  ('E0002', 3, CURRENT_DATE)
ON CONFLICT (id_etudiant, cours_id) DO NOTHING;
