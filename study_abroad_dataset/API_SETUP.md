# Setting up the Google Gemini API

This guide will help you set up and configure your Google Gemini API key for the dataset generator.

## Getting an API Key

1. Visit the Google AI Studio: https://makersuite.google.com/app/apikey
2. Sign in with your Google account if needed
3. Click "Create API Key" to generate a new key
4. Copy the generated API key - it should start with "AI" and be at least 20 characters long

## Configuring the API Key

1. In the root directory of the project, locate the `.env` file
2. Open the file and add your API key:
   ```
   GEMINI_API_KEY=your_api_key_here
   ```
   Replace `your_api_key_here` with your actual API key.

## Verifying the Setup

1. Run the verification script:
   ```bash
   python test_setup.py
   ```
   This will check if your API key is properly configured.

2. Try generating a sample conversation:
   ```bash
   python src/main.py --total-conversations 1 --batch-size 1
   ```

## Common Issues

1. **Invalid API Key Error**
   - Make sure your API key starts with "AI"
   - Verify you've copied the entire key
   - Check for any extra spaces or characters

2. **API Key Not Found**
   - Ensure your `.env` file exists in the project root
   - Verify the environment variable name is exactly `GEMINI_API_KEY`
   - Try reactivating your virtual environment

3. **Rate Limiting**
   - The free tier has usage limits
   - Try reducing batch size
   - Add delays between requests

## Getting Help

If you're still having issues:
1. Check the logs in the `logs/` directory
2. Visit the Google AI Studio documentation
3. Open an issue in the project repository

## API Key Safety

- Never commit your API key to version control
- Don't share your API key with others
- Rotate your key if you suspect it's been compromised
- Use environment variables in production
