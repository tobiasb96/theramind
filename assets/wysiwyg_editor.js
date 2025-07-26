import { Editor } from 'https://esm.sh/@tiptap/core@2.6.6';
import StarterKit from 'https://esm.sh/@tiptap/starter-kit@2.6.6';
import Underline from 'https://esm.sh/@tiptap/extension-underline@2.6.6';

window.initWysiwygEditor = function(editorId, content, placeholder = 'Text eingeben...') {
  const editorElement = document.getElementById(editorId);
  const hiddenInput = document.getElementById(editorId + '-input');

  if (editorElement && !editorElement.hasAttribute('data-editor-initialized')) {
    editorElement.setAttribute('data-editor-initialized', 'true');

    // Initialize TipTap editor
    const editor = new Editor({
      element: editorElement,
      extensions: [
        StarterKit,
        Underline,
      ],
      content: content || `<p>${placeholder}</p>`,
      editorProps: {
        attributes: {
          class: 'format format-sm focus:outline-none format-blue max-w-none',
        },
      },
      onUpdate: ({editor}) => {
        // Update hidden input with current content
        hiddenInput.value = editor.getHTML();
      },
    });

    // Toolbar button event listeners with proper event handling
    document.getElementById('toggleBoldButton-' + editorId)?.addEventListener('click', (e) => {
      e.preventDefault();
      editor.chain().focus().toggleBold().run();
    });

    document.getElementById('toggleItalicButton-' + editorId)?.addEventListener('click', (e) => {
      e.preventDefault();
      editor.chain().focus().toggleItalic().run();
    });

    document.getElementById('toggleUnderlineButton-' + editorId)?.addEventListener('click', (e) => {
      e.preventDefault();
      editor.chain().focus().toggleUnderline().run();
    });

    document.getElementById('toggleListButton-' + editorId)?.addEventListener('click', (e) => {
      e.preventDefault();
      editor.chain().focus().toggleBulletList().run();
    });

    document.getElementById('toggleOrderedListButton-' + editorId)?.addEventListener('click', (e) => {
      e.preventDefault();
      editor.chain().focus().toggleOrderedList().run();
    });

    document.getElementById('toggleParagraphButton-' + editorId)?.addEventListener('click', (e) => {
      e.preventDefault();
      editor.chain().focus().setParagraph().run();
      // Hide dropdown using Flowbite instance
      const typographyDropdown = window.FlowbiteInstances?.getInstance('Dropdown', 'typographyDropdown-' + editorId);
      if (typographyDropdown) {
        typographyDropdown.hide();
      }
    });

    // Heading buttons
    document.querySelectorAll('.heading-button-' + editorId).forEach(button => {
      button.addEventListener('click', (e) => {
        e.preventDefault();
        const level = parseInt(button.getAttribute('data-heading-level'));
        editor.chain().focus().toggleHeading({level}).run();
        // Hide dropdown using Flowbite instance
        const typographyDropdown = window.FlowbiteInstances?.getInstance('Dropdown', 'typographyDropdown-' + editorId);
        if (typographyDropdown) {
          typographyDropdown.hide();
        }
      });
    });

    // Initialize hidden input with current content
    hiddenInput.value = editor.getHTML();
  }
}; 