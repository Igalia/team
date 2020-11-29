# Team

This is a hobby project for building a simple web service that would allow evaluating and analysing the expertise of a project team.

The service is built on Django framework.

## Idea

Teams that work in large areas of expertise sometimes come to point when they need to understand their capabilities.

The whole area of expertise is divided into a set of sub-areas, or skills.  Each team member can then tell how good they are in each skill, and how much they would want to use that skill more.  After all members have assessed themselves, it becomes possible to see expertise of the team as a whole: which skills are represented better or worse, which skills are more or less interesting to the people, and where there is room for improvement.

## Implementation

### Models

The team member is represented by `people.models.Person` model.

The skills application defines data on areas of expertise.  Skills (`skills.models.Skill`) represent sub-areas of knowledge, they are grouped into Categories (`skills.models.Category`).

The Measurement (`skills.models.Measurement`) represents an answer to a question: *"Regarding skill X, how good are you in it, and how much would you like to use it in your work?"*  The answer consists of two values: the perceived level of knowledge and the desire to use or learn that skill.  Several measurements for different skills are grouped in the `skills.models.PersonAssessment` model, which in its turn refers to a `people.models.Person` and contains date of recording.

### Logic

The Self Assessment page (`skills.views.assess()` view) displays a form that lists all available skills, so the entire assessment can be done with the single submission.

The Our Skills page (`skills.views.home()`) loads the latest assessments for each team member, and displays a table with team stats.  For each skill, numbers of people at each level of knowledge and interest are displayed; also some aggregated values are shown.

The Skill page (`skills.views.skill()`) displays full details for a single skill: what are levels of knowledge and interest for each team member.

The Person page (`skills.views.person()`) displays full details for a single team member: what are their levels of knowledge and interest for each skill.
