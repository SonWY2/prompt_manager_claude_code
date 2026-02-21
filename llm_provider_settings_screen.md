<!DOCTYPE html>

<html class="dark" lang="en"><head>
<meta charset="utf-8"/>
<meta content="width=device-width, initial-scale=1.0" name="viewport"/>
<title>LLM Provider Settings - Prompt Manager</title>
<!-- Fonts -->
<link href="https://fonts.googleapis.com" rel="preconnect"/>
<link crossorigin="" href="https://fonts.gstatic.com" rel="preconnect"/>
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&amp;display=swap" rel="stylesheet"/>
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500&amp;display=swap" rel="stylesheet"/>
<!-- Icons -->
<link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet"/>
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&amp;display=swap" rel="stylesheet"/>
<!-- Tailwind Config -->
<script src="https://cdn.tailwindcss.com?plugins=forms,container-queries"></script>
<script>
        tailwind.config = {
            darkMode: "class",
            theme: {
                extend: {
                    colors: {
                        "primary": "#2b8cee",
                        "primary-hover": "#1a7bdc",
                        "background-light": "#f6f7f8",
                        "background-dark": "#101922",
                        "surface-dark": "#1a2632",
                        "surface-hover": "#243242",
                        "input-bg": "#0d141c",
                        "success": "#10b981",
                        "error": "#ef4444",
                    },
                    fontFamily: {
                        "display": ["Space Grotesk", "sans-serif"],
                        "mono": ["JetBrains Mono", "monospace"],
                    },
                    borderRadius: {
                        "DEFAULT": "0.25rem", 
                        "lg": "0.5rem", 
                        "xl": "0.75rem", 
                        "full": "9999px"
                    },
                },
            },
        }
    </script>
<style>
        /* Custom scrollbar for webkit browsers */
        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }
        ::-webkit-scrollbar-track {
            background: #101922; 
        }
        ::-webkit-scrollbar-thumb {
            background: #243242; 
            border-radius: 4px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: #2b8cee; 
        }
        
        .glass-panel {
            background: rgba(26, 38, 50, 0.7);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(43, 140, 238, 0.1);
        }
    </style>
</head>
<body class="bg-background-light dark:bg-background-dark text-slate-800 dark:text-slate-200 font-display h-screen flex overflow-hidden selection:bg-primary/30 selection:text-primary">
<!-- Sidebar -->
<aside class="w-80 flex-shrink-0 border-r border-slate-200 dark:border-slate-800 bg-white dark:bg-surface-dark flex flex-col h-full z-20">
<!-- App Header -->
<div class="h-16 flex items-center px-6 border-b border-slate-200 dark:border-slate-800">
<div class="flex items-center gap-3">
<div class="w-8 h-8 rounded-lg bg-primary/20 flex items-center justify-center text-primary">
<span class="material-icons text-xl">terminal</span>
</div>
<h1 class="font-bold text-lg tracking-tight">Prompt Manager</h1>
</div>
</div>
<!-- Search & Add -->
<div class="p-4 space-y-4">
<div class="relative group">
<span class="absolute left-3 top-2.5 text-slate-400 group-focus-within:text-primary transition-colors">
<span class="material-icons text-lg">search</span>
</span>
<input class="w-full bg-slate-100 dark:bg-input-bg border-none rounded-lg py-2 pl-10 pr-4 text-sm focus:ring-2 focus:ring-primary/50 placeholder-slate-500 transition-all" placeholder="Filter providers..." type="text"/>
</div>
<button class="w-full flex items-center justify-center gap-2 py-2 px-4 bg-primary/10 hover:bg-primary/20 text-primary rounded-lg transition-all font-medium border border-primary/20 hover:border-primary/50">
<span class="material-icons text-lg">add</span>
<span>New Provider</span>
</button>
</div>
<!-- Provider List -->
<div class="flex-1 overflow-y-auto px-3 space-y-1 pb-4">
<div class="px-3 py-2 text-xs font-bold text-slate-500 uppercase tracking-wider">Configured</div>
<!-- Item 1: Active -->
<button class="w-full text-left p-3 rounded-lg bg-primary/10 border border-primary/30 relative group transition-all">
<div class="flex justify-between items-start mb-1">
<span class="font-semibold text-primary">OpenAI Production</span>
<span class="flex h-2.5 w-2.5 relative">
<span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-success opacity-75"></span>
<span class="relative inline-flex rounded-full h-2.5 w-2.5 bg-success"></span>
</span>
</div>
<div class="flex items-center gap-2 text-xs text-slate-400">
<span class="material-icons text-[14px]">dns</span>
<span>gpt-4-turbo</span>
</div>
</button>
<!-- Item 2 -->
<button class="w-full text-left p-3 rounded-lg hover:bg-surface-hover border border-transparent hover:border-slate-700 transition-all group">
<div class="flex justify-between items-start mb-1">
<span class="font-medium text-slate-300 group-hover:text-white">Local Ollama</span>
<span class="flex h-2.5 w-2.5 relative items-center justify-center">
<span class="relative inline-flex rounded-full h-2 w-2 bg-success"></span>
</span>
</div>
<div class="flex items-center gap-2 text-xs text-slate-500 group-hover:text-slate-400">
<span class="material-icons text-[14px]">computer</span>
<span>llama-3-8b</span>
</div>
</button>
<!-- Item 3: Offline -->
<button class="w-full text-left p-3 rounded-lg hover:bg-surface-hover border border-transparent hover:border-slate-700 transition-all group">
<div class="flex justify-between items-start mb-1">
<span class="font-medium text-slate-300 group-hover:text-white">vLLM Server</span>
<span class="flex h-2.5 w-2.5 relative items-center justify-center">
<span class="relative inline-flex rounded-full h-2 w-2 bg-slate-600"></span>
</span>
</div>
<div class="flex items-center gap-2 text-xs text-slate-500 group-hover:text-slate-400">
<span class="material-icons text-[14px]">cloud_off</span>
<span>mistral-7b</span>
</div>
</button>
<!-- Item 4 -->
<button class="w-full text-left p-3 rounded-lg hover:bg-surface-hover border border-transparent hover:border-slate-700 transition-all group">
<div class="flex justify-between items-start mb-1">
<span class="font-medium text-slate-300 group-hover:text-white">Anthropic Claude</span>
<span class="flex h-2.5 w-2.5 relative items-center justify-center">
<span class="relative inline-flex rounded-full h-2 w-2 bg-success"></span>
</span>
</div>
<div class="flex items-center gap-2 text-xs text-slate-500 group-hover:text-slate-400">
<span class="material-icons text-[14px]">auto_awesome</span>
<span>claude-3-opus</span>
</div>
</button>
</div>
<!-- Sidebar Footer -->
<div class="p-4 border-t border-slate-200 dark:border-slate-800">
<div class="flex items-center gap-3 text-sm text-slate-500">
<div class="w-8 h-8 rounded-full bg-slate-200 dark:bg-slate-700 overflow-hidden relative">
<img alt="User Avatar" class="w-full h-full object-cover" data-alt="Profile picture of the logged in user" src="https://lh3.googleusercontent.com/aida-public/AB6AXuAH0RXV4kvbkgFMfYeNyUPnMgK13CQwbIXhoYi8PTovSVRVh1ZbdR5T7kvvQDflOvLXejWCJCbiblI9lhl2SlAkeG3BTS54-0B2qbiqnSnvKyzZRN6EdF0HbPt42QkZHbS25ZDta4el0DkAuOuTeZvdAgiFDcwv3WBzCFZd22K5hNf5V2lNBWyI-0_IyZcRutGye9u8-6PkzpZbLtHxcYjgPjw3b07ZwoNwNH2CDi0ORE3J-63slHPFZkUa21TJSk6et65Gl9tP5fI"/>
</div>
<div class="flex-1">
<p class="font-medium text-slate-700 dark:text-slate-300">Jane Engineer</p>
<p class="text-xs">Pro License</p>
</div>
<button class="text-slate-400 hover:text-primary transition-colors">
<span class="material-icons">settings</span>
</button>
</div>
</div>
</aside>
<!-- Main Content -->
<main class="flex-1 flex flex-col h-full relative overflow-hidden">
<!-- Background Pattern -->
<div class="absolute inset-0 z-0 opacity-20 pointer-events-none" style="background-image: radial-gradient(#2b8cee 1px, transparent 1px); background-size: 32px 32px;"></div>
<!-- Top Bar -->
<header class="h-16 flex items-center justify-between px-8 border-b border-slate-200 dark:border-slate-800 bg-white/50 dark:bg-background-dark/80 backdrop-blur-sm z-10">
<div class="flex items-center gap-4">
<span class="px-2 py-1 rounded bg-green-500/10 text-green-500 border border-green-500/20 text-xs font-mono font-bold uppercase tracking-wider">Active</span>
<h2 class="text-xl font-bold text-slate-800 dark:text-white">OpenAI Production</h2>
</div>
<div class="flex gap-3">
<button class="px-4 py-2 rounded-lg text-sm font-medium text-slate-500 hover:text-error hover:bg-error/10 transition-all flex items-center gap-2">
<span class="material-icons text-lg">delete</span>
                    Delete
                </button>
<button class="px-6 py-2 rounded-lg text-sm font-bold bg-primary hover:bg-primary-hover text-white shadow-lg shadow-primary/20 transition-all flex items-center gap-2">
<span class="material-icons text-lg">save</span>
                    Save Changes
                </button>
</div>
</header>
<!-- Scrollable Content Area -->
<div class="flex-1 overflow-y-auto p-8 z-10 relative">
<div class="max-w-4xl mx-auto space-y-8">
<!-- General Settings Card -->
<section class="bg-white dark:bg-surface-dark border border-slate-200 dark:border-slate-800 rounded-xl p-6 shadow-sm">
<div class="flex items-center gap-3 mb-6 border-b border-slate-200 dark:border-slate-700 pb-4">
<span class="material-icons text-primary text-2xl">tune</span>
<div>
<h3 class="text-lg font-bold">General Configuration</h3>
<p class="text-sm text-slate-500">Basic details for the provider connection.</p>
</div>
</div>
<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
<!-- Provider Name -->
<div class="space-y-2">
<label class="text-sm font-medium text-slate-400">Provider Alias</label>
<input class="w-full bg-slate-50 dark:bg-input-bg border border-slate-300 dark:border-slate-700 rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-primary focus:border-primary text-slate-800 dark:text-white transition-all outline-none" type="text" value="OpenAI Production"/>
</div>
<!-- Provider Type (Disabled/Fixed) -->
<div class="space-y-2 opacity-70">
<label class="text-sm font-medium text-slate-400">Provider Type</label>
<div class="w-full bg-slate-100 dark:bg-surface-hover border border-slate-300 dark:border-slate-700 rounded-lg px-4 py-2.5 text-slate-500 cursor-not-allowed flex items-center justify-between">
<span>OpenAI Compatible</span>
<span class="material-icons text-sm">lock</span>
</div>
</div>
</div>
</section>
<!-- Connection Settings Card -->
<section class="bg-white dark:bg-surface-dark border border-slate-200 dark:border-slate-800 rounded-xl p-6 shadow-sm">
<div class="flex items-center gap-3 mb-6 border-b border-slate-200 dark:border-slate-700 pb-4">
<span class="material-icons text-primary text-2xl">link</span>
<div>
<h3 class="text-lg font-bold">API Connection</h3>
<p class="text-sm text-slate-500">Endpoints and authentication credentials.</p>
</div>
</div>
<div class="space-y-6">
<!-- Base URL -->
<div class="space-y-2">
<label class="text-sm font-medium text-slate-400 flex justify-between">
<span>API Base URL</span>
<span class="text-xs text-primary cursor-pointer hover:underline">Reset to Default</span>
</label>
<div class="relative">
<span class="absolute left-4 top-3 text-slate-500 font-mono text-sm">https://</span>
<input class="font-mono text-sm w-full bg-slate-50 dark:bg-input-bg border border-slate-300 dark:border-slate-700 rounded-lg pl-20 pr-4 py-2.5 focus:ring-2 focus:ring-primary focus:border-primary text-slate-800 dark:text-white transition-all outline-none" type="text" value="api.openai.com/v1"/>
</div>
</div>
<!-- API Key -->
<div class="space-y-2">
<label class="text-sm font-medium text-slate-400">API Key</label>
<div class="relative group">
<span class="absolute left-4 top-2.5 text-slate-500">
<span class="material-icons text-lg">vpn_key</span>
</span>
<input class="font-mono text-sm w-full bg-slate-50 dark:bg-input-bg border border-slate-300 dark:border-slate-700 rounded-lg pl-12 pr-12 py-2.5 focus:ring-2 focus:ring-primary focus:border-primary text-slate-800 dark:text-white transition-all outline-none tracking-widest" type="password" value="sk-proj-1234567890abcdef1234567890abcdef"/>
<button class="absolute right-3 top-2.5 text-slate-500 hover:text-primary transition-colors focus:outline-none">
<span class="material-icons text-lg">visibility_off</span>
</button>
</div>
<p class="text-xs text-slate-500">Your key is stored locally using OS-level encryption.</p>
</div>
</div>
</section>
<!-- Model Configuration Card -->
<section class="bg-white dark:bg-surface-dark border border-slate-200 dark:border-slate-800 rounded-xl p-6 shadow-sm">
<div class="flex items-center gap-3 mb-6 border-b border-slate-200 dark:border-slate-700 pb-4">
<span class="material-icons text-primary text-2xl">model_training</span>
<div>
<h3 class="text-lg font-bold">Model Parameters</h3>
<p class="text-sm text-slate-500">Default model selection and context limits.</p>
</div>
</div>
<div class="grid grid-cols-1 md:grid-cols-3 gap-6">
<!-- Model Selection -->
<div class="space-y-2 md:col-span-2">
<label class="text-sm font-medium text-slate-400">Default Model</label>
<div class="relative">
<select class="w-full bg-slate-50 dark:bg-input-bg border border-slate-300 dark:border-slate-700 rounded-lg pl-4 pr-10 py-2.5 focus:ring-2 focus:ring-primary focus:border-primary text-slate-800 dark:text-white transition-all outline-none appearance-none cursor-pointer">
<option value="gpt-4-turbo">gpt-4-turbo</option>
<option value="gpt-4">gpt-4</option>
<option value="gpt-3.5-turbo">gpt-3.5-turbo</option>
</select>
<span class="absolute right-3 top-3 pointer-events-none text-slate-500">
<span class="material-icons text-lg">expand_more</span>
</span>
</div>
</div>
<!-- Context Window -->
<div class="space-y-2">
<label class="text-sm font-medium text-slate-400">Context Window</label>
<div class="relative">
<input class="w-full bg-slate-50 dark:bg-input-bg border border-slate-300 dark:border-slate-700 rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-primary focus:border-primary text-slate-800 dark:text-white transition-all outline-none font-mono text-sm" type="number" value="128000"/>
<span class="absolute right-3 top-2.5 text-xs text-slate-500 pt-1">tok</span>
</div>
</div>
</div>
</section>
<!-- Test Connection Area -->
<section class="border border-primary/20 bg-primary/5 rounded-xl p-6 flex items-center justify-between gap-6">
<div class="flex items-center gap-4">
<div class="h-12 w-12 rounded-full bg-primary/10 flex items-center justify-center text-primary flex-shrink-0">
<span class="material-icons">network_check</span>
</div>
<div>
<h4 class="font-bold text-slate-800 dark:text-white">Connection Status</h4>
<div class="flex items-center gap-2 mt-1">
<span class="w-2 h-2 rounded-full bg-green-500"></span>
<p class="text-sm text-green-500 font-medium">Connected (Latency: 142ms)</p>
</div>
</div>
</div>
<button class="px-5 py-2.5 rounded-lg border border-primary text-primary hover:bg-primary hover:text-white transition-all font-medium flex items-center gap-2 group">
<span class="material-icons group-hover:animate-spin">refresh</span>
                        Test Connection
                    </button>
</section>
<div class="h-8"></div> <!-- Spacer -->
</div>
</div>
</main>
</body></html>
