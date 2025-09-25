**Prompt 1: Disqualifier – Filter Out Non-Quotables**  
**Task:** Given Wikipedia-style markdown, respond with either: **Quotable** or **Not Quotable**. Ignore formatting or syntax issues.

**Definitions:**

- **Quotable** = Actual writing meant to be read or spoken as content — including dialogue, narration, prose, or speech.
- **Not Quotable** = Meta-information, editorial notes, system messages, navigation elements, or anything clearly not meant as quoted content.

**Examples:**

```
// Quotable
**'''Gerald:''' I suppose society is wonderfully[2] delightful? <br> '''Lord Illingworth:''' '''To be in it is merely a bore. But to be out of it simply a tragedy.'''**
→ Quotable

// Not Quotable
**'''Warning''': This content is '''under review'''. <br> '''Note''': Formatting may change.**
→ Not Quotable

// Quotable
**'''From Stettin (wikipedia:Stettin) in the Baltic to Trieste (wikipedia:Trieste)...'''**
→ Quotable

// Not Quotable
'''Sean Bishop''' — Police Officer
→ Not Quotable
```
