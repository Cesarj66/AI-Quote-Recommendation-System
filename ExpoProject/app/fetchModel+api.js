async function query(data) {
  const response = await fetch(
    "https://mdrtmjzq017iqiyp.us-east-1.aws.endpoints.huggingface.cloud",
    {
      headers: {
        Accept: "application/json",
        Authorization: `Bearer ${process.env.EXPO_PUBLIC_HUGGINGFACE_TOKEN}`,
        "Content-Type": "application/json",
      },
      method: "POST",
      body: JSON.stringify(data),
    }
  );
  const result = await response.json();
  return result;
}

export async function GET(request) {
  const authorization = request.headers.get("Authorization");
  if (!authorization)
    return new Response(JSON.stringify({ error: "Unauthorized" }), {
      status: 401,
      headers: { "Content-Type": "application/json" },
    });

  const url = new URL(request.url);
  const inputTestModel = url.searchParams.get("input");

  console.log("testing model with: ", inputTestModel);

  let data = "";

  const queryResponse = await query({
    inputs: inputTestModel,
    parameters: {},
  });

  console.log("queryResponse: ", queryResponse);
  data = queryResponse[0].label;
  console.log("data: ", data);

  return new Response(JSON.stringify({ data }), {
    status: 200,
    headers: { "Content-Type": "application/json" },
  });
}
