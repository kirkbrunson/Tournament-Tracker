#!/usr/bin/env python
#
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2
import bleach


def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    try:
        DB = psycopg2.connect("dbname=tournament")
        cursor = DB.cursor()
        return DB, cursor
    except:
        raise RuntimeError("An error occured, please try again")


def deleteMatches():
    """Remove all the match records from the database."""
    DB, c = connect()
    c.execute("TRUNCATE Matches CASCADE")
    DB.commit()
    DB.close()


def deletePlayers():
    """Remove all the player records from the database."""
    DB, c = connect()
    c.execute("TRUNCATE Players CASCADE")
    DB.commit()
    DB.close()


def countPlayers():
    """Returns the number of players currently registered."""
    DB, c = connect()
    c.execute("SELECT count(players.id) as player_count from players")
    count = c.fetchall()
    count = count[0][0]

    DB.close()
    return count


def registerPlayer(name):
    """Adds a player to the tournament database.

    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)

    Args:
      name: the player's full name (need not be unique).
    """

    DB, c = connect()
    query = "INSERT INTO players VALUES(default, %s);"
    param = (bleach.clean(name),)
    c.execute(query, param)
    DB.commit()
    DB.close()


def playerStandings():
    """Returns a list of the players and their win records, sorted by wins.
    The first entry in the list should be the player in first place or a player
    tied for first place if there is currently a tie.
    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """

    DB, c = connect()
    c.execute("SELECT * from v_PlayerStandings")
    standings = c.fetchall()
    DB.close()
    return standings


def reportMatch(winner, loser):
    """Records the outcome of a single match between two players.
    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """
    DB, c = connect()

    query = "INSERT INTO matches VALUES(default, %s, %s);"
    param = (winner, loser,)
    c.execute(query, param)

    DB.commit()
    DB.close()


def swissPairings():
    """Returns a list of pairs of players for the next round of a match.

    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.

    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """

    DB, c = connect()

    # Could repeatedly (SELECT ... limit 2 offset N)-- instead calling all in
    # one DB op, then splitting. More efficient?
    c.execute("SELECT id, name from v_PlayerStandings")
    standings = c.fetchall()

    # Declare utils
    pairings = []
    index = 0
    i = 0
    j = 0

    # Loop and through standings and assign pairings
    index = len(standings)/2
    while i < index:
        pairings.append(standings[j]+standings[j+1])
        i += 1
        j += 2

    DB.close()
    return pairings
