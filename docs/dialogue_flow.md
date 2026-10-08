# Dialogue frame and flow

Each session stores current_entity, previous_question, previous_answer,
detected_intent and the last six message entries. State is in memory and is
lost when the server restarts. Browser tabs use separate random session IDs.

1. Detect greeting, help, complete goodbye expression or fact question.
2. For a question, replace supported pronouns with the current KB entity.
3. Query a disease entity and supported relation in the CSV.
4. On success, update the current entity and return the stored value.
5. Otherwise retrieve documents, select evidence and extract an answer.
6. An IR answer clears the prior healthcare entity. Save the latest turn.

Example: symptoms of Diabetes -> current_entity=Diabetes -> its treatment
-> Diabetes/treatment -> Who created Python? -> Document Retrieval,
Guido van Rossum, current_entity=None.

Limitations: simple pronouns only, no general coreference model, no persistent
session database or expiry policy. Sessions are intended for a local demo.
