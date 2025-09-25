import React, { useEffect, useState } from "react";
import { StyleSheet, TextInput, Button } from "react-native";
import { Dropdown } from "./Dropdown";
import { ThemedView } from "./ThemedView";
import { ThemedText } from "./ThemedText";

// const types = ["all", "Person", "Work"];
const types = ["all", "Person"];
const subtypes: { [key: string]: string[] } = {
  all: ["all"],
  Person: [
    "all",
    "Novelist",
    "Poet",
    "Playwright",
    "Philosopher",
    "Politician",
    "Religious Figure",
    "Scientist",
    "Artist",
    "Composer",
    "Activist",
    "Critic",
    "Historian",
    "Economist",
    "Mathematician",
    "Inventor",
    "Scholar",
    "Journalist",
    "Director",
    "Actor",
    "Military Leader",
    "Diplomat",
    "Orator",
    "Comedian",
    "Public Intellectual",
    "Educator",
    "Fictional Characters",
    "Programmer",
    "Entrepeneur",
  ],
};
const langs = [
  "all",
  "English",
  "French",
  "German",
  "Russian",
  "Italian",
  "Chinese",
  "Japanese",
  "Arabic",
  "Latin",
  "Classical Greek",
  "Spanish",
  "Portuguese",
  "Other",
];
const eras = [
  "all",
  "Ancient (before 500 BCE)",
  "Classical (500 BCE–500 CE)",
  "Early Medieval (500–1000)",
  "High Medieval (1000–1300)",
  "Late Medieval (1300–1500)",
  "14th and 15th century (1300–1500)",
  "16th century (1500–1600)",
  "17th century (1600–1700)",
  "18th century (1700–1800)",
  "19th Century (1800–1900)",
  "(1900–1945)",
  "(1945–1999)",
  "21st Century (2000–Present)",
];
export function FilterComponent({
  onFilter,
}: {
  onFilter: (filters: any) => void;
}) {
  const [title, setTitle] = useState("");
  const [type, setType] = useState("all");
  const [subtype, setSubtype] = useState("all");
  const [lang, setLang] = useState("all");
  const [era, setEra] = useState("all");
  const [hide, setHide] = useState(true);

  useEffect(() => {
    setSubtype("all");
  }, [type]);

  const handleFilter = () => {
    onFilter({ title, type, subtype, lang, era });
  };

  const toggleHide = () => setHide(!hide);

  return (
    <>
      <Button title="Filter" onPress={toggleHide} />
      <ThemedView style={[styles.container, hide ? { display: "none" } : {}]}>
        <ThemedText>Source</ThemedText>
        <TextInput
          style={styles.input}
          placeholder="Filter by Title"
          value={title}
          onChangeText={setTitle}
        />

        <ThemedText>Type</ThemedText>
        <Dropdown
          style={styles.input}
          defaultVal={type}
          setState={setType}
          list={types}
        />

        <ThemedText>Sub-Type</ThemedText>
        <Dropdown
          style={styles.input}
          defaultVal={"all"}
          setState={setSubtype}
          list={subtypes[type]}
          key={type}
        />

        <ThemedText>Language/Region</ThemedText>
        <Dropdown
          style={styles.input}
          defaultVal={type}
          setState={setLang}
          list={langs}
        />

        <ThemedText>Era</ThemedText>
        <Dropdown
          style={styles.input}
          defaultVal={type}
          setState={setEra}
          list={eras}
        />
        <Button title="Apply Filters" onPress={handleFilter} />
      </ThemedView>
    </>
  );
}

const styles = StyleSheet.create({
  container: {
    padding: 16,
  },
  input: {
    borderWidth: 1,
    borderColor: "#ccc",
    borderRadius: 4,
    padding: 8,
    marginBottom: 12,
    backgroundColor: "white",
  },
});
