import { useContext, createContext, type PropsWithChildren, useState, useEffect } from 'react';
import * as QueryParams from "expo-auth-session/build/QueryParams";
import { makeRedirectUri } from "expo-auth-session";
import * as WebBrowser from "expo-web-browser";
import { supabase } from '@/utils/supabase';
import { Session } from '@supabase/supabase-js';
import { AppState } from 'react-native';

const AuthContext = createContext<{
  signInWithEmail: (email: string, password: string) => Promise<void>;
  signInWithGoogle: () => Promise<void>;
  signUp: (email: string, password: string) => Promise<void>;
  signOut: () => void;
  createSessionFromUrl: (url: string) => Promise<Session | null | void>;
  session?: Session | null;
  isLoading: boolean;
}>({
  signInWithEmail: (email: string, password: string) => new Promise(() => { }),
  signInWithGoogle: () => new Promise(() => { }),
  signUp: (email: string, password: string) => new Promise(() => { }),
  signOut: () => null,
  createSessionFromUrl: (url: string) => new Promise(() => null),
  session: null,
  isLoading: false,
});

// This hook can be used to access the user info.
export function useSession() {
  const value = useContext(AuthContext);
  if (!value) {
    throw new Error('useSession must be wrapped in a <SessionProvider />');
  }

  return value;
}

export function SessionProvider({ children }: PropsWithChildren) {
  // const [[isLoading, session], setSession] = useStorageState('session');
  const [user, setUser] = useState(null)
  const [isLoading, setIsLoading] = useState(true)
  // initialize session for intentional lag before session is set
  const [session, setSession] = useState<Session | null>({ user: {} } as Session)

  useEffect(() => {
    supabase.auth.getSession().then(({ data: { session } }) => {
      setSession(session)
    })
    // Tells Supabase Auth to continuously refresh the session automatically if
    // the app is in the foreground. When this is added, you will continue to receive
    // `onAuthStateChange` events with the `TOKEN_REFRESHED` or `SIGNED_OUT` event
    // if the user's session is terminated. This should only be registered once.
    AppState.addEventListener('change', (state) => {
      if (state === 'active') {
        supabase.auth.startAutoRefresh()
      } else {
        supabase.auth.stopAutoRefresh()
      }
    })
    supabase.auth.onAuthStateChange((_event, session) => {
      setSession(session)
    })
    
    setIsLoading(false)
  }, [])

  const signInWithEmail = async (email: string, password: string) => {
    // Perform sign-in logic here
    setIsLoading(true)
    const { error } = await supabase.auth.signInWithPassword({
      email: email,
      password: password,
    })

    if (error) {
      setIsLoading(false)
      throw new Error(error.message)
    }
    setIsLoading(false)
  }

  const signInWithGoogle = async () => {
    setIsLoading(true)
    try {
      const { data, error } = await supabase.auth.signInWithOAuth({
        provider: "google",
        options: {
          redirectTo: makeRedirectUri(),
          skipBrowserRedirect: true,
        },
      });
      if (error) throw new Error(error.message)

      const res = await WebBrowser.openAuthSessionAsync(
        data?.url ?? "",
        makeRedirectUri()
      );

      if (res.type === "success") {
        const { url } = res;
        console.log({ url })
        await createSessionFromUrl(url);
      } else throw new Error(res.type);
    } catch (error) {
      throw error
    } finally {
      setIsLoading(false)
    }
  }

  const signUp = async (email: string, password: string) => {
    setIsLoading(true)
    let e
    const {
      data: { session },
      error,
    } = await supabase.auth.signUp({
      email: email,
      password: password,
    })

    if (error) e = new Error(error.message)
    if (!session) alert('Please check your inbox for email verification!')
    setIsLoading(false)
    if (e) throw e
  }

  const signOut = async () => {
    setIsLoading(true)
    await supabase.auth.signOut()
    setIsLoading(false)
  }

  const createSessionFromUrl = async (url: string) => {
    const { params, errorCode } = QueryParams.getQueryParams(url)

    if (errorCode) throw new Error(errorCode)
    const { access_token, refresh_token } = params
    console.log({ access_token })
    if (!access_token) return

    const { data, error } = await supabase.auth.setSession({
      access_token,
      refresh_token,
    })
    if (error) throw new Error(error.message)
    console.log(JSON.stringify(data))
    return data.session
  }

  return (
    <AuthContext.Provider
      value={{
        signInWithEmail,
        signInWithGoogle,
        signUp,
        signOut: async () => {
          setIsLoading(true)
          await supabase.auth.signOut()
          setIsLoading(false)
        },
        createSessionFromUrl,
        session,
        isLoading,
      }}>
      {children}
    </AuthContext.Provider>
  );
}
