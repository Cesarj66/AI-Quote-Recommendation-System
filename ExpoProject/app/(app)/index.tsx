import { FilterComponent } from "@/components/FilterComponent";
import { ThemedTextInput } from "@/components/ThemedTextInput";
import { authenticatedFetch, supabase } from "@/utils/supabase";
import { useThemeColor } from "@/hooks/useThemeColor";
import { useFocusEffect } from "@react-navigation/native";
import React, { useState, useCallback } from "react";
import {
  ActivityIndicator,
  Button,
  FlatList,
  ScrollView,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from "react-native";
import Constants from "expo-constants";

const API_URL = "https://api.routes.expo.app";

const generateAPIUrl = (relativePath: string) => {
  console.log("Constants", Constants.experienceUrl);

  const origin =
    Constants?.experienceUrl?.replace("exp://", "http://") || API_URL;

  const path = relativePath.startsWith("/") ? relativePath : `/${relativePath}`;

  if (process.env.NODE_ENV === "development") {
    return origin?.concat(path);
  }

  if (!API_URL) {
    throw new Error("API_URL environment variable is not defined");
  }

  return API_URL.concat(path);
};

interface AIResponse {
  title: string;
  content: string;
  thoughts: string;
  post_rate: number;
}
// https://docs.expo.dev/router/reference/api-routes/#create-an-api-route
// https://reactnative.dev/docs/flatlist#example

type Quote = {
  title: string;
  quote: string;
  hierarchy: string | null;
  quote_info: string | null;
  Emotions: { labels: string[]; scores: number[] };
  id: number;
  isLiked: boolean;
  summary: string | null;
};

function renderWikiBold(text: string) {
  const parts = text.split(/'''/);
  return parts.map((part, index) => {
    if (index % 2 === 1) {
      // Odd index -> between ''' symbols => bold
      return (
        <Text key={index} style={{ fontWeight: "bold" }}>
          {part}
        </Text>
      );
    } else {
      // Even index -> normal text
      return <Text key={index}>{part}</Text>;
    }
  });
}

async function fetchModel(
  setModelOutput: React.Dispatch<React.SetStateAction<string>>,
  inputTestModel: string
) {
  console.log("fetching testing: ", inputTestModel);
  const response = await authenticatedFetch(
    generateAPIUrl(`/fetchModel?input=${encodeURIComponent(inputTestModel)}`)
  );
  const data = await response.json();

  console.log("fetchModel response: ", data);
  setModelOutput(data.data);
}

async function fetchQuotes(
  setQuotes: React.Dispatch<React.SetStateAction<Quote[]>>,
  inputQuote: string,
  filter: {
    title: string;
    type: string;
    subtype: string;
    lang: string;
    era: string;
    emotionalScore: string;
  }
) {
  console.log("fetching quotes", inputQuote, filter);
  const response = await authenticatedFetch(
    generateAPIUrl(
      `/fetchQuotes?quote=${encodeURIComponent(
        inputQuote
      )}&filters=${encodeURIComponent(JSON.stringify(filter))}`
    )
  );
  const data = await response.json();
  const quotesArray = data.data;
  setQuotes(quotesArray);
}

const emotions_dict = {
  // positive
  admiration: "👏",
  amusement: "😂",
  approval: "👍",
  caring: "🤗",
  desire: "😍",
  excitement: "🤩",
  gratitude: "🙏",
  joy: "😀",
  love: "❤️",
  optimism: "🤞",
  pride: "😌",
  relief: "😅",
  // negative
  anger: "😡",
  annoyance: "😒",
  disappointment: "😞",
  disapproval: "👎",
  disgust: "🤢",
  embarrassment: "😳",
  fear: "😨",
  grief: "😢",
  nervousness: "😬",
  remorse: "😔",
  sadness: "😞",
  // ambiguous
  confusion: "😕",
  curiosity: "🤔",
  realization: "💡",
  surprise: "😮",
  // neutral
  neutral: "😐",
};

export default function App() {
  const [quotes, setQuotes] = useState<Quote[]>([]);
  const [hasSearched, setHasSearched] = useState(false);

  type ItemProps = { quote: Quote; refetchQuotes: () => void };

  const Item = ({ quote }: ItemProps) => {
    const [modelOutput, setModelOutput] = useState<string>("");
    const [showFullQuote, setShowFullQuote] = useState(false);

    const emotions = quote.Emotions;

    const positiveEmotions = [
      "admiration",
      "amusement",
      "approval",
      "caring",
      "desire",
      "excitement",
      "gratitude",
      "joy",
      "love",
      "optimism",
      "pride",
      "relief",
    ];

    const negativeEmotions = [
      "anger",
      "annoyance",
      "disappointment",
      "disapproval",
      "disgust",
      "embarrassment",
      "fear",
      "grief",
      "nervousness",
      "remorse",
      "sadness",
      "confusion",
    ];

    let itemStyle = styles.itemNeutral;

    console.log(emotions?.labels[0]);

    if (emotions?.labels.length > 1) {
      if (positiveEmotions.includes(emotions?.labels[1])) {
        itemStyle = styles.itemPositive;
      } else if (negativeEmotions.includes(emotions?.labels[1])) {
        itemStyle = styles.itemNegative;
      }
    }
    if (emotions?.labels.length > 0) {
      if (positiveEmotions.includes(emotions?.labels[0])) {
        itemStyle = styles.itemPositive;
      } else if (negativeEmotions.includes(emotions?.labels[0])) {
        itemStyle = styles.itemNegative;
      }
    }

    const [isLiked, setIsLiked] = useState(quote.isLiked);
    const [isLiking, setIsLiking] = useState(false);
    const [isModelLoading, setIsModelLoading] = useState(false);

    return (
      <View
        style={[
          itemStyle,
          {
            flexDirection: "row",
            justifyContent: "space-between",
            alignItems: "flex-start",
          },
        ]}
      >
        {/* Left Section */}
        <View style={{ flex: 4, flexDirection: "row", flexWrap: "wrap" }}>
          {/* Quote and Info block */}
          <View style={{ flex: 5, paddingRight: 10 }}>
            <Text style={styles.quote}>{quote.title}</Text>

            {quote.summary ? (
              <>
                <Text style={styles.quote}>{quote.summary}</Text>
                {!showFullQuote && (
                  <Text
                    style={styles.showMore}
                    onPress={() => setShowFullQuote(true)}
                  >
                    Show full quote
                  </Text>
                )}
                {showFullQuote && (
                  <>
                    <Text style={styles.quote}>
                      {renderWikiBold(quote.quote)}
                    </Text>
                    <Text
                      style={styles.showMore}
                      onPress={() => setShowFullQuote(false)}
                    >
                      Hide
                    </Text>
                  </>
                )}
              </>
            ) : (
              <Text style={styles.quote}>{renderWikiBold(quote.quote)}</Text>
            )}

            <Text style={styles.hierarchy}>{quote.hierarchy}</Text>
            <Text style={styles.quote_info}>{quote.quote_info}</Text>
            {modelOutput ? (
              <Text style={{ marginTop: 10, fontStyle: "italic" }}>
                Model Output: {modelOutput}
              </Text>
            ) : null}
          </View>

          {/* Emotions block */}
          <View
            style={{
              flex: 1,
              flexDirection: "row",
              flexWrap: "wrap",
              alignItems: "center",
            }}
          >
            {emotions?.labels.map((label, index) => (
              <Text key={index} style={styles.emotionText}>
                {emotions_dict[label as keyof typeof emotions_dict]} (
                {(emotions.scores[index] * 100).toPrecision(2) + "%"})
              </Text>
            ))}
          </View>
        </View>

        {/* Right Section: Like Button and Model Button */}
        <View
          style={{
            flex: 1,
            flexDirection: "column",
            alignItems: "center",
            gap: 8,
          }}
        >
          <TouchableOpacity
            activeOpacity={isLiking ? 1 : 0}
            onPress={async () => {
              setIsLiking(true);
              const { data, error } = !isLiked
                ? await supabase
                    .from("likes_duplicate")
                    .insert({ quote_id: quote.id })
                    .select()
                : await supabase
                    .from("likes_duplicate")
                    .delete()
                    .eq("quote_id", quote.id)
                    .select();

              if (error || data.length === 0) {
                alert(error?.message || "error: wrong user");
              } else {
                setIsLiked(!isLiked); // update local for immediate feedback
                setTimeout(() => {
                  refetchQuotes(); // actually exists now
                }, 700);
              }

              setIsLiking(false);
            }}
          >
            {isLiking ? (
              <ActivityIndicator size={20} color="#007AFF" />
            ) : (
              <View style={styles.button}>
                <Text>{isLiked ? "❤️" : "🖤"}</Text>
              </View>
            )}
          </TouchableOpacity>
          {/* create another button */}
          <TouchableOpacity
            activeOpacity={isModelLoading ? 1 : 0}
            onPress={async () => {
              setIsModelLoading(true);
              await fetchModel(setModelOutput, quote.quote);
              setIsModelLoading(false);
            }}
          >
            {isModelLoading ? (
              <ActivityIndicator size={20} color="#007AFF" />
            ) : (
              <View style={styles.button}>
                <Text>Model</Text>
              </View>
            )}
          </TouchableOpacity>
        </View>
      </View>
    );
  };

  const [inputQuote, setInputQuote] = useState("");
  const [inputTestModel, setInputTestModel] = useState(
    "She has all my love; my love she has."
  );
  const textColor = useThemeColor({}, "text");
  const [filter, setFilter] = useState({
    title: "",
    type: "all",
    subtype: "all",
    lang: "all",
    era: "all",
    emotionalScore: "",
  });

  const refetchQuotes = () => {
    fetchQuotes(setQuotes, inputQuote, filter);
  };

  useFocusEffect(
    useCallback(() => {
      if (hasSearched && inputQuote.trim() !== "") {
        refetchQuotes();
      }
    }, [hasSearched, inputQuote])
  );

  return (
    <View style={{ height: "100%" }}>
      <FilterComponent
        onFilter={(x) => {
          setFilter(x);
          alert(`filters set: ${JSON.stringify(x)}`);
        }}
      />

      <View
        style={{
          flexDirection: "row",
          alignItems: "center",
          paddingHorizontal: 10,
          marginVertical: 10,
        }}
      >
        <Text
          style={{
            color: textColor,
            marginLeft: 10,
            marginTop: 10,
            marginRight: 10,
            fontSize: 14,
            fontWeight: "bold",
          }}
        >
          Search:
        </Text>
        <ThemedTextInput
          value={inputQuote}
          onChangeText={setInputQuote}
          placeholder="Enter text here (e.g., What is truth?)"
          style={{
            borderWidth: 1,
            padding: 10,
            flex: 1,
            marginRight: 10,
          }}
        />
        <Button
          onPress={() => {
            fetchQuotes(setQuotes, inputQuote, filter);
            setHasSearched(true);
          }}
          title="Fetch Quotes"
        />
      </View>

      <ScrollView style={{ flex: 1 }}>
        {quotes.map((item, i) => (
          <Item quote={item} key={i} refetchQuotes={refetchQuotes} />
        ))}
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  list: {
    backgroundColor: "#f0f0f0",
    padding: 10,
  },
  itemPositive: {
    backgroundColor: "#d4edda",
    padding: 20,
    marginVertical: 8,
    marginHorizontal: 16,
  },
  itemNegative: {
    backgroundColor: "#f8d7da",
    padding: 20,
    marginVertical: 8,
    marginHorizontal: 16,
  },
  itemNeutral: {
    backgroundColor: "#fff3cd",
    padding: 20,
    marginVertical: 8,
    marginHorizontal: 16,
  },
  quote: {
    fontSize: 14,
  },
  hierarchy: {
    fontSize: 12,
  },
  quote_info: {
    fontSize: 12,
  },
  emotionsContainer: {
    flexDirection: "row",
    flexWrap: "wrap",
  },
  emotionText: {
    marginRight: 5,
  },
  showMore: {
    color: "#007AFF",
    fontSize: 14,
    marginTop: 5,
  },
  button: {
    backgroundColor: "#007AFF",
    paddingVertical: 8,
    paddingHorizontal: 12,
    borderRadius: 5,
    alignItems: "center",
    width: "100%",
  },
});
