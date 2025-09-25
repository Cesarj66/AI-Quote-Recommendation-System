import { Dispatch, Key, SetStateAction } from "react";
import { StyleProp, StyleSheet, Text, View, ViewStyle } from "react-native";
import SelectDropdown from "react-native-select-dropdown";

export const Dropdown = ({defaultVal,setState,list,style={}}:{defaultVal:string,setState:Dispatch<SetStateAction<string>>,list:string[],style?:StyleProp<any>}) => {
  return (
    <SelectDropdown
      data={list}
      defaultValue={defaultVal}
      onSelect={setState}
      renderButton={(selectedItem) => {
        return (
          <View style={style}>
            <Text>{selectedItem}</Text>
          </View>
        );
      }}
      renderItem={(item, index, isSelected) => {
        return (
          <View style={{  ...(isSelected && { backgroundColor: '#D2D9DF' }) }}>
            <Text>{item}</Text>
          </View>
        );
      }}
      showsVerticalScrollIndicator={false}
    />
  );
};