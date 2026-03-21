import type {
  Character,
  Episode,
  Location,
  Project,
  RenderJob,
  Notification,
  DashboardStats,
  Track,
  BibleEntry,
  MarketplaceItem,
  Trend,
} from "@/lib/types";

/* ------------------------------------------------------------------ */
/*  Dashboard Stats                                                    */
/* ------------------------------------------------------------------ */

export const dashboardStats: DashboardStats = {
  totalProjects: 12,
  activeRenders: 3,
  totalEpisodes: 47,
  totalCharacters: 86,
  renderHoursUsed: 142,
  renderHoursLimit: 200,
  storageUsedGB: 34,
  storageLimitGB: 100,
};

/* ------------------------------------------------------------------ */
/*  Projects                                                           */
/* ------------------------------------------------------------------ */

export const mockProjects: Project[] = [
  {
    id: "proj-1",
    name: "Neon Ronin",
    description: "A cyberpunk saga set in Neo-Tokyo 2087",
    genre: "Sci-Fi",
    style: "Anime",
    episodes: 12,
    status: "in_progress",
    thumbnail: "/thumbnails/neon-ronin.jpg",
    createdAt: "2026-01-15T10:00:00Z",
    updatedAt: "2026-03-20T14:30:00Z",
  },
  {
    id: "proj-2",
    name: "Whiskers & Wands",
    description: "Magical cats defend a whimsical kingdom",
    genre: "Fantasy",
    style: "Cartoon",
    episodes: 8,
    status: "rendering",
    thumbnail: "/thumbnails/whiskers.jpg",
    createdAt: "2026-02-01T09:00:00Z",
    updatedAt: "2026-03-19T11:00:00Z",
  },
  {
    id: "proj-3",
    name: "The Last Signal",
    description: "Deep-space horror aboard a derelict station",
    genre: "Horror",
    style: "Realistic",
    episodes: 6,
    status: "draft",
    thumbnail: "/thumbnails/last-signal.jpg",
    createdAt: "2026-03-10T16:00:00Z",
    updatedAt: "2026-03-18T08:00:00Z",
  },
  {
    id: "proj-4",
    name: "Bloom Academy",
    description: "Slice-of-life at a school for gifted florists",
    genre: "Slice of Life",
    style: "Anime",
    episodes: 24,
    status: "completed",
    thumbnail: "/thumbnails/bloom.jpg",
    createdAt: "2025-11-01T12:00:00Z",
    updatedAt: "2026-02-28T17:00:00Z",
  },
];

/* ------------------------------------------------------------------ */
/*  Render Jobs                                                        */
/* ------------------------------------------------------------------ */

export const mockRenderJobs: RenderJob[] = [
  {
    id: "rj-1",
    projectId: "proj-1",
    episodeId: "ep-1",
    episodeName: "Neon Ronin - Ep 7: Blade Rain",
    resolution: "4K",
    status: "rendering",
    progress: 67,
    estimatedTime: "2h 14m",
    gpu: "A100 x4",
    startedAt: "2026-03-21T08:00:00Z",
  },
  {
    id: "rj-2",
    projectId: "proj-2",
    episodeId: "ep-2",
    episodeName: "Whiskers & Wands - Ep 3: The Ember Crown",
    resolution: "1080p",
    status: "queued",
    progress: 0,
    estimatedTime: "45m",
    gpu: "A100 x2",
  },
  {
    id: "rj-3",
    projectId: "proj-1",
    episodeId: "ep-3",
    episodeName: "Neon Ronin - Ep 8: Ghost Protocol",
    resolution: "4K",
    status: "queued",
    progress: 0,
    estimatedTime: "3h 05m",
    gpu: "A100 x4",
  },
  {
    id: "rj-4",
    projectId: "proj-4",
    episodeId: "ep-4",
    episodeName: "Bloom Academy - Ep 24: Petals & Promises",
    resolution: "1080p",
    status: "completed",
    progress: 100,
    estimatedTime: "0m",
    gpu: "A100 x2",
    startedAt: "2026-03-20T06:00:00Z",
  },
  {
    id: "rj-5",
    projectId: "proj-3",
    episodeId: "ep-5",
    episodeName: "The Last Signal - Ep 1: Arrival",
    resolution: "4K",
    status: "failed",
    progress: 34,
    estimatedTime: "—",
    gpu: "A100 x4",
    startedAt: "2026-03-19T14:00:00Z",
  },
  {
    id: "rj-6",
    projectId: "proj-1",
    episodeId: "ep-6",
    episodeName: "Neon Ronin - Ep 9: Digital Requiem",
    resolution: "720p",
    status: "completed",
    progress: 100,
    estimatedTime: "0m",
    gpu: "A100 x1",
    startedAt: "2026-03-18T10:00:00Z",
  },
  {
    id: "rj-7",
    projectId: "proj-2",
    episodeId: "ep-7",
    episodeName: "Whiskers & Wands - Ep 4: Moonlit Paws",
    resolution: "1080p",
    status: "rendering",
    progress: 23,
    estimatedTime: "1h 35m",
    gpu: "A100 x2",
    startedAt: "2026-03-21T09:30:00Z",
  },
];

/* ------------------------------------------------------------------ */
/*  Notifications                                                      */
/* ------------------------------------------------------------------ */

export const mockNotifications: Notification[] = [
  {
    id: "n-1",
    type: "success",
    title: "Render Complete",
    message: "Bloom Academy Ep 24 finished rendering in 1080p.",
    read: false,
    createdAt: "2026-03-21T07:30:00Z",
  },
  {
    id: "n-2",
    type: "info",
    title: "New Model Available",
    message: "AnimeDiffusion v3.2 is now available in the model hub.",
    read: false,
    createdAt: "2026-03-21T06:00:00Z",
  },
  {
    id: "n-3",
    type: "warning",
    title: "Storage Warning",
    message: "You have used 34% of your cloud storage allocation.",
    read: true,
    createdAt: "2026-03-20T18:00:00Z",
  },
  {
    id: "n-4",
    type: "success",
    title: "Episode Published",
    message: "Neon Ronin Ep 6 has been published to your channel.",
    read: true,
    createdAt: "2026-03-20T12:00:00Z",
  },
  {
    id: "n-5",
    type: "error",
    title: "Voice Sync Failed",
    message: "Voice sync for Whiskers Ep 2 failed. Retry available.",
    read: true,
    createdAt: "2026-03-19T22:00:00Z",
  },
];

/* ------------------------------------------------------------------ */
/*  Tracks (Soundtrack Forge)                                          */
/* ------------------------------------------------------------------ */

export const mockTracks: Track[] = [
  {
    id: "trk-1",
    projectId: "proj-1",
    name: "Neon Downpour",
    mood: "Intense",
    genre: "Electronic",
    duration: "2:34",
    bpm: 140,
    status: "ready",
    assignedTo: "Ep 7: Blade Rain",
  },
  {
    id: "trk-2",
    projectId: "proj-1",
    name: "Rooftop Requiem",
    mood: "Melancholy",
    genre: "Piano",
    duration: "3:12",
    bpm: 72,
    status: "assigned",
    assignedTo: "Ep 5: Ghosts of Shibuya",
  },
  {
    id: "trk-3",
    projectId: "proj-2",
    name: "Whisker Waltz",
    mood: "Peaceful",
    genre: "Orchestral",
    duration: "1:48",
    bpm: 96,
    status: "ready",
  },
  {
    id: "trk-4",
    projectId: "proj-1",
    name: "Chrome Heartbeat",
    mood: "Epic",
    genre: "Phonk",
    duration: "2:05",
    bpm: 160,
    status: "generating",
  },
  {
    id: "trk-5",
    projectId: "proj-3",
    name: "Void Whisper",
    mood: "Mysterious",
    genre: "Ambient",
    duration: "3:00",
    bpm: 65,
    status: "ready",
    assignedTo: "Ep 1: Arrival",
  },
  {
    id: "trk-6",
    projectId: "proj-2",
    name: "Ember Lullaby",
    mood: "Romantic",
    genre: "Lo-fi",
    duration: "2:20",
    bpm: 85,
    status: "assigned",
    assignedTo: "Ep 3: The Ember Crown",
  },
  {
    id: "trk-7",
    projectId: "proj-1",
    name: "Synth Uprising",
    mood: "Epic",
    genre: "Electronic",
    duration: "1:55",
    bpm: 150,
    status: "generating",
  },
  {
    id: "trk-8",
    projectId: "proj-4",
    name: "Petal Storm",
    mood: "Comedic",
    genre: "Orchestral",
    duration: "1:30",
    bpm: 120,
    status: "ready",
  },
];

/* ------------------------------------------------------------------ */
/*  Production Bible                                                   */
/* ------------------------------------------------------------------ */

export const mockBibleEntries: BibleEntry[] = [
  {
    id: "bible-1",
    projectId: "proj-1",
    category: "character",
    title: "Kaito Tanaka — The Neon Ronin",
    content:
      "A rogue cybernetic samurai wandering the rain-soaked streets of Neo-Tokyo 2087. Kaito lost his memories after a botched neural implant procedure. He carries a plasma katana forged from decommissioned satellite parts. His left eye is a military-grade optic scanner that glows faint indigo in the dark. Personality: stoic, honorable, haunted by fragmented dreams of a past life. He speaks in clipped sentences and never makes promises he cannot keep.",
    updatedAt: "2026-03-20T12:00:00Z",
    autoGenerated: false,
  },
  {
    id: "bible-2",
    projectId: "proj-1",
    category: "location",
    title: "Neo-Tokyo — Sector 9 (The Drench)",
    content:
      "A perpetually rain-drenched district at the lowest level of Neo-Tokyo's vertical city. Neon signs in kanji and English flicker above ramen stalls and black-market cyber clinics. The streets are narrow, barely wide enough for two people, and always wet. Holographic advertisements project onto the rain itself. The dominant colors are deep blue, magenta, and sickly green. Sector 9 never sees real sunlight — only the faint glow filtering down from the upper tiers.",
    updatedAt: "2026-03-19T08:00:00Z",
    autoGenerated: true,
  },
  {
    id: "bible-3",
    projectId: "proj-1",
    category: "lore",
    title: "The Cascade Protocol",
    content:
      "An illegal neural-network hack that lets a user temporarily merge consciousness with an AI. Side effects include memory fragmentation, identity bleed, and in rare cases, permanent ego dissolution. The protocol was originally developed by Kurosawa Corp for military applications but was banned after the Tokyo Incident of 2081. Underground clinics still offer the procedure for those desperate or reckless enough to try it.",
    updatedAt: "2026-03-18T15:00:00Z",
    autoGenerated: true,
  },
  {
    id: "bible-4",
    projectId: "proj-1",
    category: "rules",
    title: "Animation Style Rules — Neon Ronin",
    content:
      "1. Maintain 24fps cinematic feel with selective 12fps for stylized action beats.\n2. Rain is ALWAYS present in exterior shots — vary intensity by mood.\n3. Light sources must cast visible volumetric rays through moisture.\n4. Character eyes glow subtly when experiencing strong emotion.\n5. Action sequences use speed lines and smear frames inspired by classic anime.\n6. UI/HUD elements within the world use a consistent cyan-and-magenta holographic style.",
    updatedAt: "2026-03-17T10:00:00Z",
    autoGenerated: false,
  },
  {
    id: "bible-5",
    projectId: "proj-1",
    category: "timeline",
    title: "Episode 1–6 Timeline",
    content:
      "Ep 1: Kaito wakes in a cyber-clinic with no memory. Ep 2: He discovers the plasma katana and instinctively knows how to wield it. Ep 3: First encounter with the Shadow Collective — a gang that controls Sector 9. Ep 4: Kaito meets Yuki, a data-runner who recognizes his face. Ep 5: Flashbacks reveal Kaito was once an enforcer for Kurosawa Corp. Ep 6: The Shadow Collective kidnaps Yuki; Kaito storms their stronghold in the climactic Ghosts of Shibuya battle.",
    updatedAt: "2026-03-16T14:00:00Z",
    autoGenerated: false,
  },
  {
    id: "bible-6",
    projectId: "proj-1",
    category: "palette",
    title: "Color Palette — Neon Ronin",
    content:
      "Primary: Deep Indigo (#1a1a3e), Electric Cyan (#00e5ff), Hot Magenta (#ff2d7b). Secondary: Gunmetal (#2c2c3a), Neon Green (#39ff14) for toxic/danger zones, Warm Amber (#ffab40) for interior warmth. Skin tones rendered with slight blue undertone to reflect perpetual neon lighting. Shadows are never pure black — always tinted deep blue or purple.",
    updatedAt: "2026-03-15T09:00:00Z",
    autoGenerated: true,
  },
  {
    id: "bible-7",
    projectId: "proj-2",
    category: "character",
    title: "Whiskers — The Arcane Tabby",
    content:
      "A plump orange tabby cat who accidentally absorbed the powers of the Ember Crown. Whiskers can conjure small fireballs, though he mostly uses them to warm his favorite napping spots. Despite his immense power, he is lazy, food-motivated, and deeply loyal to his friends. He speaks in a slow, drowsy voice and ends sentences with a contented purr when he is comfortable.",
    updatedAt: "2026-03-14T16:00:00Z",
    autoGenerated: false,
  },
  {
    id: "bible-8",
    projectId: "proj-2",
    category: "location",
    title: "The Whiskered Keep",
    content:
      "A cozy castle made from giant yarn balls and enchanted wood, perched atop Catnip Hill. The interior is warm, filled with floating candles and oversized cushions. Every room has at least one sunbeam that shifts magically to follow the time of day. The keep is defended by enchanted scratching posts that come alive when intruders approach.",
    updatedAt: "2026-03-13T11:00:00Z",
    autoGenerated: true,
  },
];

/* ------------------------------------------------------------------ */
/*  Marketplace Items                                                  */
/* ------------------------------------------------------------------ */

export const mockMarketplaceItems: MarketplaceItem[] = [
  {
    id: "mp-1",
    name: "Cinematic Anime Pipeline",
    creator: "StudioForge",
    category: "workflow",
    price: 29.99,
    rating: 4.8,
    downloads: 12400,
    description:
      "End-to-end anime production workflow with AI storyboarding, voice sync, and auto-compositing. Optimised for 4K output.",
    tags: ["anime", "cinematic", "4K", "pipeline"],
  },
  {
    id: "mp-2",
    name: "Cyberpunk City Generator",
    creator: "NeonLabs",
    category: "template",
    price: 14.99,
    rating: 4.6,
    downloads: 8700,
    description:
      "Generate sprawling cyberpunk cityscapes with neon lighting, rain effects, and day-night cycles baked in.",
    tags: ["cyberpunk", "environment", "generator", "neon"],
  },
  {
    id: "mp-3",
    name: "Emotion Engine Preset Pack",
    creator: "AIMotion",
    category: "preset",
    price: 0,
    rating: 4.9,
    downloads: 31200,
    description:
      "24 fine-tuned emotion presets for facial animation — joy, sorrow, rage, surprise, and more with micro-expression support.",
    tags: ["emotions", "facial", "free", "animation"],
  },
  {
    id: "mp-4",
    name: "Kai — Versatile Protagonist",
    creator: "CharacterVault",
    category: "character",
    price: 9.99,
    rating: 4.7,
    downloads: 5600,
    description:
      "Fully rigged protagonist character with 12 outfit variants, 40+ expressions, and voice-ready lip sync maps.",
    tags: ["protagonist", "rigged", "versatile", "lip-sync"],
  },
  {
    id: "mp-5",
    name: "Lo-fi Beats Collection",
    creator: "SoundCraft",
    category: "soundtrack",
    price: 19.99,
    rating: 4.5,
    downloads: 9200,
    description:
      "50 royalty-free lo-fi tracks perfect for slice-of-life and chill scenes. Stems included for custom mixing.",
    tags: ["lo-fi", "chill", "royalty-free", "stems"],
  },
  {
    id: "mp-6",
    name: "Horror Atmosphere Toolkit",
    creator: "DarkFrame",
    category: "workflow",
    price: 24.99,
    rating: 4.4,
    downloads: 3800,
    description:
      "Complete horror production workflow: lighting presets, sound design triggers, camera shake effects, and tension curves.",
    tags: ["horror", "atmosphere", "sound-design", "tension"],
  },
  {
    id: "mp-7",
    name: "Chibi Character Kit",
    creator: "KawaiiStudio",
    category: "character",
    price: 0,
    rating: 4.3,
    downloads: 18500,
    description:
      "Adorable chibi character base with customisable hair, eyes, and accessories. Great for comedy shorts.",
    tags: ["chibi", "cute", "free", "customisable"],
  },
  {
    id: "mp-8",
    name: "Epic Orchestral Score Pack",
    creator: "SymphonyAI",
    category: "soundtrack",
    price: 34.99,
    rating: 4.9,
    downloads: 6100,
    description:
      "30 sweeping orchestral pieces for action, drama, and fantasy. Full stems with conductor-style tempo maps.",
    tags: ["orchestral", "epic", "drama", "action"],
  },
  {
    id: "mp-9",
    name: "Watercolor Render Preset",
    creator: "ArtisticAI",
    category: "preset",
    price: 7.99,
    rating: 4.6,
    downloads: 14300,
    description:
      "Transform any scene into a stunning watercolor painting style. Adjustable brush density and color bleed.",
    tags: ["watercolor", "stylized", "painting", "render"],
  },
  {
    id: "mp-10",
    name: "Short-Form Vertical Template",
    creator: "ViralForge",
    category: "template",
    price: 0,
    rating: 4.2,
    downloads: 27800,
    description:
      "9:16 vertical format template optimised for TikTok, Reels, and Shorts. Includes trending transition presets.",
    tags: ["vertical", "short-form", "tiktok", "free"],
  },
];

/* ------------------------------------------------------------------ */
/*  Trends                                                             */
/* ------------------------------------------------------------------ */

export const mockTrends: Trend[] = [
  {
    id: "tr-1",
    platform: "tiktok",
    title: "AI Anime Transformations",
    category: "Visual Effects",
    growth: 340,
    views: "48.2M",
    relevance: 95,
    suggestedTemplate: "Anime Style Transfer v2",
  },
  {
    id: "tr-2",
    platform: "youtube",
    title: "24-Hour AI Movie Challenge",
    category: "Content Format",
    growth: 180,
    views: "12.7M",
    relevance: 88,
    suggestedTemplate: "Rapid Film Pipeline",
  },
  {
    id: "tr-3",
    platform: "douyin",
    title: "Virtual Idol Duets",
    category: "Character",
    growth: 520,
    views: "91.5M",
    relevance: 78,
    suggestedTemplate: "Idol Character Pack",
  },
  {
    id: "tr-4",
    platform: "instagram",
    title: "Manga Panel Reels",
    category: "Visual Style",
    growth: 210,
    views: "33.1M",
    relevance: 82,
  },
  {
    id: "tr-5",
    platform: "tiktok",
    title: "Voice-Clone Storytelling",
    category: "Audio",
    growth: 275,
    views: "22.8M",
    relevance: 91,
    suggestedTemplate: "Voice Narrative Kit",
  },
  {
    id: "tr-6",
    platform: "youtube",
    title: "AI Documentary Shorts",
    category: "Content Format",
    growth: 150,
    views: "8.4M",
    relevance: 72,
  },
  {
    id: "tr-7",
    platform: "douyin",
    title: "Pixel Art Nostalgia Clips",
    category: "Visual Style",
    growth: 190,
    views: "55.3M",
    relevance: 65,
    suggestedTemplate: "Retro Pixel Preset",
  },
  {
    id: "tr-8",
    platform: "instagram",
    title: "Cinematic AI Portraits",
    category: "Visual Effects",
    growth: 310,
    views: "19.6M",
    relevance: 85,
    suggestedTemplate: "Portrait Cinema Pack",
  },
  {
    id: "tr-9",
    platform: "tiktok",
    title: "Horror Micro-Films",
    category: "Content Format",
    growth: 420,
    views: "37.9M",
    relevance: 93,
    suggestedTemplate: "Horror Atmosphere Toolkit",
  },
  {
    id: "tr-10",
    platform: "youtube",
    title: "World-Building Timelapses",
    category: "Visual Effects",
    growth: 165,
    views: "6.2M",
    relevance: 70,
  },
];

/* ------------------------------------------------------------------ */
/*  Episodes                                                           */
/* ------------------------------------------------------------------ */

export const mockEpisodes: Episode[] = [
  {
    id: "ep-1",
    projectId: "proj-1",
    number: 7,
    title: "Blade Rain",
    brief: "Kael faces the Syndicate's elite guard on the rain-soaked rooftops of Sector 9. A climactic sword fight intercut with flashbacks to his mentor's final lesson.",
    status: "animating",
    duration: "23:40",
    scenes: 18,
    progress: 58,
    agents: [
      { name: "Script Writer", status: "completed", progress: 100, startedAt: "2026-03-20T08:00:00Z", completedAt: "2026-03-20T08:45:00Z" },
      { name: "Storyboard", status: "completed", progress: 100, startedAt: "2026-03-20T08:45:00Z", completedAt: "2026-03-20T10:20:00Z" },
      { name: "Animator", status: "active", progress: 72, startedAt: "2026-03-20T10:20:00Z" },
      { name: "Voice", status: "waiting", progress: 0 },
      { name: "Music", status: "waiting", progress: 0 },
      { name: "Editor", status: "waiting", progress: 0 },
    ],
  },
  {
    id: "ep-2",
    projectId: "proj-1",
    number: 8,
    title: "Ghost Protocol",
    brief: "The crew discovers an AI anomaly deep in the undercity network. Riko must hack the mainframe before the Syndicate trace their signal.",
    status: "scripting",
    duration: "24:10",
    scenes: 22,
    progress: 12,
    agents: [
      { name: "Script Writer", status: "active", progress: 68, startedAt: "2026-03-21T06:00:00Z" },
      { name: "Storyboard", status: "waiting", progress: 0 },
      { name: "Animator", status: "waiting", progress: 0 },
      { name: "Voice", status: "waiting", progress: 0 },
      { name: "Music", status: "waiting", progress: 0 },
      { name: "Editor", status: "waiting", progress: 0 },
    ],
  },
  {
    id: "ep-3",
    projectId: "proj-2",
    number: 3,
    title: "The Ember Crown",
    brief: "Princess Whiskers must retrieve the legendary Ember Crown from the Volcano Fortress before the Dark Hound seizes it.",
    status: "voice",
    duration: "22:00",
    scenes: 16,
    progress: 75,
    agents: [
      { name: "Script Writer", status: "completed", progress: 100, startedAt: "2026-03-18T09:00:00Z", completedAt: "2026-03-18T09:30:00Z" },
      { name: "Storyboard", status: "completed", progress: 100, startedAt: "2026-03-18T09:30:00Z", completedAt: "2026-03-18T11:00:00Z" },
      { name: "Animator", status: "completed", progress: 100, startedAt: "2026-03-18T11:00:00Z", completedAt: "2026-03-19T14:00:00Z" },
      { name: "Voice", status: "active", progress: 45, startedAt: "2026-03-19T14:00:00Z" },
      { name: "Music", status: "waiting", progress: 0 },
      { name: "Editor", status: "waiting", progress: 0 },
    ],
  },
  {
    id: "ep-4",
    projectId: "proj-4",
    number: 24,
    title: "Petals & Promises",
    brief: "The final graduation ceremony brings tears and laughter as the students present their masterpiece bouquets. Hana confesses her dream.",
    status: "completed",
    duration: "24:30",
    scenes: 20,
    progress: 100,
    agents: [
      { name: "Script Writer", status: "completed", progress: 100, startedAt: "2026-02-20T08:00:00Z", completedAt: "2026-02-20T09:00:00Z" },
      { name: "Storyboard", status: "completed", progress: 100, startedAt: "2026-02-20T09:00:00Z", completedAt: "2026-02-20T11:30:00Z" },
      { name: "Animator", status: "completed", progress: 100, startedAt: "2026-02-20T11:30:00Z", completedAt: "2026-02-22T16:00:00Z" },
      { name: "Voice", status: "completed", progress: 100, startedAt: "2026-02-22T16:00:00Z", completedAt: "2026-02-23T10:00:00Z" },
      { name: "Music", status: "completed", progress: 100, startedAt: "2026-02-23T10:00:00Z", completedAt: "2026-02-23T14:00:00Z" },
      { name: "Editor", status: "completed", progress: 100, startedAt: "2026-02-23T14:00:00Z", completedAt: "2026-02-24T12:00:00Z" },
    ],
  },
];

/* ------------------------------------------------------------------ */
/*  Characters                                                         */
/* ------------------------------------------------------------------ */

export const mockCharacters: Character[] = [
  {
    id: "char-1",
    projectId: "proj-1",
    name: "Kael",
    role: "protagonist",
    description: "A rogue street samurai seeking redemption in Neo-Tokyo.",
    appearance: "Cybernetic arm, silver hair, neon-blue eyes, long coat",
    personality: "Brooding, loyal, sharp-witted",
    voiceType: "Deep baritone",
    emotionProfile: { anger: 0.7, sadness: 0.5, joy: 0.3, fear: 0.2 },
    memoryEntries: 142,
    avatar: "/avatars/kael.jpg",
  },
  {
    id: "char-2",
    projectId: "proj-1",
    name: "Riko",
    role: "supporting",
    description: "Brilliant hacker and Kael's closest ally.",
    appearance: "Short green hair, AR visor, petite build",
    personality: "Energetic, sarcastic, fiercely intelligent",
    voiceType: "Alto, fast-paced",
    emotionProfile: { anger: 0.3, sadness: 0.2, joy: 0.8, fear: 0.4 },
    memoryEntries: 98,
    avatar: "/avatars/riko.jpg",
  },
  {
    id: "char-3",
    projectId: "proj-2",
    name: "Princess Whiskers",
    role: "protagonist",
    description: "A brave calico cat who is heir to the Crystal Throne.",
    appearance: "Calico fur, golden tiara, emerald cape",
    personality: "Courageous, kind, sometimes naive",
    voiceType: "Soprano, warm",
    emotionProfile: { anger: 0.2, sadness: 0.4, joy: 0.9, fear: 0.3 },
    memoryEntries: 67,
    avatar: "/avatars/whiskers.jpg",
  },
];

/* ------------------------------------------------------------------ */
/*  Locations                                                          */
/* ------------------------------------------------------------------ */

export const mockLocations: Location[] = [
  {
    id: "loc-1",
    projectId: "proj-1",
    name: "Sector 9 Rooftops",
    type: "urban",
    description: "Rain-soaked neon rooftops overlooking the megacity skyline.",
    mood: "Tense",
    lighting: "Neon reflections on wet surfaces",
    timeOfDay: "night",
    usedInEpisodes: [6, 7],
  },
  {
    id: "loc-2",
    projectId: "proj-1",
    name: "The Undercity",
    type: "urban",
    description: "Sprawling underground network of tunnels and black markets.",
    mood: "Mysterious",
    lighting: "Dim, flickering fluorescent",
    timeOfDay: "night",
    usedInEpisodes: [3, 5, 8],
  },
  {
    id: "loc-3",
    projectId: "proj-2",
    name: "Volcano Fortress",
    type: "fantasy",
    description: "An ancient fortress built inside a dormant volcano.",
    mood: "Epic",
    lighting: "Lava glow, dramatic shadows",
    timeOfDay: "dusk",
    usedInEpisodes: [3],
  },
];
