## 🔹 Prompt 2: **Formatter**

**Task:** Clean up wiki-style text.

---

### 🚫 Remove:

- HTML comments (`<!-- ... -->`)
- Wikipedia links (`(wikipedia:XYZ)`)
- All HTML except `<br>`
- Entities (`&nbsp;`, `&lt;`, etc.)
- Extra/prefatory non-quote text

---

### ✅ Keep:

- `<br>`
- **Speaker names** in dialogue (e.g. `Kruge:`)
  - ✅ `Kruge: They're hiding!`
  - ❌ `They're hiding!`

---

### 🎯 Output:

- Clean, display-ready quote

---

### 🔹 Examples

#### 🧼 Basic Cleanup

**Input:**

```
<b>Truth</b><!-- obviously --> is what matters most when discussing the (wikipedia:Moon) Moon — not myths&nbsp;or&nbsp;legends.<br><p>Let that be clear.</p>
```

**Output:**

```
Truth is what matters most when discussing the Moon — not myths or legends. <br> Let that be clear.
```

---

#### 🗣️ Dialogue

**Input:**

```
<p>Torg: My lord, the ship appears to be <!-- clearly --> deserted.</p>
Kruge: How can that be? They're (wikipedia:Hiding) hiding!
<b>Torg:</b> Yes,&nbsp;sir. But the bridge is run by <i>computer</i>. It is the only thing speaking.<br>
Kruge: Speaking? Let me hear.
```

**Output:**

```
Torg: My lord, the ship appears to be deserted.
Kruge: How can that be? They're hiding!
Torg: Yes, sir. But the bridge is run by computer. It is the only thing speaking.
Kruge: Speaking? Let me hear.
```
