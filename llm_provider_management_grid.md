<!DOCTYPE html>

<html class="dark" lang="en"><head>
<meta charset="utf-8"/>
<meta content="width=device-width, initial-scale=1.0" name="viewport"/>
<title>LLM Provider Management Grid</title>
<!-- Fonts -->
<link href="https://fonts.googleapis.com" rel="preconnect"/>
<link crossorigin="" href="https://fonts.gstatic.com" rel="preconnect"/>
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&amp;display=swap" rel="stylesheet"/>
<link href="https://fonts.googleapis.com/icon?family=Material+Icons+Round" rel="stylesheet"/>
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&amp;display=swap" rel="stylesheet"/>
<!-- Tailwind CSS -->
<script src="https://cdn.tailwindcss.com?plugins=forms,container-queries"></script>
<script id="tailwind-config">
        tailwind.config = {
            darkMode: "class",
            theme: {
                extend: {
                    colors: {
                        "primary": "#2b8cee",
                        "background-light": "#f6f7f8",
                        "background-dark": "#101922",
                        "surface-dark": "#1A2633", // Derived darker surface
                        "surface-darker": "#15202B", // Derived darker surface
                    },
                    fontFamily: {
                        "display": ["Space Grotesk", "sans-serif"]
                    },
                    borderRadius: {"DEFAULT": "0.25rem", "lg": "0.5rem", "xl": "0.75rem", "2xl": "1rem", "full": "9999px"},
                },
            },
        }
    </script>
<style>
        /* Custom scrollbar for dark theme */
        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }
        ::-webkit-scrollbar-track {
            background: #101922; 
        }
        ::-webkit-scrollbar-thumb {
            background: #2b8cee; 
            border-radius: 4px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: #2374c6; 
        }
    </style>
</head>
<body class="bg-background-light dark:bg-background-dark text-slate-900 dark:text-slate-100 font-display antialiased selection:bg-primary selection:text-white min-h-screen flex flex-col">
<!-- Navbar / App Header -->
<header class="w-full border-b border-slate-200 dark:border-slate-800 bg-white dark:bg-surface-darker sticky top-0 z-30">
<div class="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
<div class="flex items-center gap-4">
<div class="w-8 h-8 rounded-lg bg-primary flex items-center justify-center text-white font-bold text-xl">P</div>
<div class="h-6 w-px bg-slate-300 dark:bg-slate-700"></div>
<nav class="flex items-center text-sm font-medium text-slate-500 dark:text-slate-400">
<a class="hover:text-primary transition-colors" href="#">Settings</a>
<span class="mx-2">/</span>
<span class="text-slate-900 dark:text-white">LLM Providers</span>
</nav>
</div>
<div class="flex items-center gap-4">
<div class="flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20">
<span class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
<span class="text-xs font-medium text-emerald-500">System Healthy</span>
</div>
<button class="p-2 rounded-full hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors text-slate-500">
<span class="material-icons-round text-xl">notifications</span>
</button>
<div class="w-8 h-8 rounded-full bg-gradient-to-tr from-primary to-purple-500 p-[2px]">
<img alt="User Avatar" class="rounded-full w-full h-full object-cover border-2 border-white dark:border-surface-darker" data-alt="Portrait of a user" src="https://lh3.googleusercontent.com/aida-public/AB6AXuD4minP4Pas2Ki545iiuCQEPSBCNHM83GL9Tq5kvNkA6NCwi5gu9CTRTjrfHj_N6vQuygIqz-rF3g2E3YlAZinpvmQ9P-smL_4A9zhEn5pTGB7EBDwoLqsDbz9_sC33pJ6v05V078-vTybvOoS6YM3HVfBRKH6chs5yROqdb7VndZWXLABoVpnwhIeyE6b-pXN90Of9BqSfb5GnyL9LSSRo0i7ydiXUREyJCxFkiySuAFOPpHpgj_zU0sg70dMpxrmegCLdRDreeAQ"/>
</div>
</div>
</div>
</header>
<!-- Main Content -->
<main class="flex-1 max-w-7xl w-full mx-auto px-6 py-8">
<!-- Section Header -->
<div class="flex flex-col md:flex-row md:items-end justify-between gap-6 mb-10">
<div>
<h1 class="text-3xl font-bold text-slate-900 dark:text-white mb-2">Provider Connections</h1>
<p class="text-slate-500 dark:text-slate-400 max-w-xl">
                    Manage your connections to LLM providers. Configure API keys, endpoints, and default models for your prompt engineering workflow.
                </p>
</div>
<div class="flex items-center gap-3">
<button class="flex items-center gap-2 px-4 py-2.5 rounded-lg bg-surface-dark border border-slate-700 hover:bg-slate-800 text-slate-300 transition-all text-sm font-medium">
<span class="material-icons-round text-base">refresh</span>
                    Sync Models
                </button>
<button class="flex items-center gap-2 px-5 py-2.5 rounded-lg bg-primary hover:bg-blue-600 text-white shadow-lg shadow-primary/25 transition-all transform active:scale-95 font-medium">
<span class="material-icons-round text-xl">add</span>
                    Add New Provider
                </button>
</div>
</div>
<!-- Connection Stats -->
<div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
<div class="bg-white dark:bg-surface-dark rounded-xl p-4 border border-slate-200 dark:border-slate-800 flex items-center gap-4">
<div class="p-3 rounded-lg bg-primary/10 text-primary">
<span class="material-icons-round">link</span>
</div>
<div>
<p class="text-xs text-slate-500 uppercase tracking-wider font-semibold">Total Connected</p>
<p class="text-2xl font-bold text-slate-900 dark:text-white">3</p>
</div>
</div>
<div class="bg-white dark:bg-surface-dark rounded-xl p-4 border border-slate-200 dark:border-slate-800 flex items-center gap-4">
<div class="p-3 rounded-lg bg-emerald-500/10 text-emerald-500">
<span class="material-icons-round">check_circle</span>
</div>
<div>
<p class="text-xs text-slate-500 uppercase tracking-wider font-semibold">Active Sessions</p>
<p class="text-2xl font-bold text-slate-900 dark:text-white">12</p>
</div>
</div>
<div class="bg-white dark:bg-surface-dark rounded-xl p-4 border border-slate-200 dark:border-slate-800 flex items-center gap-4">
<div class="p-3 rounded-lg bg-amber-500/10 text-amber-500">
<span class="material-icons-round">speed</span>
</div>
<div>
<p class="text-xs text-slate-500 uppercase tracking-wider font-semibold">Avg Latency</p>
<p class="text-2xl font-bold text-slate-900 dark:text-white">240ms</p>
</div>
</div>
<div class="bg-white dark:bg-surface-dark rounded-xl p-4 border border-slate-200 dark:border-slate-800 flex items-center gap-4">
<div class="p-3 rounded-lg bg-rose-500/10 text-rose-500">
<span class="material-icons-round">warning</span>
</div>
<div>
<p class="text-xs text-slate-500 uppercase tracking-wider font-semibold">Errors (24h)</p>
<p class="text-2xl font-bold text-slate-900 dark:text-white">0</p>
</div>
</div>
</div>
<!-- Provider Grid -->
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
<!-- OpenAI Card (Connected) -->
<div class="group relative bg-white dark:bg-surface-dark rounded-xl border border-slate-200 dark:border-slate-800 hover:border-primary dark:hover:border-primary transition-all duration-300 shadow-sm hover:shadow-lg hover:shadow-primary/5 overflow-hidden">
<div class="absolute top-0 left-0 w-full h-1 bg-emerald-500"></div>
<div class="p-6">
<div class="flex justify-between items-start mb-4">
<div class="w-12 h-12 rounded-lg bg-white dark:bg-slate-800 p-2 flex items-center justify-center shadow-inner border border-slate-100 dark:border-slate-700">
<!-- Placeholder for OpenAI Logo -->
<svg class="w-8 h-8 text-slate-900 dark:text-white" fill="currentColor" viewbox="0 0 24 24"><path d="M22.2819 9.8211a5.9847 5.9847 0 0 0-.5157-4.9108 6.0462 6.0462 0 0 0-6.5098-2.9A6.0651 6.0651 0 0 0 4.9807 4.1818a5.9847 5.9847 0 0 0-3.9977 2.9 6.0462 6.0462 0 0 0 .7427 7.0966 5.98 5.98 0 0 0 .511 4.9107 6.0462 6.0462 0 0 0 6.5146 2.9001A5.9847 5.9847 0 0 0 13.2599 24a6.0557 6.0557 0 0 0 5.7718-4.2058 5.9894 5.9894 0 0 0 3.9977-2.9001 6.0557 6.0557 0 0 0-.7475-7.0729zm-9.022 12.6081a4.4755 4.4755 0 0 1-2.8764-1.0408l.1419-.0843 3.5366-1.9718a3.1335 3.1335 0 0 0 1.5528 2.0837l.0136.0088-.0529.044a4.522 4.522 0 0 1-2.3156.9604zm-7.007-1.6343a4.484 4.484 0 0 1-1.0069-2.9197l.1419.0833 3.5366 1.9718a3.14 3.14 0 0 0-.0908 2.5925l-.0148.0061-.0612-.0292a4.5364 4.5364 0 0 1-2.5048-1.7048zm-.1278-7.2343a4.5126 4.5126 0 0 1 1.8741-2.438l.1432-.0797 3.5366 1.9732a3.14 3.14 0 0 0-1.6428 1.996l-.0148-.0072-.0612-.0318a4.538 4.538 0 0 1-3.8351-1.4125zm7.1328-5.3262a4.498 4.498 0 0 1 2.8787 1.0372l-.1419.0827-3.5366 1.9732a3.1398 3.1398 0 0 0-1.5542-2.0864l-.0136-.0083.0529-.044a4.526 4.526 0 0 1 2.3147-.9544zm7.0049 1.6366a4.509 4.509 0 0 1 1.009 2.9179l-.1419-.0848-3.5366-1.9718a3.14 3.14 0 0 0 .0908-2.5898l.0148-.0066.0612.0298a4.5397 4.5397 0 0 1 2.5027 1.7053zm.1278 7.2344a4.5222 4.5222 0 0 1-1.8741 2.438l-.1432.0796-3.5366-1.9731a3.1335 3.1335 0 0 0 1.6428-1.9961l.0148.0072.0612.0318a4.5413 4.5413 0 0 1 3.8351 1.4126zM12 14.1563a2.1563 2.1563 0 1 1 2.1563-2.1563A2.1563 2.1563 0 0 1 12 14.1563z"></path></svg>
</div>
<div class="flex items-center gap-2">
<div class="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20">
<span class="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
<span class="text-xs font-semibold text-emerald-500">Connected</span>
</div>
</div>
</div>
<h3 class="text-xl font-bold text-slate-900 dark:text-white mb-1 group-hover:text-primary transition-colors">OpenAI</h3>
<p class="text-sm text-slate-500 dark:text-slate-400 mb-6">GPT-4 Turbo, GPT-3.5 Turbo</p>
<div class="flex items-center justify-between border-t border-slate-100 dark:border-slate-800 pt-4 mt-auto">
<div class="flex flex-col">
<span class="text-[10px] uppercase text-slate-400 font-bold tracking-wider">Default Model</span>
<span class="text-sm font-medium text-slate-700 dark:text-slate-300">gpt-4-turbo</span>
</div>
<button class="w-8 h-8 rounded-lg flex items-center justify-center text-slate-400 hover:text-primary hover:bg-primary/10 transition-colors">
<span class="material-icons-round text-lg">settings</span>
</button>
</div>
</div>
</div>
<!-- Anthropic Card (Connected) -->
<div class="group relative bg-white dark:bg-surface-dark rounded-xl border border-slate-200 dark:border-slate-800 hover:border-primary dark:hover:border-primary transition-all duration-300 shadow-sm hover:shadow-lg hover:shadow-primary/5 overflow-hidden">
<div class="absolute top-0 left-0 w-full h-1 bg-emerald-500"></div>
<div class="p-6">
<div class="flex justify-between items-start mb-4">
<div class="w-12 h-12 rounded-lg bg-white dark:bg-slate-800 p-2 flex items-center justify-center shadow-inner border border-slate-100 dark:border-slate-700 overflow-hidden">
<!-- Anthropic Logo (Simulated) -->
<div class="w-8 h-8 bg-slate-900 dark:bg-white rounded-md flex items-center justify-center text-white dark:text-slate-900 font-bold text-lg">A</div>
</div>
<div class="flex items-center gap-2">
<div class="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20">
<span class="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
<span class="text-xs font-semibold text-emerald-500">Connected</span>
</div>
</div>
</div>
<h3 class="text-xl font-bold text-slate-900 dark:text-white mb-1 group-hover:text-primary transition-colors">Anthropic</h3>
<p class="text-sm text-slate-500 dark:text-slate-400 mb-6">Claude 3 Opus, Claude 3 Sonnet</p>
<div class="flex items-center justify-between border-t border-slate-100 dark:border-slate-800 pt-4 mt-auto">
<div class="flex flex-col">
<span class="text-[10px] uppercase text-slate-400 font-bold tracking-wider">Default Model</span>
<span class="text-sm font-medium text-slate-700 dark:text-slate-300">claude-3-opus</span>
</div>
<button class="w-8 h-8 rounded-lg flex items-center justify-center text-slate-400 hover:text-primary hover:bg-primary/10 transition-colors">
<span class="material-icons-round text-lg">settings</span>
</button>
</div>
</div>
</div>
<!-- Ollama Card (Offline/Error) -->
<div class="group relative bg-white dark:bg-surface-dark rounded-xl border border-slate-200 dark:border-slate-800 hover:border-rose-500 dark:hover:border-rose-500 transition-all duration-300 shadow-sm hover:shadow-lg hover:shadow-rose-500/5 overflow-hidden">
<div class="absolute top-0 left-0 w-full h-1 bg-rose-500"></div>
<div class="p-6">
<div class="flex justify-between items-start mb-4">
<div class="w-12 h-12 rounded-lg bg-white dark:bg-slate-800 p-2 flex items-center justify-center shadow-inner border border-slate-100 dark:border-slate-700">
<span class="material-icons-round text-3xl text-slate-700 dark:text-slate-200">dns</span>
</div>
<div class="flex items-center gap-2">
<div class="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-rose-500/10 border border-rose-500/20">
<span class="w-1.5 h-1.5 rounded-full bg-rose-500 animate-pulse"></span>
<span class="text-xs font-semibold text-rose-500">Offline</span>
</div>
</div>
</div>
<h3 class="text-xl font-bold text-slate-900 dark:text-white mb-1">Ollama (Local)</h3>
<p class="text-sm text-slate-500 dark:text-slate-400 mb-6">Local Llama 3, Mistral</p>
<div class="flex items-center justify-between border-t border-slate-100 dark:border-slate-800 pt-4 mt-auto">
<div class="flex flex-col">
<span class="text-[10px] uppercase text-slate-400 font-bold tracking-wider">Endpoint</span>
<span class="text-sm font-medium text-rose-400 font-mono text-xs mt-0.5">http://localhost:11434</span>
</div>
<button class="w-8 h-8 rounded-lg flex items-center justify-center text-slate-400 hover:text-rose-500 hover:bg-rose-500/10 transition-colors">
<span class="material-icons-round text-lg">refresh</span>
</button>
</div>
</div>
</div>
<!-- Custom vLLM (Inactive) -->
<div class="group relative bg-white dark:bg-surface-dark rounded-xl border border-slate-200 dark:border-slate-800 hover:border-slate-400 transition-all duration-300 shadow-sm hover:shadow-lg overflow-hidden opacity-80 hover:opacity-100">
<div class="absolute top-0 left-0 w-full h-1 bg-slate-500"></div>
<div class="p-6">
<div class="flex justify-between items-start mb-4">
<div class="w-12 h-12 rounded-lg bg-white dark:bg-slate-800 p-2 flex items-center justify-center shadow-inner border border-slate-100 dark:border-slate-700">
<span class="material-icons-round text-3xl text-slate-700 dark:text-slate-200">storage</span>
</div>
<div class="flex items-center gap-2">
<div class="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-slate-500/10 border border-slate-500/20">
<span class="w-1.5 h-1.5 rounded-full bg-slate-500"></span>
<span class="text-xs font-semibold text-slate-500">Inactive</span>
</div>
</div>
</div>
<h3 class="text-xl font-bold text-slate-900 dark:text-white mb-1">Custom vLLM</h3>
<p class="text-sm text-slate-500 dark:text-slate-400 mb-6">High throughput serving</p>
<div class="flex items-center justify-between border-t border-slate-100 dark:border-slate-800 pt-4 mt-auto">
<div class="flex flex-col">
<span class="text-[10px] uppercase text-slate-400 font-bold tracking-wider">Endpoint</span>
<span class="text-sm font-medium text-slate-500 dark:text-slate-500 italic">Not Configured</span>
</div>
<button class="w-8 h-8 rounded-lg flex items-center justify-center text-slate-400 hover:text-primary hover:bg-primary/10 transition-colors">
<span class="material-icons-round text-lg">edit</span>
</button>
</div>
</div>
</div>
<!-- Add New Placeholder -->
<button class="group flex flex-col items-center justify-center bg-transparent rounded-xl border-2 border-dashed border-slate-300 dark:border-slate-700 hover:border-primary dark:hover:border-primary hover:bg-primary/5 transition-all duration-300 h-full min-h-[220px]">
<div class="w-16 h-16 rounded-full bg-slate-100 dark:bg-slate-800 flex items-center justify-center mb-4 group-hover:bg-primary group-hover:text-white transition-colors text-slate-400">
<span class="material-icons-round text-3xl">add</span>
</div>
<span class="text-lg font-bold text-slate-700 dark:text-slate-300 group-hover:text-primary transition-colors">Add New Provider</span>
<span class="text-sm text-slate-500 mt-1">Configure Hugging Face, Cohere, etc.</span>
</button>
</div>
</main>
<!-- Slide-over / Modal (Positioned absolutely for demo purposes to simulate open state over content) -->
<!-- In a real app, this would be toggled via JS and have a backdrop -->
<div class="fixed inset-0 z-50 flex justify-end pointer-events-none">
<!-- Backdrop (Simulated invisible for now to not block view, or semi-transparent) -->
<div class="absolute inset-0 bg-black/40 backdrop-blur-sm pointer-events-auto"></div>
<!-- Panel -->
<div class="relative w-full max-w-md bg-white dark:bg-surface-darker h-full shadow-2xl border-l border-slate-200 dark:border-slate-800 flex flex-col pointer-events-auto transform transition-transform duration-300 ease-in-out translate-x-0">
<!-- Panel Header -->
<div class="flex items-center justify-between px-6 py-5 border-b border-slate-200 dark:border-slate-800">
<div>
<h2 class="text-xl font-bold text-slate-900 dark:text-white">Configure OpenAI</h2>
<p class="text-xs text-slate-500 dark:text-slate-400 mt-1">Update credentials and connection settings</p>
</div>
<button class="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 transition-colors">
<span class="material-icons-round">close</span>
</button>
</div>
<!-- Panel Content -->
<div class="flex-1 overflow-y-auto px-6 py-6 space-y-6">
<!-- Logo & Name Display -->
<div class="flex items-center gap-4 p-4 rounded-lg bg-background-light dark:bg-background-dark border border-slate-200 dark:border-slate-800">
<div class="w-10 h-10 rounded bg-white dark:bg-slate-800 flex items-center justify-center border border-slate-200 dark:border-slate-700">
<svg class="w-6 h-6 text-slate-900 dark:text-white" fill="currentColor" viewbox="0 0 24 24"><path d="M22.2819 9.8211a5.9847 5.9847 0 0 0-.5157-4.9108 6.0462 6.0462 0 0 0-6.5098-2.9A6.0651 6.0651 0 0 0 4.9807 4.1818a5.9847 5.9847 0 0 0-3.9977 2.9 6.0462 6.0462 0 0 0 .7427 7.0966 5.98 5.98 0 0 0 .511 4.9107 6.0462 6.0462 0 0 0 6.5146 2.9001A5.9847 5.9847 0 0 0 13.2599 24a6.0557 6.0557 0 0 0 5.7718-4.2058 5.9894 5.9894 0 0 0 3.9977-2.9001 6.0557 6.0557 0 0 0-.7475-7.0729zm-9.022 12.6081a4.4755 4.4755 0 0 1-2.8764-1.0408l.1419-.0843 3.5366-1.9718a3.1335 3.1335 0 0 0 1.5528 2.0837l.0136.0088-.0529.044a4.522 4.522 0 0 1-2.3156.9604zm-7.007-1.6343a4.484 4.484 0 0 1-1.0069-2.9197l.1419.0833 3.5366 1.9718a3.14 3.14 0 0 0-.0908 2.5925l-.0148.0061-.0612-.0292a4.5364 4.5364 0 0 1-2.5048-1.7048zm-.1278-7.2343a4.5126 4.5126 0 0 1 1.8741-2.438l.1432-.0797 3.5366 1.9732a3.14 3.14 0 0 0-1.6428 1.996l-.0148-.0072-.0612-.0318a4.538 4.538 0 0 1-3.8351-1.4125zm7.1328-5.3262a4.498 4.498 0 0 1 2.8787 1.0372l-.1419.0827-3.5366 1.9732a3.1398 3.1398 0 0 0-1.5542-2.0864l-.0136-.0083.0529-.044a4.526 4.526 0 0 1 2.3147-.9544zm7.0049 1.6366a4.509 4.509 0 0 1 1.009 2.9179l-.1419-.0848-3.5366-1.9718a3.14 3.14 0 0 0 .0908-2.5898l.0148-.0066.0612.0298a4.5397 4.5397 0 0 1 2.5027 1.7053zm.1278 7.2344a4.5222 4.5222 0 0 1-1.8741 2.438l-.1432.0796-3.5366-1.9731a3.1335 3.1335 0 0 0 1.6428-1.9961l.0148.0072.0612.0318a4.5413 4.5413 0 0 1 3.8351 1.4126zM12 14.1563a2.1563 2.1563 0 1 1 2.1563-2.1563A2.1563 2.1563 0 0 1 12 14.1563z"></path></svg>
</div>
<div>
<h3 class="font-bold text-slate-900 dark:text-white">OpenAI</h3>
<p class="text-xs text-emerald-500 font-medium">● Connected</p>
</div>
</div>
<!-- API Key Input -->
<div class="space-y-2">
<label class="block text-sm font-medium text-slate-700 dark:text-slate-300">API Key</label>
<div class="relative group">
<input class="w-full bg-white dark:bg-background-dark border border-slate-300 dark:border-slate-700 rounded-lg px-4 py-2.5 text-slate-900 dark:text-white focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition-all pr-10 font-mono text-sm" placeholder="sk-..." type="password" value="sk-proj-........................"/>
<button class="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200">
<span class="material-icons-round text-lg">visibility</span>
</button>
</div>
<p class="text-xs text-slate-500">Your key is encrypted locally.</p>
</div>
<!-- Base URL Input (Optional) -->
<div class="space-y-2">
<label class="block text-sm font-medium text-slate-700 dark:text-slate-300">Base URL <span class="text-slate-500 font-normal">(Optional)</span></label>
<input class="w-full bg-white dark:bg-background-dark border border-slate-300 dark:border-slate-700 rounded-lg px-4 py-2.5 text-slate-900 dark:text-white focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition-all font-mono text-sm" type="text" value="https://api.openai.com/v1"/>
</div>
<!-- Default Model Selection -->
<div class="space-y-2">
<label class="block text-sm font-medium text-slate-700 dark:text-slate-300">Default Model</label>
<div class="relative">
<select class="w-full appearance-none bg-white dark:bg-background-dark border border-slate-300 dark:border-slate-700 rounded-lg px-4 py-2.5 text-slate-900 dark:text-white focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition-all pr-10">
<option selected="" value="gpt-4-turbo">gpt-4-turbo</option>
<option value="gpt-4">gpt-4</option>
<option value="gpt-3.5-turbo">gpt-3.5-turbo</option>
</select>
<div class="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none text-slate-500">
<span class="material-icons-round">expand_more</span>
</div>
</div>
</div>
<!-- Org ID (Advanced) -->
<div class="pt-2">
<button class="flex items-center gap-2 text-sm text-primary font-medium hover:text-blue-400 transition-colors">
<span class="material-icons-round text-base">tune</span>
                        Show Advanced Settings
                    </button>
</div>
</div>
<!-- Panel Footer -->
<div class="px-6 py-5 border-t border-slate-200 dark:border-slate-800 bg-background-light dark:bg-surface-dark flex flex-col gap-3">
<button class="w-full flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg border border-primary/30 text-primary hover:bg-primary/5 transition-all text-sm font-bold">
<span class="material-icons-round text-lg">wifi_tethering</span>
                    Test Connection
                </button>
<div class="grid grid-cols-2 gap-3">
<button class="w-full px-4 py-2.5 rounded-lg border border-slate-300 dark:border-slate-600 text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700 transition-all text-sm font-bold">
                        Cancel
                    </button>
<button class="w-full px-4 py-2.5 rounded-lg bg-primary text-white hover:bg-blue-600 shadow-lg shadow-primary/20 transition-all text-sm font-bold">
                        Save Changes
                    </button>
</div>
</div>
</div>
</div>
</body></html>
