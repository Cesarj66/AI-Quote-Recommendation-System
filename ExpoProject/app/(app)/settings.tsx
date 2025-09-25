import { ThemedScrollView } from '@/components/ThemedScrollView';
import { ThemedText } from '@/components/ThemedText';
import { useSession } from '@/context/AuthContext';
import { useTheme } from '@/context/ThemeContext';
import { supabase } from '@/utils/supabase';
import { useEffect, useState } from 'react';
import { View, Image, TouchableOpacity, StyleSheet } from 'react-native';

const SettingsScreen = () => {
    const { theme, setTheme } = useTheme();
    const { signOut } = useSession();
    const [username, setUsername] = useState<string>('???');
    const [email, setEmail] = useState<string>('???');
    const [avatarUrl, setAvatarUrl] = useState<string>('https://randomuser.me/api/portraits/men/41.jpg');
    useEffect(() => {
        const loadTheme = async () => {
            const { data: { user }, error } = await supabase.auth.getUser();
            if (error) alert(error.message);
            else {
                setUsername(user?.user_metadata.name ?? 'Anonymous')
                setEmail(user?.email ?? 'no email?')
                setAvatarUrl(user?.user_metadata.avatar_url ?? 'https://randomuser.me/api/portraits/men/41.jpg')
            }
        };
        loadTheme();
    }, []);
    const toggleTheme = async () => {
        const newTheme = theme === "light" ? "dark" : "light";
        const { data: { user }, error } = await supabase.auth.updateUser({ data: { theme: newTheme } });
        if (error) alert(error.message);
        else setTheme(user!.user_metadata.theme);
    };

    return (
        <ThemedScrollView style={styles.container}>

            <View style={styles.profileSection}>
                <Image
                    source={{ uri: avatarUrl }}
                    style={styles.avatar}
                />
                <View>
                    <ThemedText style={styles.name}>{username}</ThemedText>
                    <ThemedText style={styles.email}>{email}</ThemedText>
                </View>
            </View>

            <TouchableOpacity style={styles.settingItem} onPress={() => alert('Test Button')}>
                <ThemedText>🛠️ Test</ThemedText>
            </TouchableOpacity>

            <TouchableOpacity style={styles.settingItem} onPress={toggleTheme}>
                <ThemedText>{theme === 'dark' ? "☀️ Light Mode" : "🌙 Dark Mode"}</ThemedText>
            </TouchableOpacity>

            <TouchableOpacity style={styles.settingItem} onPress={() => signOut()}>
                <ThemedText style={styles.settingText}>🚪 Sign Out</ThemedText>
            </TouchableOpacity>
        </ThemedScrollView>
    );
};

const styles = StyleSheet.create({
    container: {
        flex: 1,
        paddingHorizontal: 20,
        paddingVertical: 10,
    },
    profileSection: {
        flexDirection: 'row',
        alignItems: 'center',
        paddingVertical: 20,
        borderBottomWidth: 1,
    },
    avatar: {
        width: 60,
        height: 60,
        borderRadius: 30,
        marginRight: 15,
    },
    name: {
        fontSize: 18,
        fontWeight: 'bold',
    },
    email: {
        fontSize: 14,
    },
    settingItem: {
        paddingVertical: 15,
        borderBottomWidth: 1,
    },
    settingText: {
        fontSize: 16,
    },
});

export default SettingsScreen;
