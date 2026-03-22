from openai import AzureOpenAI

client = AzureOpenAI(
    api_key="2FAWbaBw3DaBdGtqJvvTOPZLXByQDSf23za6IE9uK8GmXCCcB0HoJQQJ99CCACHYHv6XJ3w3AAAAACOGdGEm",
    api_version="2025-01-01-preview",
    azure_endpoint="https://akash-mn1btcwy-eastus2.cognitiveservices.azure.com/"
)

try:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "test"}]
    )
    print("SUCCESS")
except Exception as e:
    print("ERROR:", str(e))
