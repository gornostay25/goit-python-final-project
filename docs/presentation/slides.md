---
theme: seriph
transition: slide-up
title: Personal Assistant CLI
class: text-center
info: |
  ## Personal Assistant CLI - Team Project Presentation
  Горностайчики Team 🦄 - Python CLI Application
---

# Personal Assistant CLI

<div class="text-xl opacity-80 mt-4">
  "Горностайчики" Team Project Presentation
</div>

<div class="text-sm opacity-60 mt-12">
  Neoversity Python Course • 2026
</div>

<!--
Всім привіт ми команда горностайчики і сьогодні будемо презентувати нащ проєкт Personal Assistant CLI.
-->

---
layout: center
class: text-center
transition: view-transition
---

# 👥 Учасники команди

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

<!--
Наша команда складається з чотирьох учасників: Мене, Людмили, Аурики і Даніїла

Ми об'єднали свої навички щоб зробити кінцевий продукт гарним і функціональним
-->

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

<!--
В мене звати Володимир, я Team Lead нашої команди. Я відповідаю за архітектурний дизайн нашого застосунку, проводив код-рев'ю та допомагав інтегрувати нові функції в основну систему.
-->

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

<!--
Людмили, виконувала роль Scrum Master.
Вона займалася:
- координацією команди
- плануванням спринтів
- управління завданнями
- та забезпеченням відкритого комунікації всередині команди.
-->

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

<!--
Наступний учасник команди - Аурика.

Як розробник, вона відповідала за розробку модуля **контактів**, А також тестування і виправлення багів
-->

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

<!--
І наш останній учасник - Данііл.

Він розробив модуль нотатків і допомагав з тестуванням і виправленням багів
-->

---
layout: center
---

# 📝 Опис проєкту

<div class="max-w-4xl mx-auto space-y-4 mt-8">
  <div class="flex items-center gap-4 text-xl">
    <span class="text-orange-500 text-2xl">🎯</span>
    <span>Personal Assistant CLI</span>
  </div>
  <div class="flex items-center gap-4 text-xl">
    <span class="text-orange-500 text-2xl">📇</span>
    <span>Керування контактами (add, search, edit, delete, birthdays)</span>
  </div>
  <div class="flex items-center gap-4 text-xl">
    <span class="text-orange-500 text-2xl">📝</span>
    <span>Керування нотатками (tags, search, sort, edit, delete)</span>
  </div>
  <div class="flex items-center gap-4 text-xl">
    <span class="text-orange-500 text-2xl">🎨</span>
    <span>Rich UI з таблицями та кольоровим виводом</span>
  </div>
  <div class="flex items-center gap-4 text-xl">
    <span class="text-orange-500 text-2xl">⚡</span>
    <span>Команди з автодоповненням та підказками при помилках</span>
  </div>
  <div class="flex items-center gap-4 text-xl">
    <span class="text-orange-500 text-2xl">💾</span>
    <span>JSON персистентне зберігання (contacts.json, notes.json)</span>
  </div>
</div>

<!--
Тепер перейдемо до самого проєкту. Наш Personal Assistant CLI - це універсальний інструмент для керування контактами та нотатками.

Ми реалізували повний цикл управління **контактами**: додавання, пошук, редагування, видалення та сповіщення про дні народження.

Також ми створили систему **нотаток** з можливістю додавання тегів, пошуку, сортування, редагування та видалення.

Особливістю нашого застосунку є інтерфейс, що використовує таблиці та кольоровий вивід для кращого сприйняття інформації.

Ми впровадили систему автодоповнення та підказок при помилках у командах для підвищення зручності використання.
-->

---
layout: center
---

<div class="text-6xl mb-8">⚖️</div>

# Проблеми та рішення

<!--
Problems we have: Multiline input git conflict
UA phone to E.164 format
UNIT tests CI/CD -->

<div class="grid grid-cols-2 gap-8 max-w-5xl mx-auto mt-8">
  <div class="space-y-6">
    <div class="text-2xl font-bold text-red-400 mb-4">❌ Проблеми</div>
    <div class="flex items-center gap-3 text-lg">
      <span class="text-red-400">🚫</span>
      <span>UX у CLI</span>
    </div>
    <div class="flex items-center gap-3 text-lg">
      <span class="text-red-400">🚫</span>
      <span>Введення команд</span>
    </div>
    <div class="flex items-center gap-3 text-lg">
      <span class="text-red-400">🚫</span>
      <span>Обробка невірних команд</span>
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
      <span>Автодоповнення команд</span>
    </div>
    <div class="flex items-center gap-3 text-lg">
      <span class="text-green-400">✅</span>
      <span>Regex validation for arguments</span>
    </div>
    <div class="flex items-center gap-3 text-lg">
      <span class="text-green-400">✅</span>
      <span>TypedDict + dataclasses</span>
    </div>
  </div>
</div>

<!--
Під час розробки ми стикалися з певними проблемами. Найбільшими викликами були поганий UX у CLI, ускладнений процес введення команд, потреба в кращій обробці невірних команд та потреба у чіткій організації архітектури системи.


Щоб вирішити ці проблеми, ми використали Rich UI бібліотеку для створення зручного інтерфейсу, впровадили систему автодоповнення команд (prompt_toolkit), додали regex validation для перевірки аргументів команд та застосували TypedDict та dataclasses для кращої типізації даних.
-->

---
layout: center
---

# 🛠️ Технології

<div class="grid grid-cols-3 gap-6 max-w-5xl mx-auto mt-8">
  <div class="bg-gradient-to-br from-blue-500/10 to-blue-600/10 border border-blue-500/20 rounded-2xl p-6">
    <div class="text-3xl mb-4">🐍</div>
    <div class="text-xl font-bold mb-2">Back-end</div>
    <div class="space-y-2 text-base opacity-90">
      <div>• Python >=3.10</div>
      <div>• Rich UI Library</div>
      <div>• Prompt Toolkit</div>
      <div>• TypedDict + dataclasses</div>
    </div>
  </div>

  <div class="bg-gradient-to-br from-purple-500/10 to-purple-600/10 border border-purple-500/20 rounded-2xl p-6">
    <div class="text-3xl mb-4">⚡</div>
    <div class="text-xl font-bold mb-2">Features</div>
    <div class="space-y-2 text-base opacity-90">
      <div>• Custom command system</div>
      <div>• Tables with Rich</div>
      <div>• Interactive input with prompt_toolkit</div>
      <div>• Autocompletion and suggestions</div>
    </div>
  </div>

  <div class="bg-gradient-to-br from-green-500/10 to-green-600/10 border border-green-500/20 rounded-2xl p-6">
    <div class="text-3xl mb-4">🔧</div>
    <div class="text-xl font-bold mb-2">Dev Tools</div>
    <div class="space-y-2 text-base opacity-90">
      <div>• pytest</div>
      <div>• Ruff</div>
      <div>• GitHub Actions</div>
      <div>• uv Package Manager</div>
    </div>
  </div>
</div>

<!--
Технології які ми використовували у проекті:
- Python 3.10,
- Rich UI Library та Prompt Toolkit для створення інтерактивного інтерфейсу
- TypedDict та dataclasses для кращої структуризації та типізації даних
- Для тестування ми використали pytest
- Ruff для форматування коду
- GitHub Actions для CI/CD
- uv як менеджер пакетів.
-->

---
layout: image-left
image: https://raw.githubusercontent.com/gornostay25/goit-python-final-project/refs/heads/main/docs/demo.gif
backgroundSize: 90% 80%
---

# 🎬 Демонстрація

<div class="bg-gray-900/50 border border-gray-700 rounded-2xl p-12 max-w-3xl mx-auto mt-8">
  <div class="text-2xl font-bold text-orange-500 mb-2">💻 CLI Demo</div>
  <div class="mt-6 text-sm opacity-60">
    <span class="bg-gray-800 px-3 py-1 rounded">$ uv run python -m app</span>
  </div>
</div>

<!--
Тепер давайте подивимося на наш проєкт у дії
-->

---
layout: center
---

# 🎉 Висновок

<div class="max-w-2xl mx-auto space-y-4 mt-8">
  <div class="flex items-center gap-4 text-xl">
    <span class="text-orange-500 text-2xl">✨</span>
    <span>Створено CLI застосунок зі зручним інтерфейсом</span>
  </div>
  <div class="flex items-center gap-4 text-xl">
    <span class="text-orange-500 text-2xl">🎨</span>
    <span>Попрактикували роботу в команді і Scrum</span>
  </div>
</div>

<div class="mt-16 text-3xl font-bold text-orange-500">
  Дякуємо за увагу!
</div>

<div class="mt-4 text-sm opacity-60">
  Горностайчики Team 🦄 • 2026
</div>

<!--
Підсумовуючи, ми створили CLI-застосунок із зручним інтерфейсом, який дозволяє ефективно керувати контактами та нотатками. Окрім технічних навичок, ми також набули досвіду роботи в команді та практикували Scrum-процеси.
-->
