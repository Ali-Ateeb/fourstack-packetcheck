# PacketCheck

PacketCheck is an offline command-line prototype for reviewing fictional clinic
handoffs. It highlights passages about a callback channel, a requested visit
window and supporting records. A field without a clear match goes to human
review. The tool never checks the attachment itself or verifies whether contact
information is accurate.

## Run

Use Python 3.10 or newer. From this folder, run:

```sh
python packetcheck.py demo all-fields
python packetcheck.py demo missing-records
python packetcheck.py demo out-of-vocabulary
python packetcheck.py evaluate
```

The demo takes only built-in fictional cases. It runs locally without
dependencies, network access or a connection to patient records.

## Method and evaluation

A Naive Bayes text classifier learns from 17 short synthetic phrases across
three administrative categories and a background category. It abstains on
weak scores, close scores, questions and common uncertainty or negation cues.
Each reported field comes with the original matched sentence.

On eight synthetic packets excluded from training, seven matched all expected
fields exactly. Across the packets, the model found 9 of 12 expected fields
and produced zero extra matches. All three misses came from one paraphrased
example using unfamiliar language. The dataset and metric are reproducible
with the evaluation command. These author-created cases measure only the
prototype's behavior on the included examples.

A coordinator could use a future version to direct attention to missing
administrative evidence. Wrong matches could hide a missing item, and
unfamiliar wording could create unnecessary review work. This prototype has
no clinical validation, supports only a small set of English phrases and
leaves administrative and clinical decisions to people. A next iteration
would add independently authored fictional cases with conflicting statements,
varying dialects and more ways of expressing uncertainty.

## Competition status and disclosure

Codex created the prototype, synthetic examples and documentation on
November 8, 2026. The training and evaluation examples were authored for
this prototype. No earlier team product, personal contribution claim or real
patient data was used. The organizer permits previously started projects and
disclosed AI assistance. The submission window begins November 9 at 10:00 PKT.
The [88-second demo](./packetcheck-demo.webm) shows actual command output for
a complete packet, a missing attachment, an unfamiliar paraphrase and the
evaluation. Human review, account terms, full eligibility and Devpost
submission remain pending.

[AI for Medicine rules](https://ai-for-medicine.devpost.com/rules)
