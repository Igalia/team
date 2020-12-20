# Ballots

This application allows performing ballots.

## Idea

Companies that have spirit of cooperation take (at least some of) their decisions via discussions and democratic procedures such as ballots.

The simplest form of a ballot is a question that can be answered either yes or no.

## Models

This application is very simple.  Ballot (`ballots.models.Ballot`) groups Votes (`ballots.models.Vote`).  Both ballots and votes are linked to their owners (`people.models.Person`).

## Logic

The Our Ballots page (`ballots.views.home()`) displays the list of active ballots—that is, ones that have not yet reached their deadlines.

The Ballot page (`ballots.views.ballot()`) allows voting and shows the current status of the ballot.

Each user can create a new ballot, and also edit the ballot that they have created earlier.
