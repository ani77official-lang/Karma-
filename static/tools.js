// 50 AI-powered tools — each sends a pre-built prompt to the selected provider
// Each tool: { id, name, icon, category, placeholder, prompt }

const TOOLS = [
  // --- Writing (1-8) ---
  { id: 1, name: "Email Writer", icon: "mail", category: "Writing", placeholder: "Topic: Write a leave application email to my boss...", prompt: "Write a professional email based on the user's request. Format it with Subject line, greeting, body, and sign-off. Make it polished and ready to send." },
  { id: 2, name: "Story Generator", icon: "book", category: "Writing", placeholder: "A story about a robot who discovers emotions...", prompt: "Write a creative short story based on the user's input. Include vivid descriptions, dialogue, and a satisfying ending. Keep it 300-500 words." },
  { id: 3, name: "Poem Creator", icon: "sparkle", category: "Writing", placeholder: "Write a poem about the monsoon season...", prompt: "Write a beautiful poem based on the user's input. Use rich imagery and emotion. 4-8 stanzas." },
  { id: 4, name: "Essay Outline", icon: "file", category: "Writing", placeholder: "Topic: Impact of AI on education...", prompt: "Create a detailed essay outline based on the user's topic. Include introduction, 3-5 main points with sub-points, and conclusion. Format with clear headings." },
  { id: 5, name: "Cover Letter", icon: "briefcase", category: "Writing", placeholder: "Applying for Software Engineer at Google, I have 3 years experience...", prompt: "Write a professional cover letter based on the user's input. Include their qualifications, why they want the role, and a strong closing. Format properly." },
  { id: 6, name: "Resume Summary", icon: "user", category: "Writing", placeholder: "I'm a marketing professional with 5 years experience in digital ads...", prompt: "Write a compelling 3-4 line resume summary/profile based on the user's input. Make it impactful, quantified where possible, and ready to paste on a resume." },
  { id: 7, name: "Blog Post", icon: "edit", category: "Writing", placeholder: "Topic: 10 tips for saving money as a student...", prompt: "Write an engaging blog post based on the user's input. Include a catchy title, introduction, well-structured body with headings, and a conclusion. 400-600 words." },
  { id: 8, name: "Speech Writer", icon: "message", category: "Writing", placeholder: "A graduation speech for my college farewell...", prompt: "Write a speech based on the user's input. Make it inspiring, include anecdotes or quotes, and keep it appropriate for the occasion. 2-3 minutes when spoken." },

  // --- Code (9-14) ---
  { id: 9, name: "Code Generator", icon: "code", category: "Code", placeholder: "Write a Python function to reverse a string...", prompt: "Write clean, well-commented code based on the user's request. Include the code in a code block with the language specified. Add a brief explanation after." },
  { id: 10, name: "Code Explainer", icon: "eye", category: "Code", placeholder: "Paste code here to get an explanation...", prompt: "Explain the following code in simple terms. Describe what it does, how it works step by step, and any important concepts. Use the user's input as the code to explain." },
  { id: 11, name: "Bug Finder", icon: "search", category: "Code", placeholder: "Paste your buggy code here...", prompt: "Analyze the code provided by the user. Identify any bugs, errors, or issues. Explain each problem clearly and provide the corrected code." },
  { id: 12, name: "Code Reviewer", icon: "check", category: "Code", placeholder: "Paste code for review...", prompt: "Review the code provided by the user. Give feedback on code quality, best practices, performance, and readability. Suggest improvements with examples." },
  { id: 13, name: "Regex Builder", icon: "key", category: "Code", placeholder: "Match email addresses in a string...", prompt: "Create a regular expression based on the user's request. Provide the regex, explain each part, and give 2-3 test examples showing matches and non-matches." },
  { id: 14, name: "SQL Generator", icon: "layers", category: "Code", placeholder: "Get all users who joined in the last 30 days...", prompt: "Write a SQL query based on the user's request. Provide the query in a code block, explain what it does, and mention any assumptions about table structure." },

  // --- Translation & Languages (15-18) ---
  { id: 15, name: "Translator", icon: "translate", category: "Language", placeholder: "Translate to Hindi: Hello, how are you?", prompt: "Translate the user's text. Detect the target language from their request. Provide the translation and a brief note on any cultural nuances." },
  { id: 16, name: "Grammar Fixer", icon: "edit", category: "Language", placeholder: "Paste text with grammar issues...", prompt: "Fix all grammar, spelling, and punctuation errors in the user's text. Provide the corrected version, then list the changes made." },
  { id: 17, name: "Text Summarizer", icon: "list", category: "Language", placeholder: "Paste long text to summarize...", prompt: "Summarize the user's text into key points. Provide a 2-3 sentence summary, then 3-5 bullet points of the main takeaways." },
  { id: 18, name: "Paraphraser", icon: "refresh", category: "Language", placeholder: "Paste text to rephrase...", prompt: "Paraphrase the user's text while keeping the same meaning. Provide 2 alternative versions: one formal and one casual." },

  // --- Productivity (19-26) ---
  { id: 19, name: "Todo List Maker", icon: "list", category: "Productivity", placeholder: "Plan my day: gym, work, study, cook dinner...", prompt: "Create a structured todo list based on the user's input. Organize tasks by priority (High/Medium/Low) and suggest time estimates for each." },
  { id: 20, name: "Meeting Notes", icon: "file", category: "Productivity", placeholder: "Meeting about Q3 product launch, discussed timeline, budget...", prompt: "Organize the user's input into professional meeting notes. Include: Attendees (if mentioned), Agenda items, Key decisions, Action items with assignees." },
  { id: 21, name: "Goal Planner", icon: "target", category: "Productivity", placeholder: "I want to learn Python in 3 months...", prompt: "Create a detailed goal plan based on the user's input. Break it into weekly milestones, list resources needed, and suggest metrics to track progress." },
  { id: 22, name: "Time Blocking", icon: "clock", category: "Productivity", placeholder: "I have work 9-5, want to study 2hrs, exercise 1hr...", prompt: "Create a time-blocked daily schedule based on the user's input. Format as a table with time slots, activities, and breaks. Optimize for productivity." },
  { id: 23, name: "Habit Tracker Plan", icon: "check", category: "Productivity", placeholder: "I want to build habits: read, exercise, meditate...", prompt: "Design a habit tracking plan based on the user's input. Include the habits, frequency, a simple tracking method, milestones, and tips for consistency." },
  { id: 24, name: "Decision Maker", icon: "compass", category: "Productivity", placeholder: "Should I switch jobs? Current: 12LPA, new offer: 18LPA but more travel...", prompt: "Help the user make a decision based on their input. List pros and cons of each option, identify key factors, and give a structured recommendation." },
  { id: 25, name: "Project Planner", icon: "briefcase", category: "Productivity", placeholder: "Building a mobile app for food delivery...", prompt: "Create a project plan based on the user's input. Include phases, tasks, estimated timeline, resources needed, and potential risks. Format as a structured document." },
  { id: 26, name: "Brainstorm Ideas", icon: "bulb", category: "Productivity", placeholder: "Ideas for a side business with low investment...", prompt: "Generate 10 creative ideas based on the user's input. For each idea, give a 1-line description and why it could work. Be creative and practical." },

  // --- Education (27-32) ---
  { id: 27, name: "Concept Explainer", icon: "bulb", category: "Education", placeholder: "Explain quantum computing like I'm 15...", prompt: "Explain the concept provided by the user in simple, easy-to-understand terms. Use analogies, examples, and avoid jargon. Adjust complexity to their level." },
  { id: 28, name: "Quiz Generator", icon: "check", category: "Education", placeholder: "Create a quiz on Indian History, 10 questions...", prompt: "Create a quiz based on the user's input. Generate 10 multiple-choice questions with 4 options each. Put answers at the end. Vary difficulty." },
  { id: 29, name: "Flashcards", icon: "layers", category: "Education", placeholder: "Create flashcards for Spanish vocabulary...", prompt: "Create flashcards based on the user's input. Format as: Front (question/term) -> Back (answer/definition). Generate 15-20 flashcards." },
  { id: 30, name: "Math Solver", icon: "calculator", category: "Education", placeholder: "Solve: 3x + 7 = 22, find x...", prompt: "Solve the math problem provided by the user. Show step-by-step working, explain each step, and give the final answer clearly." },
  { id: 31, name: "Study Guide", icon: "book", category: "Education", placeholder: "Study guide for Class 10 Science: Light and Optics...", prompt: "Create a study guide based on the user's input. Include key concepts, formulas, important definitions, common question types, and study tips." },
  { id: 32, name: "Language Teacher", icon: "translate", category: "Education", placeholder: "Teach me basic Japanese greetings...", prompt: "Act as a language teacher. Based on the user's input, teach key phrases with pronunciation, usage examples, and cultural tips. Format clearly." },

  // --- Business & Finance (33-38) ---
  { id: 33, name: "Business Plan", icon: "briefcase", category: "Business", placeholder: "Starting an online t-shirt brand...", prompt: "Create a mini business plan based on the user's input. Include: concept, target market, revenue model, marketing strategy, initial costs, and 6-month milestones." },
  { id: 34, name: "SWOT Analysis", icon: "grid", category: "Business", placeholder: "SWOT for a local coffee shop competing with chains...", prompt: "Create a SWOT analysis based on the user's input. List 4-5 items each for Strengths, Weaknesses, Opportunities, and Threats. Format as a table." },
  { id: 35, name: "Pitch Deck", icon: "rocket", category: "Business", placeholder: "Pitch for an AI-powered fitness app...", prompt: "Create a pitch deck outline based on the user's input. Include 8-10 slides: Problem, Solution, Market, Product, Traction, Business Model, Competition, Team, Financials, Ask." },
  { id: 36, name: "Budget Planner", icon: "calculator", category: "Business", placeholder: "Monthly income: 50000, rent: 15000, want to save...", prompt: "Create a personal budget plan based on the user's input. Break down income into categories: essentials, savings, investments, and discretionary. Use percentages and amounts." },
  { id: 37, name: "Marketing Copy", icon: "zap", category: "Business", placeholder: "Instagram ad copy for a new protein powder brand...", prompt: "Write compelling marketing copy based on the user's input. Include a catchy headline, body copy, call-to-action, and 5 relevant hashtags. Make it persuasive." },
  { id: 38, name: "Tagline Generator", icon: "sparkle", category: "Business", placeholder: "Taglines for a eco-friendly packaging company...", prompt: "Generate 15 catchy taglines based on the user's input. Make them memorable, short, and impactful. Vary the tone from professional to playful." },

  // --- Creative (39-44) ---
  { id: 39, name: "Joke Generator", icon: "smile", category: "Creative", placeholder: "Tell me a joke about programmers...", prompt: "Generate 5 funny jokes based on the user's input. Make them clean, clever, and genuinely funny. Vary the style (wordplay, situational, etc.)." },
  { id: 40, name: "Song Lyrics", icon: "music", category: "Creative", placeholder: "Write lyrics about chasing dreams...", prompt: "Write song lyrics based on the user's input. Include 2 verses, a chorus, and a bridge. Add rhythm and rhyme. Mention a suggested genre/style." },
  { id: 41, name: "Movie Pitch", icon: "film", category: "Creative", placeholder: "A sci-fi movie about time-traveling chefs...", prompt: "Create a movie pitch based on the user's input. Include: title, genre, logline (1 sentence), plot summary, main characters, and target audience." },
  { id: 42, name: "Character Bio", icon: "user", category: "Creative", placeholder: "Create a character: a detective with a fear of the dark...", prompt: "Create a detailed character profile based on the user's input. Include: name, age, appearance, personality, backstory, strengths, weaknesses, and motivations." },
  { id: 43, name: "Recipe Creator", icon: "coffee", category: "Creative", placeholder: "Something with chicken, rice, and spices...", prompt: "Create a recipe based on the user's ingredients/request. Include: name, prep time, cook time, ingredients list, step-by-step instructions, and serving size." },
  { id: 44, name: "Gift Ideas", icon: "gift", category: "Creative", placeholder: "Gift for my mom who loves gardening, budget 2000...", prompt: "Suggest 10 thoughtful gift ideas based on the user's input. For each, explain why it's a good choice and estimate the price range in INR." },

  // --- Utilities (45-50) ---
  { id: 45, name: "Instagram Bio", icon: "camera", category: "Utility", placeholder: "I'm a travel photographer and foodie...", prompt: "Write 5 creative Instagram bio options based on the user's input. Each under 150 characters. Include relevant emojis (use text descriptors like [camera]) and a call-to-action." },
  { id: 46, name: "Hashtag Generator", icon: "trending", category: "Utility", placeholder: "Post about a beach vacation in Goa...", prompt: "Generate 25 relevant hashtags based on the user's input. Mix popular and niche tags. Organize by category (broad, specific, location, niche)." },
  { id: 47, name: "Tweet Writer", icon: "message", category: "Utility", placeholder: "Tweet about my startup launch...", prompt: "Write 3 tweet options based on the user's input. Each under 280 characters. Make them engaging, with a hook and call-to-action. Suggest hashtags." },
  { id: 48, name: "Caption Creator", icon: "image", category: "Utility", placeholder: "Photo of sunset at Marine Drive Mumbai...", prompt: "Write 5 engaging social media captions based on the user's input. Vary the tone (funny, poetic, informative, trendy). Keep each under 200 characters." },
  { id: 49, name: "Text Counter", icon: "list", category: "Utility", placeholder: "Paste text to analyze...", prompt: "Analyze the user's text and provide: word count, character count (with and without spaces), sentence count, estimated reading time, and a brief readability assessment." },
  { id: 50, name: "Name Generator", icon: "sparkle", category: "Utility", placeholder: "Name my new tech startup, it does AI for retail...", prompt: "Generate 15 creative names based on the user's input. For each, explain the meaning/inspiration. Include a mix of modern, classic, and quirky options." },

  // --- Live Data (51-70) — fetch REAL info from free APIs, no AI key needed ---
  { id: 51, name: "Current Time", icon: "clock", category: "Live Data", placeholder: "Enter timezone, e.g. Asia/Kolkata or Europe/London (blank = IST)...", live: true, action: "time" },
  { id: 52, name: "Wikipedia Search", icon: "book", category: "Live Data", placeholder: "Search any topic, e.g. 'Albert Einstein' or 'Quantum physics'...", live: true, action: "wikipedia" },
  { id: 53, name: "Weather", icon: "cloud", category: "Live Data", placeholder: "Enter city name, e.g. 'Mumbai' or 'Delhi'...", live: true, action: "weather" },
  { id: 54, name: "Dictionary", icon: "translate", category: "Live Data", placeholder: "Enter a word to look up definitions, e.g. 'serendipity'...", live: true, action: "dictionary" },
  { id: 55, name: "Currency Converter", icon: "dollar", category: "Live Data", placeholder: "Enter: 100 USD to INR...", live: true, action: "currency" },
  { id: 56, name: "Number Fact", icon: "calculator", category: "Live Data", placeholder: "Enter a number, or 'random' for a random fact...", live: true, action: "number_fact" },
  { id: 57, name: "Random Quote", icon: "sparkle", category: "Live Data", placeholder: "Click Run to get an inspiring quote (no input needed)...", live: true, action: "quote" },
  { id: 58, name: "Random Joke", icon: "smile", category: "Live Data", placeholder: "Click Run for a random joke (no input needed)...", live: true, action: "joke" },
  { id: 59, name: "IP Info", icon: "globe", category: "Live Data", placeholder: "Click Run to see your IP and location info...", live: true, action: "ip_info" },
  { id: 60, name: "Hacker News Top 5", icon: "trending", category: "Live Data", placeholder: "Click Run to fetch the top 5 stories from Hacker News...", live: true, action: "hackernews" },
  { id: 61, name: "Country Info", icon: "flag", category: "Live Data", placeholder: "Enter a country name, e.g. 'India' or 'Japan'...", live: true, action: "country" },
  { id: 62, name: "NASA Space Photo", icon: "sun", category: "Live Data", placeholder: "Click Run to see NASA's Astronomy Picture of the Day...", live: true, action: "space" },
  { id: 63, name: "GitHub User Info", icon: "code", category: "Live Data", placeholder: "Enter a GitHub username, e.g. 'torvalds'...", live: true, action: "github" },
  { id: 64, name: "Random Advice", icon: "compass", category: "Live Data", placeholder: "Click Run to get a random piece of advice...", live: true, action: "advice" },
  { id: 65, name: "Dog Photo", icon: "heart", category: "Live Data", placeholder: "Click Run to get a random cute dog photo URL...", live: true, action: "dog" },
  { id: 66, name: "Cat Fact", icon: "sparkle", category: "Live Data", placeholder: "Click Run to get a random fun fact about cats...", live: true, action: "cat_fact" },
  { id: 67, name: "Trivia Question", icon: "target", category: "Live Data", placeholder: "Click Run to get a random multiple-choice trivia question...", live: true, action: "trivia" },
  { id: 68, name: "Sunrise & Sunset", icon: "sun", category: "Live Data", placeholder: "Enter a city name to get sunrise/sunset times...", live: true, action: "sunrise" },
  { id: 69, name: "HTTP Status Lookup", icon: "link", category: "Live Data", placeholder: "Enter an HTTP status code, e.g. 404 or 200...", live: true, action: "http_status" },
  { id: 70, name: "QR Code Generator", icon: "key", category: "Live Data", placeholder: "Enter text or URL to generate a QR code...", live: true, action: "qr_code" },

  // --- NEW Live Data (71-76) ---
  { id: 71, name: "Stock Market", icon: "trending", category: "Live Data", placeholder: "Enter NSE symbol, e.g. RELIANCE, TCS, INFY, HDFCBANK...", live: true, action: "stock" },
  { id: 72, name: "Cricket Scores", icon: "trophy", category: "Live Data", placeholder: "Click Run to see live & recent cricket matches...", live: true, action: "cricket" },
  { id: 73, name: "News Headlines", icon: "file", category: "Live Data", placeholder: "Enter a topic (e.g. 'India', 'Technology', 'Sports') or leave blank...", live: true, action: "news" },
  { id: 74, name: "Movie/TV Info", icon: "film", category: "Live Data", placeholder: "Enter a TV show or movie name, e.g. 'Breaking Bad' or 'Inception'...", live: true, action: "movies" },
  { id: 75, name: "YouTube Search", icon: "play", category: "Live Data", placeholder: "Enter a search term, e.g. 'Python tutorial' or 'Indian cooking'...", live: true, action: "youtube" },
  { id: 76, name: "Unit Converter", icon: "calculator", category: "Live Data", placeholder: "Enter like: '5 kg to lbs' or '30 C to F' or '1 km to miles'...", live: true, action: "unit_converter" },
];

// Group tools by category for UI rendering
const TOOL_CATEGORIES = {};
TOOLS.forEach(t => {
  if (!TOOL_CATEGORIES[t.category]) TOOL_CATEGORIES[t.category] = [];
  TOOL_CATEGORIES[t.category].push(t);
});
