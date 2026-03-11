---
theme: seriph
transition: slide-up
title: Personal Assistant CLI
class: text-center
info: |
  ## Personal Assistant CLI - Team Project Presentation
  CodeFlow Team - Python CLI Application
---

# Personal Assistant CLI

<div class="text-xl opacity-80 mt-4">
  Team Project Presentation
</div>

<div class="text-sm opacity-60 mt-12">
  Python CLI Application • CodeFlow Team
</div>

---
layout: center
class: text-center
transition: view-transition
---

<div class="text-6xl mb-8">👥</div>

# Учасники команди

<div class="grid grid-cols-2 gap-8 mt-12 max-w-4xl mx-auto">
  <div class="bg-gradient-to-br from-orange-500 to-orange-600 rounded-2xl p-6 text-left">
    <div class="text-3xl mb-2 view-transition-devicon">🧙‍♂️</div>
    <div class="font-bold text-lg view-transition-devname">Volodymyr Palamar</div>
    <div class="text-sm opacity-90 view-transition-devrole">Team Lead</div>
  </div>
  <div class="bg-gradient-to-br from-orange-500 to-orange-600 rounded-2xl p-6 text-left">
    <div class="text-3xl mb-2">👩‍💼</div>
    <div class="font-bold text-lg">Liudmyla Slipko</div>
    <div class="text-sm opacity-90">Scrum Master</div>
  </div>
  <div class="bg-gradient-to-br from-orange-500 to-orange-600 rounded-2xl p-6 text-left">
    <div class="text-3xl mb-2">👩‍💻</div>
    <div class="font-bold text-lg">Aurika</div>
    <div class="text-sm opacity-90">Developer</div>
  </div>
  <div class="bg-gradient-to-br from-orange-500 to-orange-600 rounded-2xl p-6 text-left">
    <div class="text-3xl mb-2">👨‍💻</div>
    <div class="font-bold text-lg">Daniil Kukhar</div>
    <div class="text-sm opacity-90">Developer</div>
  </div>
</div>

---
layout: two-cols
transition: slide-left
---

::left::

<AboutMemberCard
  name="Volodymyr Palamar"
  role="Team Lead"
  emoji="🧙‍♂️"
/>

::right::

<DetailsMemberCard
  :items="[
    { icon: '🎯', text: 'Architecture design' },
    { icon: '🏗️', text: 'CLI structure' },
    { icon: '🔍', text: 'Code review' },
    { icon: '🔧', text: 'Feature integration' }
  ]"
/>

---
layout: two-cols
transition: slide-left
---

::left::

<AboutMemberCard
  name="Liudmyla Slipko"
  role="Scrum Master"
  emoji="👩‍💼"
/>


::right::

<DetailsMemberCard
  :items="[
    { icon: '🤝', text: 'Team coordination' },
    { icon: '📋', text: 'Sprint planning' },
    { icon: '✅', text: 'Task management' },
    { icon: '💬', text: 'Communication' }
  ]"
/>

---
layout: two-cols
transition: slide-left
---

::left::

<AboutMemberCard
  name="Aurika"
  role="Developer"
  emoji="👩‍💻"
/>

::right::

<DetailsMemberCard
  :items="[
    { icon: '💻', text: 'CLI command development' },
    { icon: '⚡', text: 'Feature implementation' },
    { icon: '🧪', text: 'Testing' },
    { icon: '🐛', text: 'Bug fixing' }
  ]"
/>

---
layout: two-cols

---

::left::

<AboutMemberCard
  name="Daniil Kukhar"
  role="Developer"
  emoji="👨‍💻"
/>

::right::

<DetailsMemberCard
  :items="[
    { icon: '⚙️', text: 'Command logic' },
    { icon: '🎮', text: 'CLI interaction' },
    { icon: '🔎', text: 'Debugging' },
    { icon: '🚀', text: 'Project improvements' }
  ]"
/>

---
layout: center
---

<div class="text-6xl mb-8">📝</div>

# Опис проєкту

<div class="max-w-2xl mx-auto space-y-4 mt-8">
  <div class="flex items-center gap-4 text-xl">
    <span class="text-orange-500 text-2xl">🎯</span>
    <span>Personal Assistant CLI</span>
  </div>
  <div class="flex items-center gap-4 text-xl">
    <span class="text-orange-500 text-2xl">📇</span>
    <span>Керування контактами та нотатками</span>
  </div>
  <div class="flex items-center gap-4 text-xl">
    <span class="text-orange-500 text-2xl">🎨</span>
    <span>CLI інтерфейс з Rich UI</span>
  </div>
  <div class="flex items-center gap-4 text-xl">
    <span class="text-orange-500 text-2xl">⚡</span>
    <span>Інтерактивні команди</span>
  </div>
  <div class="flex items-center gap-4 text-xl">
    <span class="text-orange-500 text-2xl">💡</span>
    <span>Підказки при помилках команд</span>
  </div>
</div>

---
layout: center
---

<div class="text-6xl mb-8">⚖️</div>

# Проблеми та рішення

<div class="grid grid-cols-2 gap-8 max-w-5xl mx-auto mt-8">
  <div class="space-y-6">
    <div class="text-2xl font-bold text-red-400 mb-4">❌ Проблеми</div>
    <div class="flex items-center gap-3 text-lg">
      <span class="text-red-400">🚫</span>
      <span>UX у CLI</span>
    </div>
    <div class="flex items-center gap-3 text-lg">
      <span class="text-red-400">🚫</span>
      <span>Структура команд</span>
    </div>
    <div class="flex items-center gap-3 text-lg">
      <span class="text-red-400">🚫</span>
      <span>Обробка помилок</span>
    </div>
    <div class="flex items-center gap-3 text-lg">
      <span class="text-red-400">🚫</span>
      <span>Організація архітектури</span>
    </div>
  </div>

  <div class="space-y-6">
    <div class="text-2xl font-bold text-green-400 mb-4">✅ Рішення</div>
    <div class="flex items-center gap-3 text-lg">
      <span class="text-green-400">✅</span>
      <span>Rich UI бібліотека</span>
    </div>
    <div class="flex items-center gap-3 text-lg">
      <span class="text-green-400">✅</span>
      <span>Система команд</span>
    </div>
    <div class="flex items-center gap-3 text-lg">
      <span class="text-green-400">✅</span>
      <span>Command suggestions</span>
    </div>
    <div class="flex items-center gap-3 text-lg">
      <span class="text-green-400">✅</span>
      <span>Typed Python code</span>
    </div>
  </div>
</div>

---
layout: center
---

<div class="text-6xl mb-8">🛠️</div>

# Технології

<div class="grid grid-cols-3 gap-6 max-w-5xl mx-auto mt-8">
  <div class="bg-gradient-to-br from-blue-500/10 to-blue-600/10 border border-blue-500/20 rounded-2xl p-6">
    <div class="text-3xl mb-4">🐍</div>
    <div class="text-xl font-bold mb-2">Back-end</div>
    <div class="space-y-2 text-base opacity-90">
      <div>• Python</div>
      <div>• Rich</div>
      <div>• CLI Architecture</div>
    </div>
  </div>

  <div class="bg-gradient-to-br from-purple-500/10 to-purple-600/10 border border-purple-500/20 rounded-2xl p-6">
    <div class="text-3xl mb-4">⚡</div>
    <div class="text-xl font-bold mb-2">Features</div>
    <div class="space-y-2 text-base opacity-90">
      <div>• Command system</div>
      <div>• Tables</div>
      <div>• Interactive input</div>
      <div>• Command suggestions</div>
    </div>
  </div>

  <div class="bg-gradient-to-br from-green-500/10 to-green-600/10 border border-green-500/20 rounded-2xl p-6">
    <div class="text-3xl mb-4">🔧</div>
    <div class="text-xl font-bold mb-2">Utilities</div>
    <div class="space-y-2 text-base opacity-90">
      <div>• VSCode</div>
      <div>• Git</div>
      <div>• GitHub</div>
    </div>
  </div>
</div>

---
layout: center
---

<div class="text-6xl mb-8">🎬</div>

# Демонстрація

<div class="bg-gray-900/50 border border-gray-700 rounded-2xl p-12 max-w-3xl mx-auto mt-8">
  <div class="text-4xl mb-4">💻</div>
  <div class="text-2xl font-bold text-orange-500 mb-2">CLI Demo</div>
  <div class="text-lg opacity-80">
    Запуск та робота команд
  </div>
  <div class="mt-6 text-sm opacity-60">
    <span class="bg-gray-800 px-3 py-1 rounded">$ python main.py</span>
  </div>
</div>

---
layout: center
---

<div class="text-6xl mb-8">🎉</div>

# Висновок

<div class="max-w-2xl mx-auto space-y-4 mt-8">
  <div class="flex items-center gap-4 text-xl">
    <span class="text-orange-500 text-2xl">✨</span>
    <span>Створено CLI оболонку</span>
  </div>
  <div class="flex items-center gap-4 text-xl">
    <span class="text-orange-500 text-2xl">🎨</span>
    <span>Зручний інтерфейс з Rich</span>
  </div>
  <div class="flex items-center gap-4 text-xl">
    <span class="text-orange-500 text-2xl">🏗️</span>
    <span>Основа для масштабування</span>
  </div>
  <div class="flex items-center gap-4 text-xl">
    <span class="text-orange-500 text-2xl">🚀</span>
    <span>Наступний крок — реалізація бізнес-логіки</span>
  </div>
</div>

<div class="mt-16 text-3xl font-bold text-orange-500">
  Дякуємо за увагу!
</div>

<div class="mt-4 text-sm opacity-60">
  CodeFlow Team • 2024
</div>
