# OptiQuery

**OptiQuery** is an AI-powered query optimization tool that helps developers analyze and improve slow-running database queries — based on your **actual data and structure**, not just generic tips.

Currently supports **Neo4j**, with upcoming support for **SQL** and **MongoDB**. Choose your preferred LLM (ChatGPT, Gemini), plug in your API key, and let OptiQuery handle the rest.

---

## 🚀 Features

- 📊 Analyze real DB metadata, relationships, and usage patterns
- 🧠 Use ChatGPT or Gemini for smart, context-aware optimizations
- 🔄 Manage multiple databases and AI providers by friendly name
- 💻 Fully interactive CLI — no boilerplate, no memorizing tokens
- 💾 Secure, local config storage
- 🛠️ Modular codebase — easily extend to new DBs or LLMs

---

## 📦 Installation

Install from PyPI:

```bash
pip install optiquery
```

Or clone locally:

```bash
git clone https://github.com/mich-gurevitz/opti-query
cd optiquery
pip install -r requirements.txt
```

---

## 💡 Usage

To launch the interactive CLI:

```bash
optiquery
```

You’ll be able to:

- 🔍 Start a query optimization session
- 🧩 Configure or update database connections
- 🤖 Configure or update AI providers (e.g. ChatGPT, Gemini)
- 📈 View optimized query versions with full explanations and suggestions

---

## 🧪 Local Development

Install in dev mode:

```bash
make install-dev
```

Lint with pre-commit:

```bash
make lint
```

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

---

## 👨‍💻 Author

**Michael Gurevitz**  
GitHub: [@mich-gurevitz](https://github.com/mich-gurevitz)

---

## ⭐️ Support the Project

If you find OptiQuery helpful, give it a ⭐ on GitHub and share it with your dev friends!
