import { supabase } from '@/utils/supabase';
import React, { createContext, useContext, useEffect, useState } from 'react';

type ThemeType = 'dark' | 'light';

type ThemeContextType = {
  theme: ThemeType;
  setTheme: (theme: ThemeType) => void;
};

const ThemeContext = createContext<ThemeContextType>({
  theme: 'light',
  setTheme: (theme: ThemeType) => { },
});

export const useTheme = () => useContext(ThemeContext);

export const ThemeProvider = ({ children }: { children: React.ReactNode }) => {
  const [theme, setTheme] = useState<ThemeType>('light');

  useEffect(() => {
    // supabase.auth.onAuthStateChange((_event, session) => {
    // 
    // const {data,error}=awaitsupabase.from('users').select('*').eq('id', supabase.auth.user()?.id)
    // setTheme(data[0].theme)
  }, []);

  return (
    <ThemeContext.Provider value={{ theme, setTheme }}>
      {children}
    </ThemeContext.Provider>
  );
};