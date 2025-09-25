const axios = require("axios");
const fs = require("fs");
const { JSDOM } = require("jsdom"); // Use JSDOM to parse and clean HTML

const WIKIQUOTE_API_URL = "https://en.wikiquote.org/w/api.php";

async function searchTitle(title) {
    try {
        const response = await axios.get(WIKIQUOTE_API_URL, {
            params: {
                format: "json",
                action: "query",
                titles: title,
                prop: "extracts",
                exintro: true
            }
        });

        const pages = response.data.query.pages;
        const pageId = Object.keys(pages)[0];

        if (pageId === "-1") {
            console.log("No results found.");
            return null;
        }

        return pageId;
    } catch (error) {
        console.error("Error searching Wikiquote:", error);
        return null;
    }
}

async function getQuotes(title) {
    try {
        const pageId = await searchTitle(title);
        if (!pageId) return;

        const response = await axios.get(WIKIQUOTE_API_URL, {
            params: {
                format: "json",
                action: "query",
                prop: "extracts",
                pageids: pageId
            }
        });

        let rawQuotes = response.data.query.pages[pageId].extract;

        // Clean the quotes using JSDOM
        const dom = new JSDOM(rawQuotes);
        const cleanQuotes = dom.window.document.body.textContent.trim();

        // Format the output
        const output = `Quotes from ${title}:\n\n${cleanQuotes.replace(/\n+/g, "\n")}\n`;

        // Write to a file
        fs.writeFileSync("quotes.txt", output, "utf8");
        console.log(`Quotes saved to quotes.txt`);

    } catch (error) {
        console.error("Error fetching quotes:", error);
    }
}

module.exports = { getQuotes };
