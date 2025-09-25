import { ThemeProvider as CustomThemeProvider } from "@/context/ThemeContext";
import { Slot } from 'expo-router';
import { SessionProvider } from "@/context/AuthContext";

export default function RootLayout() {

    return (
        <SessionProvider>
        <CustomThemeProvider>
            <Slot />
        </CustomThemeProvider>
        </SessionProvider>
    );
}