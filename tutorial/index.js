const mysql = require("mysql2");
require("dotenv").config();

// credentials for OpenAI
const openAiHeaders = {
  "Content-Type": "application/json",
  Authorization: `Bearer ${process.env.OPENAI_API_KEY}`,
};

// credentials for SingleStore
const dbInfo = {
  host: process.env.DB_HOST,
  port: process.env.DB_PORT,
  user: process.env.DB_USER,
  password: process.env.DB_PASS,
  database: process.env.DB_NAME,
  ssl: {},
};

console.log("DB_HOST:", process.env.DB_HOST);
console.log("DB_PORT:", process.env.DB_PORT);
console.log("DB_USER:", process.env.DB_USER);
console.log("DB_PASS:", process.env.DB_PASS ? "Loaded" : "Not Loaded"); // Hide actual password
console.log("DB_NAME:", process.env.DB_NAME);

// database table name
const TABLE_NAME = "myvectortable";

// open connection to SingleStore
const connection = mysql.createConnection(dbInfo);

// return embedding of text
async function createEmbedding(text) {
  let response = await fetch("https://api.openai.com/v1/embeddings", {
    method: "POST",
    headers: openAiHeaders,
    body: JSON.stringify({
      input: text,
      model: "text-embedding-ada-002",
    }),
  });
  if (response.ok) {
    return response.json().then((data) => {
      console.log(data);
      return data.data[0].embedding;
    });
  }
}

// get all data from SingleStore (list of objects)
async function selectAllData() {
  const query = `SELECT text, JSON_ARRAY_UNPACK(vector) as vector FROM ${TABLE_NAME}`;
  return new Promise((resolve, reject) => {
    connection.execute(query, (err, results) => {
      if (err) {
        reject("Error fetching data:", err);
        return;
      }
      resolve(results);
    });
  });
}

// insert data into SingleStore
function insertData(text, vector) {
  const query = `INSERT INTO ${TABLE_NAME} (text,vector) VALUES (?, JSON_ARRAY_PACK(?))`;
  connection.execute(query, [text, JSON.stringify(vector)], (err, results) => {
    if (err) {
      console.error("Error inserting data:", err);
      return;
    }
    console.log("Data inserted successfully:", results);
  });
}

// get embedding and insert data
async function processTextAndInsert(text) {
  try {
    const embedding = await createEmbedding(text);
    console.log(text, embedding);
    insertData(text, embedding);
  } catch (error) {
    console.error("Error processing text and inserting data:", error);
  }
}

async function main() {
  // console.log("Starting main function");
  // // Example usage
  // await processTextAndInsert("The die is cast.");
  // await processTextAndInsert("I came, I saw, I conquered");
  // await processTextAndInsert(
  //   "Fortune, which has a great deal of power in other matters but especially in war, can bring about great changes in a situation through very slight forces."
  // );

  let data = await selectAllData();
  console.log(data);

  // close the connection to the database
  connection.end();
}

main();
