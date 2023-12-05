# People

This application manages the actual people, i. e., the company staff and the organisational structure of the company.  People may be grouped in teams, and also they have "levels" which form the "career ladder" or other progression, whatever sense it would imply in the actual company.

The company is the people, which is why this application works like a "hub" for all other parts: all other applications have connections to either people or teams.  When other applications need to address a person in a company, they should refer to an instance of `people.models.Person` model.

Due to its central role in the system, the `people` application defines the top-level menu, and also it provides some "root level" URLs in the URL scheme.
