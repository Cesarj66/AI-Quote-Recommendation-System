const axios = require("axios");
const cheerio = require("cheerio");

const WIKIQUOTE_API_URL = "https://en.wikiquote.org/w/api.php";

// Function to search for an author's page on Wikiquote
async function searchAuthor(author) {
    try {
        const response = await axios.get(WIKIQUOTE_API_URL, {
            params: {
                format: "json",
                action: "query",
                list: "search",
                srsearch: author,
                srnamespace: 0
            }
        });

        const results = response.data.query?.search;
        if (results && results.length > 0) {
            return results[0].title;
        } else {
            console.log(`No Wikiquote page found for ${author}.`);
            return null;
        }
    } catch (error) {
        console.error("Error searching Wikiquote:", error);
        return null;
    }
}

// Function to fetch quotes from Wikiquote
async function getQuotes(author, maxQuotes = 5) {
    const authorPage = await searchAuthor(author);
    if (!authorPage) return [];

    try {
        const response = await axios.get(WIKIQUOTE_API_URL, {
            params: {
                format: "json",
                action: "query",
                prop: "extracts",
                titles: authorPage,
                explaintext: 1
            }
        });

        const pages = response.data.query?.pages;
        const pageContent = Object.values(pages)[0]?.extract || "";

        // Split quotes by new lines and clean them
        let rawQuotes = pageContent.split("\n").map(q => cleanText(q));
        rawQuotes = rawQuotes.filter(q => q.length > 10); // Remove very short lines

        return rawQuotes.slice(0, maxQuotes);
    } catch (error) {
        console.error("Error fetching quotes:", error);
        return [];
    }
}

// Function to clean HTML and unnecessary spaces
function cleanText(text) {
    const $ = cheerio.load(text);
    return $.text().trim().replace(/\s+/g, " "); // Remove extra whitespace
}

// Export the functions
module.exports = { getQuotes };
