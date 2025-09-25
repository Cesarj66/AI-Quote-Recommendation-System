### 🔹**Extractor**

**Task:**  
Given wiki-style text, extract the **most paradoxical, striking statement** that can be found within the text. Ideally declarative, self-contained, and succinct.

- Use **ellipses or square brackets** to reduce the size to one clause and improve standalone readability.
- **Preserve original wording exactly.**

---

**Examples**

**Input:**  
Pure mathematics consists entirely of assertions to the effect that, if such and such a proposition is true of anything, then such and such another proposition is true of that thing. It is essential not to discuss whether the first proposition is really true, and not to mention what the anything is, of which it is supposed to be true. Both these points would belong to applied mathematics. We start, in pure mathematics, from certain rules of inference, by which we can infer that if one proposition is true, then so is some other proposition. These rules of inference constitute the major part of the principles of formal logic. We then take any hypothesis that seems amusing, and deduce its consequences. If our hypothesis is about anything, and not about some one or more particular things, then our deductions constitute mathematics. Thus mathematics may be defined as the subject in which we never know what we are talking about, nor whether what we are saying is true. People who have been puzzled by the beginnings of mathematics will, I hope, find comfort in this definition, and will probably agree that it is accurate.

**Output:**  
[M]athematics may be defined as the subject in which we never know what we are talking about, nor whether what we are saying is true.

---

**Input:**  
The human understanding when it has once adopted an opinion (either as being the received opinion or as being agreeable to itself) draws all things else to support and agree with it. And though there be a greater number and weight of instances to be found on the other side, yet these it either neglects and despises, or else by some distinction sets aside and rejects, in order that by this great and pernicious predetermination the authority of its former conclusions may remain inviolate.

**Output:**  
The human understanding when it has once adopted an opinion... draws all things else to support and agree with it.

---

**Input:**  
Therefore only an utterly senseless person can fail to know that our characters are the result of our conduct.

**Output:**
[O]nly an utterly senseless person can fail to know that our characters are the result of our conduct
