-- Table definitions for the tournament project.


/* Drop and recreate DB */
DROP DATABASE tournamentdb;
CREATE DATABASE tournamentdb;

-- Connect to DB
\c tournamentdb;


-- Table defs
CREATE TABLE Players(
	id serial PRIMARY KEY,
	name text
);

CREATE TABLE Tournaments(
	id serial PRIMARY KEY,
	name text
);

-- Need to check server side that both player and tour exist
CREATE TABLE TournamentRegistration(
	id serial PRIMARY KEY,
	tournament_id smallint REFERENCES Tournaments(id),
	player_id smallint REFERENCES Players(id)
);


/* 
	Match schema: id | tourID | player1 | player2 | matchVal (describes rel between p1 and p2)
	matchVal: = 1 if p1 win, = 0 if p1 loss, = 0.5 if draw... don't need 0/loss case bc always sorted on p1 vs p2
	Bye inserted w. player1, player2 = NULL, 1
*/

CREATE TABLE Matches(
	id serial PRIMARY KEY,
	tournament_id smallint REFERENCES Tournaments(id),
	player1 smallint default 0 REFERENCES Players(id) NOT NULL,
	player2 smallint default 0 REFERENCES Players(id),
	matchValue numeric default 1
);


-- need to support byes for mult tour
CREATE TABLE ByeLog(
	id serial PRIMARY KEY,
	tournament_id smallint REFERENCES Tournaments(id) NOT NULL,
	player_id smallint REFERENCES Players(id) NOT NULL
);



-- Create views here:

-- Should refactor into smaller sections that do one thing only... then create this as aggregate view.
-- change this to a function to accept args and comment
CREATE VIEW v_playerStandings AS
	SELECT tournaments.id as tournament_id, players.id as player_id, players.name, 
	(SELECT COALESCE(wins, 0) as wins 
		FROM (SELECT sum(matches.matchValue) as wins 
			from Matches where players.id = matches.player1 and matches.tournament_id = 1) as wins), 
	
	-- Describe this 
	(select * from
		(SELECT count(matches) as totalMatches from Matches 
			where ((players.id = matches.player1 or players.id = matches.player2) and matches.tournament_id = 1)
		) as totalMatches
	where totalMatches != 0
	)

	-- Describe this
	from Players, Tournaments where tournaments.id = 1 
		and (SELECT count(matches) as totalMatches from Matches 
			where ((players.id = matches.player1 or players.id = matches.player2) and matches.tournament_id = 1)) !=0
	ORDER BY wins desc;


CREATE VIEW v_matchCount AS
	select player_id, totalMatches from v_PlayerStandings;


-- Values to populate DB

-- Create players
INSERT INTO Players VALUES(default, 'Bobby Tables');
INSERT INTO Players VALUES(default, 'Anna Polski');
INSERT INTO Players VALUES(default, 'Xavier S. Santora');
INSERT INTO Players VALUES(default, 'Bill Havaford');
INSERT INTO Players VALUES(default, 'Jim Crawford');

-- Create tournaments
INSERT INTO Tournaments VALUES(default, 'tournament_1');
INSERT INTO Tournaments VALUES(default, 'tournament_2');

-- Register players for tournament 1
INSERT INTO TournamentRegistration VALUES(default, 1, 1);
INSERT INTO TournamentRegistration VALUES(default, 1, 2);
INSERT INTO TournamentRegistration VALUES(default, 1, 3);
INSERT INTO TournamentRegistration VALUES(default, 1, 4);
INSERT INTO TournamentRegistration VALUES(default, 1, 5);

-- Insert matches into tournament 1
INSERT INTO Matches VALUES(default, 1, 1, 2, default);
INSERT INTO Matches VALUES(default, 1, 1, 3, default);
INSERT INTO Matches VALUES(default, 1, 4, 3, default);
INSERT INTO Matches VALUES(default, 1, 1, 4, default);
INSERT INTO Matches VALUES(default, 1, 2, 1, default);
INSERT INTO Matches VALUES(default, 1, 3, 1, default);
INSERT INTO Matches VALUES(default, 1, 3, 2, default);
INSERT INTO Matches VALUES(default, 1, 5, 1, default);

-- Testing draws:
INSERT INTO Matches VALUES(default, 1, 3, 2, 0.5);
INSERT INTO Matches VALUES(default, 1, 1, 2, 0.5);
INSERT INTO Matches VALUES(default, 1, 4, 3, 0.5);
INSERT INTO Matches VALUES(default, 1, 3, 1, 0.5);

-- Register players for tournament 2
INSERT INTO TournamentRegistration VALUES(default, 2, 1);
INSERT INTO TournamentRegistration VALUES(default, 2, 2);
INSERT INTO TournamentRegistration VALUES(default, 2, 3);

-- Insert matches into tournament 2
INSERT INTO Matches VALUES(default, 2, 1, 2, default);
INSERT INTO Matches VALUES(default, 2, 1, 3, default);
INSERT INTO Matches VALUES(default, 2, 2, 3, default);
