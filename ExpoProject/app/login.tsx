import * as WebBrowser from "expo-web-browser";
import * as Linking from "expo-linking";
import { useEffect, useState } from 'react'
import { StyleSheet, View } from 'react-native'
import { Button, Input } from '@rneui/themed'
import { useSession } from "@/context/AuthContext";
import { router } from "expo-router";

WebBrowser.maybeCompleteAuthSession(); // required for web only

export default function Auth() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const { signInWithEmail, signInWithGoogle, signUp, isLoading, createSessionFromUrl } = useSession();
  const url = Linking.useURL();

  useEffect(() => {
    if (url) createSessionFromUrl(url);
  }, [url]);

  return (
    <View style={styles.container}>
      <View style={[styles.verticallySpaced, styles.mt20]}>
        <Input
          label="Email"
          leftIcon={{ type: 'font-awesome', name: 'envelope' }}
          onChangeText={(text) => setEmail(text)}
          value={email}
          placeholder="email@address.com"
          autoCapitalize={'none'}
        />
        <Input
          label="Password"
          leftIcon={{ type: 'font-awesome', name: 'lock' }}
          onChangeText={(text) => setPassword(text)}
          value={password}
          secureTextEntry={true}
          placeholder="Password"
          autoCapitalize={'none'}
        />
      </View>
      <View style={[styles.verticallySpaced, styles.mt20]}>
        <Button title="Sign in" disabled={isLoading} onPress={() =>
          signInWithEmail(email, password)
            .then(() => router.replace('/'))
            .catch(error => alert(error))
        } />
        <Button title="Sign up" disabled={isLoading} onPress={() =>
          signUp(email, password)
            .then(() => router.replace('/'))
            .catch(error => alert(error))
        } />
        <Button title="Sign in with Google" disabled={isLoading} onPress={() =>
          signInWithGoogle()
            .then(() => router.replace('/'))
            .catch(error => alert(error))
        } />
      </View>
    </View>
  )
}

const styles = StyleSheet.create({
  container: {
    marginTop: 40,
    padding: 12,
  },
  verticallySpaced: {
    paddingTop: 4,
    paddingBottom: 4,
    alignSelf: 'stretch',
    gap: 10
  },
  mt20: {
    marginTop: 20,
  },
})