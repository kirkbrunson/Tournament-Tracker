-- Table definitions for the tournament project.


/* Drop and recreate DB */
DROP DATABASE tournament;
CREATE DATABASE tournament;

-- Connect to DB
\c tournament;


-- Table defs
CREATE TABLE Players(
	id serial PRIMARY KEY,
	name text
);

CREATE TABLE Matches(
	id serial PRIMARY KEY,
	player1 smallint default 0 REFERENCES Players(id) NOT NULL,
	player2 smallint default 0 REFERENCES Players(id) NOT NULL
);

-- Create views here:

-- View for player Standings:
CREATE VIEW v_playerStandings AS
	SELECT players.id, players.name, 
	(SELECT COALESCE(wins, 0) as wins 
		FROM (SELECT count(matches) as wins 
			from Matches where players.id = matches.player1) as wins), 
	
	(SELECT count(matches) as totalMatches from Matches 
			where (players.id = matches.player1 or players.id = matches.player2))

	from Players
	ORDER BY wins desc;


CREATE VIEW v_matchCount AS
	select id, totalMatches from v_PlayerStandings;


CREATE VIEW v_playerCount AS
	SELECT count(players.id) as player_count from players;

-- Values to populate DB

-- Create players
-- INSERT INTO Players VALUES(default, 'Bobby Tables');
-- INSERT INTO Players VALUES(default, 'Anna Polski');
-- INSERT INTO Players VALUES(default, 'Xavier S. Santora');
-- INSERT INTO Players VALUES(default, 'Bill Havaford');
-- INSERT INTO Players VALUES(default, 'Jim Crawford');

-- -- Insert matches into tournament 1
-- INSERT INTO Matches VALUES(default, 1, 1, 2, default);
-- INSERT INTO Matches VALUES(default, 1, 1, 3, default);
-- INSERT INTO Matches VALUES(default, 1, 4, 3, default);
-- INSERT INTO Matches VALUES(default, 1, 1, 4, default);
-- INSERT INTO Matches VALUES(default, 1, 2, 1, default);
-- INSERT INTO Matches VALUES(default, 1, 3, 1, default);
-- INSERT INTO Matches VALUES(default, 1, 3, 2, default);
-- INSERT INTO Matches VALUES(default, 1, 5, 1, default);