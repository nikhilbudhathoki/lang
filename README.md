  LANG-TRANSLATOR

# 🌐 **English-Nepali Translation System** with **Groq API** & **Streamlit**

This project provides a **bi-directional translation system** that translates text between **English** and **Nepali** using the **Groq API**. Additionally, it integrates with **Streamlit** to offer a simple, interactive web interface for real-time translation.

---

## 🚀 Features

- **Bi-directional Translation**: Translate text from **English to Nepali** and vice versa.
- **Groq API Integration**: Utilizes the Groq API for high-quality translation between languages.
- **Streamlit Interface**: Provides a user-friendly web interface to input text and get translations instantly.
- **Real-time Translation**: See translations as you type!

---

## 🛠️ Technologies Used

- **Python**: The core language used to implement the translation system and web interface.
- **Groq API**: The translation engine for English-Nepali and Nepali-English translations.
- **Streamlit**: A Python library for creating interactive, web-based applications.
- **Requests**: Used for making HTTP requests to the Groq API.

---

## 📥 Installation

To set up the project locally, follow these steps:

1. **Clone the repository**:

```bash
git clone https://github.com/nikhilbudhathoki/lang.git
cd lang
```

2. **Install dependencies**:

Make sure to install all required Python packages using `pip`:

```bash
pip install -r requirements.txt
```

> **Note**: You’ll need a **Groq API key** to access the translation services. Make sure to sign up at [Groq API](https://groq.co) and get your API key.

---

## 🏃 Usage

1. **Set up API Key**: 
   You will need to add your **Groq API key** to the code or environment variable to authenticate requests. If the key is stored in an environment variable:

   ```bash
   export GROQ_API_KEY="your-api-key"
   ```

2. **Run the Streamlit App**:
   
   Start the app using Streamlit by running the following command:

   ```bash
   streamlit run app.py
   ```

   This will launch a web interface in your browser where you can input text and see translations between English and Nepali in real-time.

---

## 🌍 Streamlit Interface

The Streamlit interface allows you to:

- **Translate from English to Nepali**: Enter text in English and get the Nepali translation.
- **Translate from Nepali to English**: Enter text in Nepali and get the English translation.

### Example Workflow:

1. Open the app in your browser.
2. Choose the translation direction (English ↔ Nepali).
3. Enter the text to translate.
4. Click "Translate" and get the output in the target language.

---

## 🤖 How It Works

1. **Input Text**: The user enters text to be translated in the input field.
2. **API Request**: The app sends the input text to the **Groq API** for translation.
3. **Display Output**: The translated text is displayed in real-time.

---

## 📊 Example Output

Here’s what the translation might look like:

### English to Nepali:
```plaintext
Input: "Hello, how are you?"
Output: "नमस्ते, तपाईंलाई कस्तो छ?"
```

### Nepali to English:
```plaintext
Input: "नमस्ते, तपाईंलाई कस्तो छ?"
Output: "Hello, how are you?"
```

---

## 📝 Customizing the App

You can modify the translation parameters or improve the UI by editing the `app.py` file. For example, you can adjust the layout of the input boxes or change the button text.

---

## 🤝 Contributing

If you’d like to contribute, follow these steps:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Make changes or add new features.
4. Commit your changes (`git commit -am 'Add new feature'`).
5. Push to the branch (`git push origin feature-branch`).
6. Open a pull request to merge changes.

---

## 📑 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 💬 Questions?

Feel free to open an issue or reach out if you have any questions or need help with the project!

---

