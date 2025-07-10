2. Set up Tailwind CSS
Make sure you have Tailwind CSS and Alpine.js installed:

You can use npm or yarn to install tailwindcss:

npm install -D tailwindcss tw-animate-css
or, you can also use django-tailwind-cli if you don't want to use node, and follow the manual installation instructions for tw-animate-css here

See alpinejs docs for installation instructions: https://alpinejs.dev/installation

Add the CSS and Alpine.js to your base template <head> tag:

<!-- Tailwind CSS output file -->
<link rel="stylesheet" href="{% static 'css/output.css' %}" />

<!-- Alpine.js tag - directly from CDN (not recommended for production) -->
<script defer src="https://unpkg.com/alpinejs@3.x.x/dist/cdn.min.js"></script>
Run Tailwind to generate your CSS:

npx @tailwindcss/cli -i input.css -o static/css/output.css --watch
3. Add components
List available components:

uvx shadcn_django list

╭───────────────────────────────── Available Components ──────────────────────────────────╮
│                                                                                         │
│  a              accordion  alert      alert_dialog  badge            button             │
│  card           checkbox   combobox   command       command_dialog   dialog             │
│  dropdown_menu  form       input      label         navigation_menu  popover            │
│  progress       select     separator  sheet         table            tabs               │
│  textarea       toast                                                                   │
│                                                                                         │
╰───────────────────────────────── Total: 26 components ─

Add a component:

uvx shadcn_django add button
This will add the button component and any of its dependencies to your templates/cotton directory.

Using Components in Django Templates
After adding components, you can use them in your Django templates:

<div>
  <c-button variant="outline">Cancel</c-button>
  <c-button variant="default">Submit</c-button>
</div>
Customization
When you use the CLI to add components, they are copied into your project folder. You own the components and can customize them as you see fit.

All components use Tailwind CSS classes and can also be customized by passing additional classes:

<c-button variant="default" class="w-full mt-4" />