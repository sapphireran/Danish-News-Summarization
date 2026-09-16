# Documentation index

Personal write-up of the 2023 ITU Danish news summarization project. Start at the repository [README](../README.md) if you want commands; start here if you want the argument.

| Doc | Question it answers |
| --- | --- |
| [00-overview.md](00-overview.md) | Why translate–summarize–translate instead of annotating? |
| [01-pipeline.md](01-pipeline.md) | What does each root script read and write? |
| [02-chunking-and-length.md](02-chunking-and-length.md) | How are long articles packed into 512-token windows? |
| [03-models-and-hyperparameters.md](03-models-and-hyperparameters.md) | Which checkpoints and knobs were used? |
| [04-dataset-schema.md](04-dataset-schema.md) | What are the CSV columns and Hub dataset fields? |
| [05-evaluation.md](05-evaluation.md) | What do ROUGE and BERTScore mean here? |
| [06-limitations-and-ethics.md](06-limitations-and-ethics.md) | How can silver labels lie or leak? |
| [07-reproduction.md](07-reproduction.md) | What can you rerun on a laptop vs a GPU box? |
| [08-troubleshooting.md](08-troubleshooting.md) | What breaks first? |
| [09-glossary.md](09-glossary.md) | What do the short words mean in this repo? |

Runnable companions live in [../examples/](../examples/README.md).
