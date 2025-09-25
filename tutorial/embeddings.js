import { createClient } from "@supabase/supabase-js";
import OpenAI from "openai";

const supabaseUrl = "https://ekrumlfvpstscaavmdtx.supabase.co";
const supabaseKey =
  (process.env.SUPABASE_KEY = ``);
const supabase = createClient(supabaseUrl, supabaseKey);

const openai = new OpenAI({
  apiKey:
    (process.env.OPENAI_API_KEY = ``),
});

export default supabase;

export async function searchSimilarQuotes(query) {
  const queryEmbedding = await generateEmbedding(query);
  if (!queryEmbedding) {
    console.error("Failed to generate query embedding.");
    return [];
  }

  const { data, error } = await supabase
    .from("wikiquote_duplicate")
    .select("id, quote, embedding");

  if (error) {
    console.error("Error fetching quotes:", error);
    return [];
  }

  const results = data
    .map((row) => {
      try {
        const storedEmbedding = JSON.parse(row.embedding); // Convert stored embedding from string to array
        return {
          id: row.id,
          quote: row.quote,
          similarity: cosineSimilarity(queryEmbedding, storedEmbedding),
        };
      } catch (err) {
        console.error("Error parsing embedding for quote:", row.quote, err);
        return null;
      }
    })
    .filter((result) => result !== null); // Remove any failed parsing entries

  results.sort((a, b) => b.similarity - a.similarity);
  return results.slice(0, 5);
}

// Function to generate an embedding for a given text
export async function generateEmbedding(text) {
  try {
    const response = await openai.embeddings.create({
      model: "text-embedding-ada-002",
      input: text,
    });
    return response.data[0].embedding;
  } catch (error) {
    console.error("Error generating embedding:", error);
    return null;
  }
}

// Function to compute cosine similarity between two vectors
function cosineSimilarity(vecA, vecB) {
  const dotProduct = vecA.reduce((sum, val, i) => sum + val * vecB[i], 0);
  const normA = Math.sqrt(vecA.reduce((sum, val) => sum + val * val, 0));
  const normB = Math.sqrt(vecB.reduce((sum, val) => sum + val * val, 0));
  return dotProduct / (normA * normB);
}

// Example search
(async () => {
  const results = await searchSimilarQuotes("There is no reason to be happy");
  console.log(results);

  //   // inserting embeddings in database
  //   const { data, error } = await supabase
  //     .from("wikiquote_duplicate")
  //     .select("id, quote");

  //   if (error) {
  //     console.error("Error fetching quotes:", error);
  //     return [];
  //   }

  //   for (const row of data) {
  //     try {
  //       const embedding = await generateEmbedding(row.quote);
  //       await supabase
  //         .from("wikiquote_duplicate")
  //         .update({ embedding: JSON.stringify(embedding) })
  //         .eq("id", row.id);
  //     } catch (err) {
  //       console.error("Error updating embedding for quote:", row.quote, err);
  //     }
  //   }
})();
