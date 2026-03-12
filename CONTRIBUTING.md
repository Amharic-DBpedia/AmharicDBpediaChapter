# Amharic DBpedia Contributing Guidelines

-   [How to contribute](#how-to-contribute)
    -   [Bug reports](#bug-reports)
    -   [Feature requests](#feature-requests)
    -   [Contributing data, code, and
        documentation](#contributing-data-code-and-documentation)
        -   [Commit messages](#commit-messages)
-   [Release Process](#release-process)
-   [Versioning](#versioning)

## How to contribute

**Amharic DBpedia** is a community-driven initiative to build and
maintain a structured knowledge base for the Amharic language. We
welcome contributions from researchers, developers, and the open-source
community.

Thank you for considering contributing!

Please follow the guidelines below to ensure a smooth collaboration
process.

------------------------------------------------------------------------

## Bug reports

If you find a bug or data issue in **Amharic DBpedia**, please first
search the existing issues:

https://github.com/Amharic-DBpedia/AmharicDBpediaChapter/issues

If the issue has not been reported yet, please open a new issue and
include:

-   A clear description of the problem
-   Steps to reproduce the issue
-   Relevant dataset or entity examples
-   Expected vs. actual behavior

Providing detailed information helps maintainers reproduce and resolve
the issue faster.

------------------------------------------------------------------------

## Feature requests

If you would like to propose a new feature or improvement, please first
search the issue tracker to see if a similar idea already exists.

If not, open a new issue and describe:

-   The proposed feature or improvement
-   Why it is useful for Amharic DBpedia
-   Possible implementation ideas (optional)

Examples of feature requests include:

-   Adding new entity extraction pipelines
-   Improving ontology mappings
-   Adding new Amharic datasets
-   Enhancing data quality validation

------------------------------------------------------------------------

## Contributing data, code, and documentation

We welcome contributions in the following areas:

-   Knowledge graph data
-   Dataset improvements
-   Extraction pipelines
-   Documentation
-   Tools for Amharic NLP and knowledge extraction

To contribute:

1.  **Check existing forks**

See if someone is already working on the same feature:

https://github.com/Amharic-DBpedia/AmharicDBpediaChapter/network

2.  **Discuss your idea first**

Before implementing large changes, please open an issue and discuss your
approach with maintainers.

3.  **Fork the repository**

Create a fork of:

Amharic-DBpedia/AmharicDBpediaChapter

into your own GitHub account.

4.  **Create a dedicated branch**

Create a branch describing your change:

feature-add-new-entities\
bugfix-fix-ontology-links\
dataset-update-amharic-wikipedia

5.  **Make your changes**

You can commit to your branch as often as needed.

6.  **Test your changes**

Before submitting a pull request, please verify:

-   Data formatting is correct
-   RDF/JSON/CSV files are valid
-   No duplicate or inconsistent entries exist

7.  **Open a Pull Request**

Submit a pull request to the main repository and describe:

-   What your change introduces
-   Why it is needed
-   Which issue it addresses

Each pull request should focus on **one feature or fix**.

8.  **Code review**

Maintainers will review the pull request. If changes are requested,
update your branch and push again.

Once accepted, the pull request will be merged.

------------------------------------------------------------------------

### Commit messages

Please write clear and meaningful commit messages.

Recommended format:

summary

body

footer

Example:

Add Amharic Wikipedia entity mappings

This commit introduces new mappings between Amharic Wikipedia entities
and DBpedia ontology classes.

Fixes #42

Guidelines:

-   **Summary:** imperative form, \~50 characters
-   **Body:** explain what and why
-   **Footer:** reference issues

Examples:

Refs #123\
Fixes #45\
Closes #89

------------------------------------------------------------------------

## Release Process

New releases of **Amharic DBpedia** are coordinated by the project
maintainers.

Release planning may include:

-   Dataset updates
-   Ontology improvements
-   Extraction pipeline upgrades
-   Data quality improvements

------------------------------------------------------------------------

## Versioning

The project follows **Semantic Versioning**:

X.Y.Z

Where:

-   **X** -- Major release\
    Significant structural changes to the dataset or ontology

-   **Y** -- Minor release\
    Backward-compatible improvements or additions

-   **Z** -- Patch release\
    Bug fixes, corrections, and minor data updates
