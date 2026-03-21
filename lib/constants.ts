export const SITE = {
  name: "SYNTHOS",
  tagline: "Synthesize stories. Ship scenes. Scale everything.",
  description:
    "The world's first AI-native production studio. Transform a single story brief into fully produced episodes with consistent characters, locations, music, and voice across unlimited episodes.",
  positioning: "Higgsfield = Camera. SYNTHOS = Studio.",
} as const;

export const FEATURES = [
  {
    icon: "🤖",
    title: "Agentic Episode Pipeline",
    description:
      "One brief, full episode. Autonomous agents cascade from script to storyboard to video to voice to music to final edit.",
  },
  {
    icon: "🧠",
    title: "Total Memory Architecture",
    description:
      "Characters remember everything — faces, outfits, scars, emotions, relationships — across episodes and seasons.",
  },
  {
    icon: "🎨",
    title: "Anime-Native Rendering",
    description:
      "Built for anime from day one. Illustrious-SDXL, cel-shading pipelines, JJK/Chainsaw Man aesthetic presets.",
  },
  {
    icon: "🎵",
    title: "Soundtrack Forge",
    description:
      "Every scene gets its own AI-composed score. Battle phonk, ambient piano, orchestral swells — auto-matched to mood.",
  },
  {
    icon: "🔀",
    title: "Visual Workflow Canvas",
    description:
      "See your entire production as a node graph. Drag, connect, swap models, A/B test branches, fork storylines.",
  },
  {
    icon: "💫",
    title: "Emotion Choreography",
    description:
      "Direct emotions like a real director. Per-shot intensity curves sync facial expression, voice tone, music, and camera.",
  },
  {
    icon: "🌐",
    title: "Multilingual Story Engine",
    description:
      "Write in English, render in Japanese, prompt in Chinese. Native multilingual production, not just dubbing.",
  },
  {
    icon: "📈",
    title: "Trend Radar + Auto-Adapt",
    description:
      "AI monitors viral formats across TikTok, YouTube, Douyin. Auto-suggests templates. Create your own trend presets.",
  },
  {
    icon: "🏠",
    title: "Self-Hosted Sovereign Mode",
    description:
      "Your GPU. Your data. Your rules. Full Docker stack runs on a single RTX 3090/4090/5070.",
  },
  {
    icon: "📖",
    title: "Production Bible Generator",
    description:
      "Auto-generate a complete series bible from Episode 1: character sheets, locations, palettes, lore — always in sync.",
  },
  {
    icon: "🛒",
    title: "Workflow Marketplace",
    description:
      "Package and sell your pipelines. Buy proven workflows. A creator economy for AI video production.",
  },
  {
    icon: "⚡",
    title: "Smart Render Queue",
    description:
      "Intelligent GPU routing: previews on light hardware, finals on heavy. Local + cloud hybrid with cost optimization.",
  },
] as const;

export const PRICING_TIERS = [
  {
    name: "Free",
    price: "$0",
    period: "forever",
    description: "Try the studio",
    features: [
      "5 videos/month",
      "720p resolution",
      "Basic templates",
      "Watermarked output",
      "Community support",
    ],
    cta: "Join Waitlist",
    highlighted: false,
  },
  {
    name: "Creator Pro",
    price: "$29",
    period: "/month",
    description: "For individual creators",
    features: [
      "50 videos/month",
      "1080p resolution",
      "All templates & presets",
      "Custom characters (DNA Vault)",
      "Voice cloning (3 voices)",
      "Priority rendering",
    ],
    cta: "Join Waitlist",
    highlighted: true,
  },
  {
    name: "Studio",
    price: "$99",
    period: "/month",
    description: "For pro creators & teams",
    features: [
      "Unlimited videos",
      "4K resolution",
      "API access",
      "5-seat workspace",
      "Model fine-tuning",
      "Self-hosted mode",
      "Marketplace publishing",
    ],
    cta: "Join Waitlist",
    highlighted: false,
  },
  {
    name: "Enterprise",
    price: "$299+",
    period: "/month",
    description: "For studios & agencies",
    features: [
      "Everything in Studio",
      "Unlimited seats",
      "Dedicated GPU allocation",
      "SSO & compliance",
      "White-label option",
      "Custom model training",
      "Priority support (SLA)",
    ],
    cta: "Contact Us",
    highlighted: false,
  },
] as const;

export const COMPARISON = {
  categories: [
    "Autonomous episode pipeline",
    "Cross-episode memory",
    "Anime-native rendering",
    "AI music generation",
    "Visual workflow canvas",
    "Self-hosted option",
    "Multilingual production",
    "Workflow marketplace",
    "Production bible generator",
    "Emotion choreography",
  ],
  competitors: {
    SYNTHOS: [true, true, true, true, true, true, true, true, true, true],
    Higgsfield: [
      false,
      false,
      false,
      false,
      false,
      false,
      false,
      false,
      false,
      false,
    ],
    Runway: [
      false,
      false,
      false,
      false,
      false,
      false,
      false,
      false,
      false,
      false,
    ],
    Pika: [
      false,
      false,
      false,
      false,
      false,
      false,
      false,
      false,
      false,
      false,
    ],
  },
} as const;

export const HOW_IT_WORKS_STEPS = [
  {
    step: "01",
    title: "Write Your Brief",
    description:
      'Describe your story, characters, and style. "A dark fantasy anime about a shadow warrior who enters nightmare dungeons." That\'s it.',
  },
  {
    step: "02",
    title: "AI Agents Take Over",
    description:
      "Six autonomous agents cascade: Script Writer → Storyboard → Animator → Voice → Music → Editor. Each reads from the shared memory.",
  },
  {
    step: "03",
    title: "Full Episode Delivered",
    description:
      "Receive a complete episode with consistent characters, locations, soundtrack, and voice. Memory carries forward to the next episode.",
  },
] as const;
