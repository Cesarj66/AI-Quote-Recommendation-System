import { createClient } from "@supabase/supabase-js";
import { OpenAI } from "openai";

// https://supabase.com/docs/reference/javascript/initializing
// https://docs.expo.dev/router/reference/api-routes/#errors

const supabaseUrl = "https://ekrumlfvpstscaavmdtx.supabase.co";
const supabaseKey = process.env.EXPO_PUBLIC_SUPABASE_KEY;

export async function GET(request) {
  const authorization = request.headers.get("Authorization");
  if (!authorization)
    return new Response(JSON.stringify({ error: "Unauthorized" }), {
      status: 401,
      headers: { "Content-Type": "application/json" },
    });

  // You can now use it within a Supabase Client
  const supabase = createClient(supabaseUrl, supabaseKey, {
    global: {
      headers: {
        Authorization: authorization,
      },
    },
  });

  // supabase db
  const { data: user, error: userError } = await supabase.auth.getUser();
  if (userError) {
    console.error("Error fetching user:", userError);
    return []; //error
  }

  const userId = user.user.id; // Get the current user's ID


  const { data: quotesData, error: quotesError } = await supabase.from('likes_duplicate').select('user_id, quotes(id,page_id,page_name,quote,hierarchy,quote_info,emotions,likes_duplicate(user_id),summary)').eq('user_id', userId);

  if (quotesError) {
    console.error("Error fetching quotes:", quotesError);
    return [];
  }

  const data=quotesData.map(({quotes})=>{return {title:quotes.page_name,Emotions:quotes.emotions,...quotes}});

  return new Response(JSON.stringify({ data }), {
    status: 200,
    headers: { "Content-Type": "application/json" },
  });
}
