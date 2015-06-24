#!/usr/bin/env python
#
# tournament.py -- implementation of a Swiss-system tournament.
# Implements all extra credit options except Opponent match wins
# Note: doesn't run w. tournament_test.py as schema has been changed to support extra credit
#


import psycopg2
import math
import bleach


def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    try:
        DB = psycopg2.connect("dbname=tournament")
        cursor = DB.cursor()
        return DB, cursor
    except:
        raise RuntimeError("An error occured, please try again")


# =========== Delete functions ===========

def deleteMatches():
    """Remove all the match records from the database."""

    # Deals with integrity of foreign keys
    deleteTournamentReg()
    DB, c = connect()

    c.execute("TRUNCATE Matches CASCADE")
    DB.commit()
    DB.close()


def deletePlayers():
    """Remove all the player records from the database."""

    # Deals with integrity of foreign keys
    deleteTournaments()

    DB, c = connect()

    c.execute("TRUNCATE Players CASCADE")
    DB.commit()
    DB.close()


def deleteTournamentReg():
    """Removes current tournament registrations"""
    DB, c = connect()

    c.execute("TRUNCATE ByeLog CASCADE")
    c.execute("TRUNCATE TournamentRegistration CASCADE")
    DB.commit()
    DB.close()


def deleteTournaments():
    """Removes all records other than players"""
    DB, c = connect()

    c.execute("TRUNCATE ByeLog CASCADE")
    c.execute("TRUNCATE Matches CASCADE")
    c.execute("TRUNCATE TournamentRegistration CASCADE")
    c.execute("TRUNCATE Tournaments CASCADE")
    DB.commit()
    DB.close()


# =========== Create functions ===========

def createPlayer(name):
    """Adds a player to the tournament database."""
    DB, c = connect()

    query = "INSERT INTO players VALUES(default, %s);"
    param = (bleach.clean(name),)
    c.execute(query, param)

    DB.commit()
    DB.close()


def createTournament(name):
    # Creates a new tournament

    DB, c = connect()

    query = "INSERT INTO Tournaments VALUES(default, %s);"
    param = (bleach.clean(name),)
    c.execute(query, param)

    DB.commit()
    DB.close()


def tournamentReg(tournament, player):
    # Registers a player into a created tournament

    DB, c = connect()

    query = "INSERT INTO TournamentRegistration VALUES(default, %r, %r);"
    param = (tournament, player)
    c.execute(query, param)

    DB.commit()
    DB.close()


# =========== Utility functions ===========

def countPlayers():
    """Returns the number of players currently registered."""
    DB, c = connect()

    query = "SELECT count(players.id) as player_count from players;"

    c.execute(query)
    count = c.fetchall()
    count = count[0][0]

    DB.close()
    return count


def reportMatch(tournament, winner, loser, matchResult):
    """Records the outcome of a single match between two players."""
    # **Note** pass 0 as loserVal in reporting a bye

    # Check if winner/ loser the same
    if winner == loser:
        raise RuntimeError("Winner and loser cannot be the same")

    # Test for rematch between players
    checkRematch(winner, loser)

    DB, c = connect()

    query = "INSERT INTO matches VALUES(default, %s, %s, %s, %s);"
    try:
        # insert a bye into matches
        if matchResult == 'bye':
            c.execute(query, (tournament, winner, NULL, 1))
            c.execute("INSERT INTO byeLog VALUES(default, '%r', '%r')" %
                      (tournament, winner))

        # insert draw
        elif matchResult == 'draw':
            draw_param = (tournament, winner, loser, 0.5)
            c.execute(query, draw_param)

        # insert a win/loss
        elif matchResult == 'win' or matchResult == 'loss':
            win_param = (tournament, winner, loser, 1)
            c.execute(query, win_param)

        DB.commit()
        DB.close()
    except:
        raise RuntimeError(
            "An error occurred when reporting match. Please try again.")


# Need to chk tournamentID to fully support multiple tournaments
def checkRematch(winner, loser):
    DB, c = connect()

    query = "SELECT player1, player2 from Matches;"
    c.execute(query)
    res = c.fetchall()

    for i in res:
        if (winner == i[0] or winner == i[1]) and (loser == i[0] or loser == i[1]):
            raise RuntimeError("Cannot play rematch")
    DB.close()


def byeEligible(tournamentId, player):
    # Tests whether player has already been granted a bye

    DB, c = connect()

    query = "SELECT * from byeLog where tournament_id = %s and player_id = %s;"
    param = (tournamentId, player)
    c.execute(query, param)
    temp = c.fetchall()

    # test if player already has a bye.
    if temp == []:
        return True
    else:
        return False


def playerStandings(tournamentId):
    """Returns a list of the players and their win records, sorted by wins."""
    # Returns standings for tournament number given

    t = tournamentId
    DB, c = connect()

    # c.execute("SELECT * from v_PlayerStandings")
    # This is a monstrosity but I couldn't figure out how to pass an argument to my sql in order to support multiple tournaments-- so this is the view v_playerStandings with arg passing.
    # Can you suggest how this should be done?

    player_info = "SELECT players.id as player_id, players.name, "
    wins = "(SELECT COALESCE(wins, 0) as wins
             FROM(SELECT sum(matches.matchValue) as wins
                  from Matches where players.id=matches.player1
                  and matches.tournament_id= % s) as wins), "
    totalMatches = "(select * from (SELECT count(matches) as totalMatches
                                    from Matches where((players.id=matches.player1
                                                        or players.id=matches.player2)
                                                       and matches.tournament_id= % s)) as totalMatches where totalMatches != 0) "
    fromAndfilters = "from Players, Tournaments where tournaments.id = %s
    and (SELECT count(matches) as totalMatches
         from Matches where((players.id=matches.player1 or players.id=matches.player2)
                            and matches.tournament_id= % s)) != 0 "
    odering = "ORDER BY wins desc"
    query = player_info + wins + totalMatches + fromAndfilters + odering

    param = (t, t, t, t)

    c.execute(query, param)
    standings = c.fetchall()
    DB.close()
    return standings


def swissPairings(tournamentId):
    """Returns a list of pairs of players for the next round of a match."""
    # Returns pairings for tournament number given
    DB, c = connect()

    # Could repeatedly (SELECT ... limit 2 offset N)-- instead calling all in
    # one DB op, then splitting. More efficient?
    t = tournamentId
    player_info = "SELECT players.id as player_id, players.name, "
    wins = "(SELECT COALESCE(wins, 0) as wins
             FROM(SELECT sum(matches.matchValue) as wins
                  from Matches where players.id=matches.player1
                  and matches.tournament_id= % s) as wins), "
    totalMatches = "(select * from (SELECT count(matches) as totalMatches
                                    from Matches where((players.id=matches.player1
                                                        or players.id=matches.player2)
                                                       and matches.tournament_id= % s)) as totalMatches where totalMatches != 0) "
    fromAndfilters = "from Players, Tournaments where tournaments.id = %s
    and (SELECT count(matches) as totalMatches
         from Matches where((players.id=matches.player1 or players.id=matches.player2)
                            and matches.tournament_id= % s)) != 0 "
    odering = "ORDER BY wins desc"
    query = player_info + wins + totalMatches + fromAndfilters + odering

    param = (t, t, t, t)

    c.execute(query, param)
    standings = c.fetchall()

    # Declare utils
    pairings = []
    index = 0
    i = 0
    j = 0

    # Test if no players returned
    if len(standings) == 0:
        raise RuntimeError("No players to pair.")

    # Even cases:
    if len(standings) % 2 == 0:
        index = len(standings)/2
        while i < index:
            # so hackish... issue resulting from not passing arg to a view or
            # function in sql.
            a, s, d, f = standings[j]
            q, w, e, r = standings[j+1]
            temp1 = a, s
            temp2 = q, w
            pairings.append(temp1 + temp2)
            i += 1
            j += 2

    # Odd cases:
    elif len(standings) % 2 != 0:
        index = math.floor(len(standings)/2)

        # Forward chk if last player is eligible for a bye. Assign bye if so,
        # move up and rep if not.
        i = 1
        while i <= len(standings):
            if byeEligible(tournamentId, standings[len(standings)-i][0]):
                reportMatch(
                    tournamentId, standings[len(standings)-i][0], 0, 'bye')
                print "Player %r assigned a bye." % standings[len(standings)-i][0]
                i = 0
                break
            i += 1

        # Assign pairings
        i = 0
        while i < index:
            a, s, d, f = standings[j]
            q, w, e, r = standings[j+1]
            temp1 = a, s
            temp2 = q, w
            pairings.append(temp1 + temp2)
            i += 1
            j += 2

    DB.close()
    return pairings
