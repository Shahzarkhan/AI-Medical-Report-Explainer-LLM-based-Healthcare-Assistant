# RAG setup

The app now uses a lightweight local TF-IDF retrieval layer before the Gemini call.

Pipeline:

PDF -> extracted report text -> local RAG retrieval -> relevant medical knowledge -> Gemini -> JSON dashboard

The retrieval step is local and does not make a Gemini API request. Medical knowledge is stored in:

`data/medical_knowledge/`

You can add more `.txt` files there without changing Python code.

## Model

The default model is `gemini-3.5-flash-lite`. You can override it in `.env`:

`GEMINI_MODEL=gemini-3.5-flash-lite`

## Run

```powershell
streamlit run main.py
```

If the Gemini quota is exhausted, the app now shows a friendly quota message instead of a raw traceback. Local RAG retrieval remains available.
