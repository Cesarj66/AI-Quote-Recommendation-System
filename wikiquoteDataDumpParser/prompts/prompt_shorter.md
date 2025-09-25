You will receive Wikipedia-style markdown text. Clean it using these rules:

1. Keep bold ('''like this''' – wiki-style triple apostrophes) only if it's **quotable** (an unusual, memorable bolded phrase).
2. Remove bold from names, labels, or non-quotable text.
3. Strip Wikipedia links `(wikipedia:XYZ)`, HTML comments, and entities like `&nbsp;`.
4. Delete HTML elements except `<p>`, `<br>`.
5. If multiple short bolded parts clearly form one quote, merge them.
6. If no quotable bolded text, respond: `No quotable text found.`

**Examples (Input → Output):**

// 1. bold used for name + fragment; no quote
**'''Actor 1''': That is my catchphrase, it's '''clobberin' time'''! <!-- comment --> <\br> '''Actor 2''': Okay.** → No quotable text found

// 2. clean comment + ref; one quotable bold
**'''Gerald:''' I suppose society is wonderfully[2] delightful? <!-- comment --> <br /> '''Lord Illingworth:''' '''To be in it is merely a bore. But to be out of it simply a tragedy.'''** → Gerald: I suppose society is wonderfully delightful? <br /> Lord Illingworth: '''To be in it is merely a bore. But to be out of it simply a tragedy.'''

// 3. only labels and metadata in bold; no quote
**'''Warning''': This content is '''under review'''. <br> '''Note''': Formatting may change.** → No quotable text found

// 4. strip links; one quotable bold
**'''From Stettin (wikipedia:Stettin) in the Baltic to Trieste (wikipedia:Trieste) in the Adriatic an iron curtain (wikipedia:Iron curtain) has descended across the Continent.'''** → From Stettin in the Baltic to Trieste in the Adriatic an iron curtain has descended across the Continent.

// 5. clean extras; merge into quote
**'''Truth''' (wikipedia:Truth) is a '''slippery''' <!-- cliché --> thing, '''isn't it?'''** → '''Truth is a slippery thing, isn't it?'''

// 6. discard label; quote
**'''Tip''': Stay alert. <br> '''Cicero''': '''A room without books is like a body without a soul.'''** → Cicero: '''A room without books is like a body without a soul.'''
