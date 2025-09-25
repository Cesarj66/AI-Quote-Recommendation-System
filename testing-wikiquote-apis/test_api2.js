const fs = require("fs");
const { getQuotes } = require("./wikiquoteApi2");

// Function to fetch and save quotes
async function fetchAndSaveQuotes(author) {
    const quotes = await getQuotes(author, 20);

    if (quotes.length === 0) {
        console.log(`No quotes found for ${author}.`);
        return;
    }

    // Format output
    const output = `Quotes from ${author}:\n\n` + quotes.map(q => `"${q}"`).join("\n") + "\n";

    // Write to file
    fs.writeFileSync("quotes.txt", output, "utf8");
    console.log(`Quotes saved to quotes.txt`);
}

// Fetch quotes for Albert Einstein as a test
fetchAndSaveQuotes("Julius Caesar");
