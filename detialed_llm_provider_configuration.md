<!DOCTYPE html>

<html class="dark" lang="en"><head>
<meta charset="utf-8"/>
<meta content="width=device-width, initial-scale=1.0" name="viewport"/>
<title>Detailed LLM Provider Configuration</title>
<script src="https://cdn.tailwindcss.com?plugins=forms,container-queries"></script>
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&amp;display=swap" rel="stylesheet"/>
<link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet"/>
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&amp;display=swap" rel="stylesheet"/>
<script id="tailwind-config">
        tailwind.config = {
            darkMode: "class",
            theme: {
                extend: {
                    colors: {
                        "primary": "#2b8cee",
                        "background-light": "#f6f7f8",
                        "background-dark": "#101922",
                    },
                    fontFamily: {
                        "display": ["Space Grotesk", "sans-serif"]
                    },
                    borderRadius: {"DEFAULT": "0.25rem", "lg": "0.5rem", "xl": "0.75rem", "full": "9999px"},
                },
            },
        }
    </script>
<style>
        /* Custom scrollbar for developer vibe */
        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }
        ::-webkit-scrollbar-track {
            background: #101922; 
        }
        ::-webkit-scrollbar-thumb {
            background: #2b8cee40; 
            border-radius: 4px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: #2b8cee80; 
        }
    </style>
</head>
<body class="bg-background-light dark:bg-background-dark text-slate-800 dark:text-slate-200 font-display h-screen flex overflow-hidden">
<!-- Sidebar: Provider List -->
<aside class="w-80 flex flex-col border-r border-slate-300 dark:border-slate-800 bg-white dark:bg-slate-900/50 flex-shrink-0">
<!-- Sidebar Header -->
<div class="p-4 border-b border-slate-300 dark:border-slate-800">
<h2 class="text-xl font-bold tracking-tight mb-4 flex items-center gap-2">
<span class="material-icons text-primary">hub</span>
                Providers
            </h2>
<div class="relative">
<span class="material-icons absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 text-sm">search</span>
<input class="w-full bg-slate-100 dark:bg-slate-800/80 border-none rounded-lg py-2 pl-9 pr-4 text-sm focus:ring-1 focus:ring-primary placeholder-slate-500" placeholder="Filter providers..." type="text"/>
</div>
</div>
<!-- Provider List -->
<div class="flex-1 overflow-y-auto p-3 space-y-1">
<!-- Section Label -->
<div class="px-3 py-2 text-xs font-semibold text-slate-500 uppercase tracking-wider">Active</div>
<!-- Active Item 1 (Selected) -->
<button class="w-full text-left px-3 py-3 rounded-lg bg-primary/10 border border-primary/20 flex items-center gap-3 group transition-all">
<div class="w-10 h-10 rounded bg-white dark:bg-slate-800 flex items-center justify-center border border-slate-200 dark:border-slate-700 shadow-sm">
<img alt="Google" class="w-6 h-6 opacity-80" data-alt="Google logo icon" src="https://lh3.googleusercontent.com/aida-public/AB6AXuDrGkzmN27wGbdKpmlxs4sTnsVQTb0WHJRG8tp3le93GKvCOfGNMJdsW4vmVPL3BD0zV9yVHDKCCfgC0iLu5i8ExuPjdLTex0OulhLLpwJU7gu5Tarml-2VcS4Q_VyHH9vUdfRVT2eh5flO88TTNCSlhZ2JhgUrjMQ52aDyktzGm4rNFf3-vHbtFqffguuHqNjd0XICd0v9nzNl3oIuYU6IVBo0OdTwhIKkVxsY04CSP-Mxsc_cuhC2KhYMmyejWnsFUtkKXNZOMVs"/>
</div>
<div class="flex-1 min-w-0">
<div class="flex items-center justify-between">
<span class="font-medium text-slate-900 dark:text-white truncate">Gemini Pro 1.5</span>
<span class="w-2 h-2 rounded-full bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.5)]"></span>
</div>
<div class="text-xs text-primary truncate">Production • v1.5-latest</div>
</div>
</button>
<!-- Active Item 2 -->
<button class="w-full text-left px-3 py-3 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 border border-transparent hover:border-slate-300 dark:hover:border-slate-700 flex items-center gap-3 group transition-all">
<div class="w-10 h-10 rounded bg-white dark:bg-slate-800 flex items-center justify-center border border-slate-200 dark:border-slate-700 shadow-sm">
<span class="material-icons text-slate-400">api</span>
</div>
<div class="flex-1 min-w-0">
<div class="flex items-center justify-between">
<span class="font-medium text-slate-900 dark:text-slate-300 truncate">OpenAI GPT-4o</span>
<span class="w-2 h-2 rounded-full bg-green-500"></span>
</div>
<div class="text-xs text-slate-500 dark:text-slate-500 truncate">Production • gpt-4o-2024</div>
</div>
</button>
<!-- Active Item 3 -->
<button class="w-full text-left px-3 py-3 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 border border-transparent hover:border-slate-300 dark:hover:border-slate-700 flex items-center gap-3 group transition-all">
<div class="w-10 h-10 rounded bg-white dark:bg-slate-800 flex items-center justify-center border border-slate-200 dark:border-slate-700 shadow-sm">
<span class="material-icons text-orange-400">bolt</span>
</div>
<div class="flex-1 min-w-0">
<div class="flex items-center justify-between">
<span class="font-medium text-slate-900 dark:text-slate-300 truncate">Anthropic Claude 3.5</span>
<span class="w-2 h-2 rounded-full bg-green-500"></span>
</div>
<div class="text-xs text-slate-500 dark:text-slate-500 truncate">Staging • sonnet</div>
</div>
</button>
<!-- Section Label -->
<div class="px-3 py-2 mt-4 text-xs font-semibold text-slate-500 uppercase tracking-wider">Inactive / Local</div>
<!-- Inactive Item -->
<button class="w-full text-left px-3 py-3 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 border border-transparent hover:border-slate-300 dark:hover:border-slate-700 flex items-center gap-3 group transition-all opacity-70 hover:opacity-100">
<div class="w-10 h-10 rounded bg-white dark:bg-slate-800 flex items-center justify-center border border-slate-200 dark:border-slate-700 shadow-sm grayscale">
<span class="material-icons text-slate-400">computer</span>
</div>
<div class="flex-1 min-w-0">
<div class="flex items-center justify-between">
<span class="font-medium text-slate-900 dark:text-slate-400 truncate">Local LLaMA 3</span>
<span class="w-2 h-2 rounded-full bg-slate-500 border border-slate-900"></span>
</div>
<div class="text-xs text-slate-500 dark:text-slate-600 truncate">Offline • localhost:11434</div>
</div>
</button>
</div>
<!-- Footer Action -->
<div class="p-4 border-t border-slate-300 dark:border-slate-800 bg-slate-50 dark:bg-slate-900/80">
<button class="w-full flex items-center justify-center gap-2 py-2 px-4 rounded-lg bg-white dark:bg-slate-800 border border-dashed border-slate-400 dark:border-slate-600 text-slate-600 dark:text-slate-400 hover:text-primary dark:hover:text-primary hover:border-primary dark:hover:border-primary transition-colors text-sm font-medium">
<span class="material-icons text-base">add</span>
                Add New Provider
            </button>
</div>
</aside>
<!-- Main Content: Configuration Form -->
<main class="flex-1 flex flex-col h-full bg-background-light dark:bg-background-dark relative overflow-hidden">
<!-- Top Bar -->
<header class="flex items-center justify-between px-8 py-5 border-b border-slate-300 dark:border-slate-800 bg-white/50 dark:bg-slate-900/30 backdrop-blur-sm z-10">
<div class="flex items-center gap-4">
<div class="p-2 rounded-lg bg-primary/20 text-primary">
<span class="material-icons">tune</span>
</div>
<div>
<h1 class="text-2xl font-bold text-slate-900 dark:text-white leading-none">Gemini Pro 1.5</h1>
<div class="text-sm text-slate-500 dark:text-slate-400 mt-1 flex items-center gap-2">
<span>Provider Configuration</span>
<span class="text-slate-700 dark:text-slate-600">/</span>
<span class="text-primary">Detailed Settings</span>
</div>
</div>
</div>
<div class="flex items-center gap-3">
<button class="flex items-center gap-2 px-4 py-2 rounded-lg bg-slate-200 dark:bg-slate-800 hover:bg-slate-300 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300 text-sm font-medium transition-colors">
<span class="material-icons text-sm">history</span>
                    Audit Logs
                </button>
<div class="h-6 w-px bg-slate-300 dark:bg-slate-700 mx-1"></div>
<button class="flex items-center gap-2 px-4 py-2 rounded-lg border border-red-500/30 text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 text-sm font-medium transition-colors">
<span class="material-icons text-sm">delete</span>
                    Delete
                </button>
</div>
</header>
<!-- Scrollable Form Area -->
<div class="flex-1 overflow-y-auto p-8 pb-32">
<div class="max-w-4xl mx-auto space-y-8">
<!-- Section: General Info -->
<section class="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-6 shadow-sm">
<div class="flex items-start justify-between mb-6">
<div>
<h3 class="text-lg font-semibold text-slate-900 dark:text-white">General Information</h3>
<p class="text-sm text-slate-500 dark:text-slate-400">Basic identification for this LLM configuration.</p>
</div>
<span class="material-icons text-slate-400">info_outline</span>
</div>
<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
<div class="space-y-2">
<label class="block text-xs font-medium uppercase tracking-wide text-slate-500 dark:text-slate-400">Configuration Name</label>
<input class="w-full bg-slate-50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-lg px-4 py-2.5 text-slate-900 dark:text-white focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition-all placeholder-slate-400" type="text" value="Gemini Pro 1.5 - Production"/>
</div>
<div class="space-y-2">
<label class="block text-xs font-medium uppercase tracking-wide text-slate-500 dark:text-slate-400">Provider Type</label>
<div class="relative">
<select class="w-full appearance-none bg-slate-50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-lg px-4 py-2.5 text-slate-900 dark:text-white focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition-all">
<option>Google Vertex AI</option>
<option>OpenAI</option>
<option>Anthropic</option>
<option>Custom / Local</option>
</select>
<span class="material-icons absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 pointer-events-none">expand_more</span>
</div>
</div>
<div class="space-y-2 md:col-span-2">
<label class="block text-xs font-medium uppercase tracking-wide text-slate-500 dark:text-slate-400">Description</label>
<textarea class="w-full bg-slate-50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-lg px-4 py-2.5 text-slate-900 dark:text-white focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition-all placeholder-slate-400 resize-none" rows="2">Main configuration for complex reasoning tasks and code generation. Used by the backend services.</textarea>
</div>
</div>
</section>
<!-- Section: Connection Settings -->
<section class="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-6 shadow-sm">
<div class="flex items-start justify-between mb-6">
<div>
<h3 class="text-lg font-semibold text-slate-900 dark:text-white">Connection Settings</h3>
<p class="text-sm text-slate-500 dark:text-slate-400">Endpoint details and authentication credentials.</p>
</div>
<span class="material-icons text-slate-400">link</span>
</div>
<div class="space-y-6">
<div class="space-y-2">
<label class="block text-xs font-medium uppercase tracking-wide text-slate-500 dark:text-slate-400">Base Endpoint URL</label>
<div class="flex rounded-lg shadow-sm">
<span class="inline-flex items-center px-3 rounded-l-lg border border-r-0 border-slate-300 dark:border-slate-700 bg-slate-100 dark:bg-slate-800 text-slate-500 text-sm font-mono">POST</span>
<input class="flex-1 min-w-0 block w-full px-4 py-2.5 rounded-none rounded-r-lg bg-slate-50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 text-slate-900 dark:text-white font-mono text-sm focus:ring-2 focus:ring-primary focus:border-transparent outline-none" type="text" value="https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"/>
</div>
</div>
<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
<div class="space-y-2">
<label class="block text-xs font-medium uppercase tracking-wide text-slate-500 dark:text-slate-400">API Key</label>
<div class="relative">
<input class="w-full bg-slate-50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-lg pl-10 pr-10 py-2.5 text-slate-900 dark:text-white font-mono text-sm focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition-all" type="password" value="AIzaSyD-xxxxxxxxxxxxxxxxxxxxxxxx"/>
<span class="material-icons absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 text-sm">key</span>
<button class="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-200 focus:outline-none">
<span class="material-icons text-sm">visibility_off</span>
</button>
</div>
</div>
<div class="space-y-2">
<label class="block text-xs font-medium uppercase tracking-wide text-slate-500 dark:text-slate-400">Project ID (Optional)</label>
<input class="w-full bg-slate-50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-lg px-4 py-2.5 text-slate-900 dark:text-white focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition-all" placeholder="GCP Project ID" type="text"/>
</div>
</div>
<div class="pt-2">
<div class="flex items-center gap-2">
<input class="w-4 h-4 text-primary bg-slate-100 dark:bg-slate-800 border-slate-300 dark:border-slate-600 rounded focus:ring-primary focus:ring-offset-0" id="stream" type="checkbox"/>
<label class="text-sm font-medium text-slate-700 dark:text-slate-300 cursor-pointer select-none" for="stream">Enable Response Streaming</label>
</div>
<p class="text-xs text-slate-500 dark:text-slate-500 mt-1 ml-6">Toggle if the provider supports Server-Sent Events (SSE) for token streaming.</p>
</div>
</div>
</section>
<!-- Section: Default Parameters -->
<section class="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-6 shadow-sm">
<div class="flex items-start justify-between mb-6">
<div>
<h3 class="text-lg font-semibold text-slate-900 dark:text-white">Generation Parameters</h3>
<p class="text-sm text-slate-500 dark:text-slate-400">Default settings for model inference control.</p>
</div>
<span class="material-icons text-slate-400">tune</span>
</div>
<div class="grid grid-cols-1 md:grid-cols-2 gap-x-12 gap-y-8">
<!-- Temperature -->
<div class="space-y-4">
<div class="flex justify-between items-center">
<label class="text-sm font-medium text-slate-700 dark:text-slate-300">Temperature</label>
<input class="w-16 bg-slate-100 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded px-2 py-1 text-right text-sm focus:ring-1 focus:ring-primary outline-none" max="2" min="0" step="0.1" type="number" value="0.7"/>
</div>
<input class="w-full h-2 bg-slate-200 dark:bg-slate-700 rounded-lg appearance-none cursor-pointer accent-primary" max="2" min="0" step="0.1" type="range" value="0.7"/>
<div class="flex justify-between text-xs text-slate-500">
<span>Precise (0.0)</span>
<span>Creative (2.0)</span>
</div>
</div>
<!-- Top P -->
<div class="space-y-4">
<div class="flex justify-between items-center">
<label class="text-sm font-medium text-slate-700 dark:text-slate-300">Top P</label>
<input class="w-16 bg-slate-100 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded px-2 py-1 text-right text-sm focus:ring-1 focus:ring-primary outline-none" max="1" min="0" step="0.05" type="number" value="0.9"/>
</div>
<input class="w-full h-2 bg-slate-200 dark:bg-slate-700 rounded-lg appearance-none cursor-pointer accent-primary" max="1" min="0" step="0.05" type="range" value="0.9"/>
<div class="flex justify-between text-xs text-slate-500">
<span>Focused (0.0)</span>
<span>Diverse (1.0)</span>
</div>
</div>
<!-- Max Tokens -->
<div class="space-y-4">
<div class="flex justify-between items-center">
<label class="text-sm font-medium text-slate-700 dark:text-slate-300">Max Tokens</label>
<span class="text-xs text-slate-500">Maximum: 8192</span>
</div>
<div class="flex items-center gap-2">
<button class="w-10 h-10 rounded-lg bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 border border-slate-300 dark:border-slate-700 flex items-center justify-center text-slate-500 transition-colors">
<span class="material-icons text-sm">remove</span>
</button>
<input class="flex-1 bg-slate-50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-lg px-4 py-2 text-center text-slate-900 dark:text-white font-mono focus:ring-2 focus:ring-primary focus:border-transparent outline-none" type="number" value="2048"/>
<button class="w-10 h-10 rounded-lg bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 border border-slate-300 dark:border-slate-700 flex items-center justify-center text-slate-500 transition-colors">
<span class="material-icons text-sm">add</span>
</button>
</div>
</div>
<!-- Stop Sequences -->
<div class="space-y-2">
<label class="block text-sm font-medium text-slate-700 dark:text-slate-300">Stop Sequences</label>
<div class="flex flex-wrap gap-2 p-3 bg-slate-50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-lg min-h-[58px]">
<span class="inline-flex items-center px-2.5 py-1 rounded bg-slate-200 dark:bg-slate-700 text-slate-700 dark:text-slate-200 text-xs font-mono">
                                    User:
                                    <button class="ml-1.5 text-slate-500 hover:text-slate-700 dark:hover:text-slate-300"><span class="material-icons text-[10px] font-bold">close</span></button>
</span>
<input class="bg-transparent border-none p-0 text-sm focus:ring-0 placeholder-slate-500 w-full max-w-[150px]" placeholder="Add stop sequence..." type="text"/>
</div>
</div>
</div>
</section>
</div>
</div>
<!-- Sticky Footer: Actions -->
<div class="absolute bottom-0 left-0 w-full bg-white dark:bg-slate-900 border-t border-slate-300 dark:border-slate-800 p-4 px-8 flex items-center justify-between z-20">
<div class="flex items-center gap-2">
<span class="w-2 h-2 rounded-full bg-green-500 animate-pulse"></span>
<span class="text-sm text-green-600 dark:text-green-400 font-medium">Last connected: 2 mins ago</span>
</div>
<div class="flex items-center gap-4">
<button class="flex items-center gap-2 px-5 py-2.5 rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 hover:bg-slate-50 dark:hover:bg-slate-700 text-slate-700 dark:text-white font-medium transition-all shadow-sm hover:shadow">
<span class="material-icons text-[18px]">wifi_tethering</span>
                    Check Connectivity
                </button>
<button class="flex items-center gap-2 px-6 py-2.5 rounded-lg bg-primary hover:bg-primary/90 text-white font-medium shadow-lg shadow-primary/20 transition-all hover:-translate-y-0.5">
<span class="material-icons text-[18px]">save</span>
                    Save Changes
                </button>
</div>
</div>
</main>
</body></html>
