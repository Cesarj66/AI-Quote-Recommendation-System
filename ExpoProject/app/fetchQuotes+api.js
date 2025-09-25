import { createClient } from "@supabase/supabase-js";
import { OpenAI } from "openai";

const nodeMap = {
  all: "all",
  // Types
  Person: "B1",
  Work: "B2",

  // Subtypes (Person)
  Novelist: "B1a",
  Poet: "B1b",
  Playwright: "B1c",
  Philosopher: "B1d",
  Politician: "B1e",
  "Religious Figure": "B1f",
  Scientist: "B1g",
  Artist: "B1h",
  Composer: "B1i",
  Activist: "B1j",
  Critic: "B1k",
  Historian: "B1l",
  Economist: "B1m",
  Mathematician: "B1n",
  Inventor: "B1o",
  Scholar: "B1p",
  Journalist: "B1q",
  Director: "B1r",
  Actor: "B1s",
  "Military Leader": "B1t",
  Diplomat: "B1u",
  Orator: "B1v",
  Comedian: "B1w",
  "Public Intellectual": "B1x",
  Educator: "B1y",
  "Fictional Characters": "B1z",
  Programmer: "B1aa",
  Entrepeneur: "B1ab",

  // Subtypes (Work)
  Literature: "B2a",
  Novel: "B2a1",
  Poem: "B2a2",
  Play: "B2a3",
  Essay: "B2a4",
  Proverb: "B2a5",
  "Philosophical Work": "B2b",
  "Political Text": "B2c",
  Film: "B2d",
  "Television Show": "B2e",
  Newspaper: "B2f",

  // Languages
  English: "C1",
  French: "C2",
  German: "C3",
  Russian: "C4",
  Italian: "C5",
  Chinese: "C6",
  Japanese: "C7",
  Arabic: "C8",
  Latin: "C9",
  "Classical Greek": "C10",
  Spanish: "C11",
  Portuguese: "C12",
  Other: "C13",
};

const eraRanges = {
  all: [-5000, 2025],
  "Ancient (before 500 BCE)": [-5000, -500],
  "Classical (500 BCE–500 CE)": [-500, 500],
  "Early Medieval (500–1000)": [500, 1000],
  "High Medieval (1000–1300)": [1000, 1300],
  "Late Medieval (1300–1500)": [1300, 1500],
  "14th and 15th century (1300–1500)": [1300, 1500],
  "16th century (1500–1600)": [1500, 1600],
  "17th century (1600–1700)": [1600, 1700],
  "18th century (1700–1800)": [1700, 1800],
  "19th Century (1800–1900)": [1800, 1900],
  "(1900–1945)": [1900, 1945],
  "(1945–1999)": [1945, 1999],
  "21st Century (2000–Present)": [2000, new Date().getFullYear()],
};

function safeContains(query, field, value) {
  if (
    value !== undefined &&
    value !== null &&
    value !== "" &&
    value !== "all"
  ) {
    return query.contains(field, [value]);
  }
  return query;
}

// https://supabase.com/docs/reference/javascript/initializing
// https://docs.expo.dev/router/reference/api-routes/#errors

const supabaseUrl = "https://ekrumlfvpstscaavmdtx.supabase.co";
const supabaseKey = process.env.EXPO_PUBLIC_SUPABASE_KEY;

const openai = new OpenAI({
  apiKey: process.env.EXPO_PUBLIC_OPEN_AI_KEY,
});

// Function to compute cosine similarity between two vectors
function cosineSimilarity(vecA, vecB) {
  const dotProduct = vecA.reduce((sum, val, i) => sum + val * vecB[i], 0);
  const normA = Math.sqrt(vecA.reduce((sum, val) => sum + val * val, 0));
  const normB = Math.sqrt(vecB.reduce((sum, val) => sum + val * val, 0));
  return dotProduct / (normA * normB);
}

export async function searchSimilarQuotes(quote, filtersObjMapped, supabase) {
  if (!quote || quote.trim() === "") {
    console.error("Query is empty! Please enter a quote.");
    return [];
  }

  console.log("Searching for similar quotes to:", quote);
  const queryEmbedding = await generateEmbedding(quote);
  if (!queryEmbedding) {
    console.error("Failed to generate query embedding.");
    return [];
  }

  const { data: user, error: userError } = await supabase.auth.getUser();
  if (userError) {
    console.error("Error fetching user:", userError);
    return [];
  }

  const userId = user.user.id; // Get the current user's ID

  let query = supabase.from("quotes").select(`
    id,
    page_id,
    page_name,
    quote,
    hierarchy,
    quote_info,
    emotions,
    embedding,
    likes_duplicate(user_id),
    summary
  `);

  const { data: quotesData, error: quotesError } = await query;

  if (quotesError) {
    console.error("Error fetching quotes:", quotesError);
    return [];
  }

  const pageIds = quotesData.map((q) => q.page_id).filter((id) => id !== null);

  // console.log("Page IDs:", pageIds);

  const { data: pagesData, error: pagesError } = await supabase
    .from("pages")
    .select("id, page_name, type, language_region, era")
    .in("id", pageIds);

  if (pagesError) {
    console.error("Error fetching pages:", pagesError);
    return [];
  }

  const pagesById = Object.fromEntries(
    pagesData.map((page) => [page.id, page])
  );

  const fullResults = quotesData.map((quote) => ({
    ...quote,
    page: pagesById[quote.page_id] || null, // attach page manually
  }));

  const results = fullResults
    .map((row) => {
      try {
        const storedEmbedding = JSON.parse(row.embedding);
        return {
          id: row.id,
          title: row.page_name || "",
          quote: row.quote,
          hierarchy: row.hierarchy,
          quote_info: row.quote_info,
          Emotions: row.emotions,
          similarity: cosineSimilarity(queryEmbedding, storedEmbedding),
          isLiked: row.likes_duplicate.some((like) => like.user_id === userId),
          page: row.page,
          summary: row.summary,
        };
      } catch (err) {
        console.error("Error parsing embedding for quote:", row.quote, err);
        return null;
      }
    })
    .filter((result) => result !== null)
    .filter((result) => {
      const page = result.page;

      if (
        filtersObjMapped.title !== "" &&
        page.page_name !== filtersObjMapped.title
      ) {
        return false;
      }

      // if (filtersObjMapped.type !== "all" && page.type !== filtersObjMapped.type) {
      //   return false;
      // }

      if (
        filtersObjMapped.lang !== "all" &&
        page.language_region !== filtersObjMapped.lang
      ) {
        return false;
      }

      if (
        page.era === undefined ||
        page.era === null ||
        page.era < filtersObjMapped.era[0] ||
        page.era > filtersObjMapped.era[1]
      ) {
        return false;
      }

      return true;
    })
    .sort((a, b) => b.similarity - a.similarity);

  // console.log("Results after filtering:", results);

  result_slice = results.slice(0, 5);

  console.log("Sliced results:", result_slice);

  return result_slice;
}

// Function to generate an embedding for a given text
export async function generateEmbedding(text) {
  try {
    const response = await openai.embeddings.create({
      model: "text-embedding-3-small",
      input: text,
    });
    return response.data[0].embedding;
  } catch (error) {
    console.error("Error generating embedding:", error);
    return null;
  }
}

export async function GET(request) {
  const authorization = request.headers.get("Authorization");
  if (!authorization)
    return new Response(JSON.stringify({ error: "Unauthorized" }), {
      status: 401,
      headers: { "Content-Type": "application/json" },
    });

  // You can now use it within a Supabase Client
  const supabase = createClient(supabaseUrl, supabaseKey, {
    global: {
      headers: {
        Authorization: authorization,
      },
    },
  });
  const url = new URL(request.url);
  const quote = url.searchParams.get("quote");
  const filters = url.searchParams.get("filters");
  console.log(filters);
  // turn into object
  const filtersObj = JSON.parse(filters);
  // convert with nodeMap
  const filtersObjMapped = Object.fromEntries(
    Object.entries(filtersObj).map(([key, value]) => {
      if (key === "type") {
        return [key, nodeMap[value]];
      } else if (key === "subtype") {
        return [key, nodeMap[value]];
      } else if (key === "lang") {
        return [key, nodeMap[value]];
      } else if (key === "era") {
        return [key, eraRanges[value]];
      } else {
        return [key, value];
      }
    })
  );
  console.log("filtersObjMapped");
  console.log(filtersObjMapped);

  console.log(quote);
  //   return;
  console.log("GET request received");

  const similarQuotes = await searchSimilarQuotes(
    quote,
    filtersObjMapped,
    supabase
  );

  // console.log("Similar quotes:\n", similarQuotes);

  data = similarQuotes;

  return new Response(JSON.stringify({ data }), {
    status: 200,
    headers: { "Content-Type": "application/json" },
  });
}
