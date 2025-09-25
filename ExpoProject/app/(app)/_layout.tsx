import { ThemeProvider, DarkTheme, DefaultTheme } from "@react-navigation/native";
import { useTheme } from "@/context/ThemeContext";
import { Redirect, Tabs } from 'expo-router';
import { ActivityIndicator, Text, View } from "react-native";
import { useSession } from "@/context/AuthContext";
import { useEffect } from "react";
import { supabase } from "@/utils/supabase";

export default function Layout() {
  const { theme, setTheme } = useTheme();
  const { session, isLoading } = useSession();

  useEffect(() => {
    const loadTheme= async ()=>{
      const {data:{user},error}=await supabase.auth.getUser()
      if(error) alert(error.message)
      else setTheme(user!.user_metadata.theme || 'light')
    }
    loadTheme()
  }, []);

  // You can keep the splash screen open, or render a loading screen like we do here.
  if (isLoading) {
    return <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center' }}>
      <ActivityIndicator size={60} color="#007AFF" />
    </View>
  }

  // Only require authentication within the (app) group's layout as users
  // need to be able to access the (auth) group and sign in again.
  if (!session) {
    // On web, static rendering will stop here as the user is not authenticated
    // in the headless Node process that the pages are rendered in.
    return <Redirect href="/login" />;
  }

  return (
    <ThemeProvider value={theme == 'dark' ? DarkTheme : DefaultTheme}>
      <Tabs>
        <Tabs.Screen name="index" options={{ title: 'Home', tabBarIcon: () => <Text>🏠</Text> }} />
        <Tabs.Screen name="likes" options={{ title: 'Likes', tabBarIcon: () => <Text>❤️</Text> }} />
        <Tabs.Screen name="settings" options={{ title: 'Settings', tabBarIcon: () => <Text>⚙️</Text> }} />
      </Tabs>
    </ThemeProvider>
  );
}