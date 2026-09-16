# Example tests

These tests cover the CPU-only helpers. They do not download models.

```bash
python -m unittest discover -s examples/tests -t examples
```

`discover` is pointed at `examples/` so `scripts.text_lib` can be
imported as a package. The tests also append `examples/scripts` to
`sys.path` and import `text_lib` directly, which matches how the CLIs
run.
