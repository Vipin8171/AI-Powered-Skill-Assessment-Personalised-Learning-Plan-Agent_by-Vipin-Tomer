# 🔑 Groq API Setup Guide

## What is Groq?
Groq provides **free, high-speed LLM inference** for AI applications. Your app uses Groq to generate intelligent interview questions and evaluate answers.

---

## Step 1: Get Your FREE Groq API Key

1. **Go to the Groq Console:**
   - Open your browser: https://console.groq.com
   - Sign up with email or Google/GitHub account (FREE)

2. **Create API Key:**
   - Navigate to **API Keys** section (left sidebar)
   - Click **"Create New API Key"**
   - Give it a name (e.g., "Skill Assessment Agent")
   - Copy the key (starts with `gsk_`)

3. **Your key will look like:**
   ```
   gsk_1234567890abcdefghijklmnopqrst
   ```

---

## Step 2: Add API Key to Your Project

### Option A: Using .env File (RECOMMENDED - Most Secure)

1. **Open the `.env` file** in your project folder:
   - Location: `c:\Users\tvipi\project\Internship\Deccan ai\.env`

2. **Replace the placeholder:**
   ```
   # Before:
   GROQ_API_KEY=gsk_placeholder_your_api_key_here
   
   # After:
   GROQ_API_KEY=gsk_your_actual_key_here_1234567890
   ```

3. **Save the file** (Ctrl+S in VS Code)

4. **Never commit this file** to Git - it's in `.gitignore` for security

### Option B: Using Windows Environment Variables (Alternative)

If you prefer system-wide configuration:

1. **Press Win + Pause** or right-click **This PC → Properties**
2. **Click** "Advanced system settings"
3. **Click** "Environment Variables" button
4. **Under "User variables"**, click **New**
5. **Variable name:** `GROQ_API_KEY`
6. **Variable value:** `gsk_your_actual_key_here`
7. **Click OK** and restart your app

---

## Step 3: Verify Setup

1. **Start your app:**
   ```powershell
   cd "c:\Users\tvipi\project\Internship\Deccan ai"
   streamlit run app.py
   ```

2. **What should happen:**
   - ✅ App loads without errors
   - ✅ "Assessment Setup" sidebar appears
   - ✅ Questions are generated dynamically
   - ✅ Answers are evaluated with detailed feedback

3. **If you see an error:**
   ```
   ❌ Groq API key not configured!
   ```
   This means:
   - API key wasn't added to `.env`
   - File wasn't saved properly
   - App wasn't restarted

---

## Step 4: Test It Works

1. Load sample job description
2. Click **"Start Assessment"**
3. Watch the spinner: *"Generating personalized question for [Skill]..."*
4. A **unique question** should appear (not generic)
5. Type an answer
6. See detailed feedback with score

---

## Troubleshooting

### Error: "Invalid Groq API key format"
- ❌ Key doesn't start with `gsk_`
- ✅ Copy-paste again from Groq console

### Error: "Groq API key not configured"
- ❌ Still shows placeholder value  
- ✅ Edit .env, save, restart app

### Questions are generic (not personalized)
- ❌ Groq not responding
- ✅ Check internet connection
- ✅ Verify API key is valid in Groq console

### App is slow
- This is normal! First question takes 3-5 seconds
- Subsequent questions are faster
- Groq caches responses

---

## API Usage & Limits

**Free Plan:** 
- ✅ 30 requests per minute
- ✅ Unlimited requests per day
- ✅ Use `llama-3.1-70b-versatile` model (recommended)

**Your app uses:**
- 1 request per question generated
- 1 request for "Why this question?" context
- 1 request per answer evaluation
- **~3 requests per skill assessed**

For 8 skills = ~24 requests (well within free limits!)

---

## Additional Notes

### Privacy
- Your resume and job description are sent to Groq servers
- They're not stored or used for training
- Delete the `.env` file if sharing your code
- Use `.gitignore` to prevent accidental uploads

### Customization
To change the LLM model, edit `groq_integration.py`:
```python
model="llama-3.1-70b-versatile",  # Change this line
```

Other available Groq models:
- `llama-3.1-8b-instant` (faster, lighter)
- `mixtral-8x7b-32768` (balanced)
- `llama-3.1-70b-versatile` (recommended - best quality)

---

## Questions?

- Groq Docs: https://console.groq.com/docs
- API Key Issues: https://console.groq.com/keys
- Rate Limits: https://console.groq.com/account
