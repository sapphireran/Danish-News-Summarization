# Closed-world lexicon

The gazette is small enough that a hand-written DA→EN table can cover
every content token. That is a party trick, not a translation system.

Properties that matter for the lab:

1. **Coverage is a number.** `python -m fjordpress lexicon` must print
   `coverage=1.000` on the committed stories. If a new sentence is
   added, the type list of OOVs is the review checklist.
2. **The map is many-to-one.** `en` / `et` / `en` (the article) collapse
   toward `a` / `the`. Round-tripping is supposed to look worse than
   the gold parallel.
3. **Names are identity.** `Lisbeth`, `Havnepladsen`, `Mågeø` pass
   through. That isolates *attrition from dropping sentences*, not
   from transliteration.
4. **Glosses are hyphenated when English needs a phrase.**
   `varmepumpe → heat-pump` keeps one English token so the reverse
   map can find it again.

The reverse table keeps the *first* Danish spelling that produced a
given gloss. That is arbitrary and documented.

This is also why the tokenizer had to accept `é`: Danish `én` / `ét`
are real words in the Stenmole vote sentence. A letter class of
`A-Za-zÆØÅ` silently turned `én` into `n`.
