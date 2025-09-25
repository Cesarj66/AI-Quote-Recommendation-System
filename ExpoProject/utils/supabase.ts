import AsyncStorage from '@react-native-async-storage/async-storage'
import { createClient } from '@supabase/supabase-js'
import { Platform } from 'react-native'

const supabaseUrl = "https://ekrumlfvpstscaavmdtx.supabase.co"
const supabaseAnonKey = process.env.EXPO_PUBLIC_SUPABASE_KEY!

export const supabase = createClient(supabaseUrl, supabaseAnonKey, {
  auth: {
    storage: Platform.OS === "web" ? global.localStorage : AsyncStorage,
    autoRefreshToken: true,
    persistSession: true,
    detectSessionInUrl: false,
  },
})

export const authenticatedFetch = async (url: string, options: RequestInit = {}) => {
  const {data:{session}} = await supabase.auth.getSession()
  const token = session?.access_token

  const headers = {
    ...options.headers,
    Authorization: token ? `Bearer ${token}` : '',
    'Content-Type': 'application/json',
  }

  const response = await fetch(url, {
    ...options,
    headers,
  })

  return response
}